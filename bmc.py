

from pysmt.shortcuts import *
from pysmt.typing import BOOL, BVType
from pysmt.type_checker import SimpleTypeChecker


from btor2parser import *
from btor2 import *


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
        self.solver=Solver()

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
        x = And(res)
        return And(res)

    def get_notProps(self,prop, k):
        # not P(V0) /\ not P(V1) ... /\ not P(Vk)
        res = []
        for i in range(k+1):
            subs_i = self.get_subs(i)
            width =get_type(prop.substitute(subs_i)).width
            res.append(prop.substitute(subs_i).Equals(BV(1,width)))
        return And(res)

    def get_bmc(self, prop, k):
        """init /\ path /\ notP """
        init_0 = self.system.init.substitute(self.get_subs(0))
        path_0_to_k = self.get_paths(k)
        prop_0_to_k = self.get_notProps(prop, k)
        return And(path_0_to_k, init_0, prop_0_to_k)

    def run_bmc(self, prop, k):
        f = self.get_bmc(prop,k)
        print(get_model(f))
        if is_sat(f):
            print("bug find")
        if is_unsat(f):
            print("safe ")


