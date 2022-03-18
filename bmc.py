

from pysmt.shortcuts import Symbol, Not, And, Ite, BV,BVNot,BVAnd,BVComp,Equals,Array,ArrayType,get_model
from pysmt.shortcuts import is_sat, is_unsat, Solver, TRUE, FALSE
from pysmt.typing import BOOL, BVType

import btor2parser


def next_var(v):
    """Returns the 'next' of the given variable"""
    return Symbol("next(%s)" % v.symbol_name(), v.symbol_type())

def at_time(v, t):
    """Builds an SMT variable representing v at time t"""
    return Symbol("%s@%d" % (v.symbol_name(), t), v.symbol_type())


class TransitionSystem(object):
    # T(a,b,next(a),next(b),...)
    # 0-1时刻 T(a0,b0,a1,b1,..)
    # 1-2时刻 T(a0,b0,a1,b1,..)
    def __init__(self, variables, init, trans):
        self.variables = variables
        self.init = init
        self.trans = trans


class BMC(object):

    def __init__(self, system):
        self.system = system

    def get_subs(self, i):
        # 获取时刻i和时刻i+1的变量，以map的形式存储
        subs_i = {}
        for v in self.system.variables:
            subs_i[v] = at_time(v, i)
            subs_i[next_var(v)] = at_time(v, i+1)
        return subs_i

    def get_paths(self, k):
        # path(0,1) /\ path(1,2) ... /\ path(k-1,k)
        res = []
        for i in range(k+1):
            subs_i = self.get_subs(i)
            res.append(self.system.trans.substitute(subs_i))
        return And(res)

    def get_notProps(self,prop, k):
        # not P(V0) /\ not P(V1) ... /\ not P(Vk)
        res = []
        for i in range(k+1):
            subs_i = self.get_subs(i)
            res.append(Not(prop.substitute(subs_i)))
        return And(res)

    def get_bmc(self, prop, k):
        """init /\ path /\ notP """
        init_0 = self.system.init.substitute(self.get_subs(0))
        path_0_k = self.get_paths(k)
        prop_0_k = self.get_notProps(prop, k)
        return And(path_0_k, init_0, prop_0_k)

    def run_bmc(self, prop, k):
        f = self.get_bmc(prop,k)
        print(get_model(f))
        if is_sat(f):
            print("bug find")
        if is_unsat(f):
            print("safe ")


class Test():

    def run_test(self):
        # x=BV(2,2)
        # y = ArrayType(BVType(2),BVType(2))
        # x=Array(BVType(2),BV(2,4))
        x= Symbol("name1",BVType(1))
        y = Symbol("name2", ArrayType(BVType(1),BVType(2)))
        prot =btor2parser.parse_file("case/counter.btor2")
        transitionSystem,prop = prot.toTS_PySmtFormat()
        bmc = BMC(transitionSystem)
        bmc.run_bmc(prop[1],2)



if __name__ == "__main__":
    Test().run_test()