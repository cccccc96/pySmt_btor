

from pysmt.shortcuts import Symbol, Not, And, Or, EqualsOrIff, Implies, Ite, Int,BV
from pysmt.shortcuts import is_sat, is_unsat, Solver, TRUE, FALSE
from pysmt.typing import BOOL, BVType


def next_var(v):
    """Returns the 'next' of the given variable"""
    return Symbol("next(%s)" % v.symbol_name(), v.symbol_type())

def at_time(v, t):
    """Builds an SMT variable representing v at time t"""
    return Symbol("%s@%d" % (v.symbol_name(), t), v.symbol_type())


class TransitionSystem(object):
    """Trivial representation of a Transition System."""

    def __init__(self, variables, init, trans):
        self.variables = variables
        self.init = init
        self.trans = trans

class Sort():
    pass


class Bitvec(Sort):
    def __init__(self, len):
        self.len = len


class Array(Sort):
    def __init__(self, s1, s2):
        self.s1 = s1
        self.s2 = s2


class Exp():
    pass


class VarExp(Exp):
    def __init__(self, name: str, sort: Sort):
        if isinstance(sort, Bitvec):
            if sort.len==1:
                self.val = Symbol(name, BOOL)
            else:
                self.val = Symbol(name, BVType(sort.len))
        elif isinstance(sort, Array):
            assert "Array 待完善"


class ConstExp(Exp):
    def __init__(self,sort, val):
        if isinstance(sort, Bitvec):
            if sort.len==1 and val ==0:
                self.val = FALSE()
            elif sort.len==1 and val ==1:
                self.val = TRUE()
            elif sort.len!=1:
                self.val = BV(val,sort.len)
        elif isinstance(sort,Array):
            assert "array 待完善"

class NotExp(Exp):
    def __init__(self, subExp):
        self.val= Not(subExp.val)

class IteExp(Exp):
    def __init__(self, iff, left, right):
        self.val = Ite(iff.val, left.val, right.val)

class AndExp(Exp):
    def __init__(self, left, right):
        self.val = And(left.val, right.val)

class AddExp(Exp):
    def __init__(self, left, right):
        self.val = left.val + right.val

class EqExp(Exp):
    def __init__(self, left, right):
        self.val = left.val.Equals(right.val)

class InitExp(Exp):
    def __init__(self, state:VarExp, const:ConstExp):
        # 如果是bitvec就用equals，如果是Bool处理成布尔逻辑的形式(state/!state)
        self.val = state.val.Equals(const.val)

class TransExp(Exp):
    def __init__(self, next: VarExp, cur):
        self.val = next_var(next.val).Equals(cur.val)

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
        """Returns the BMC encoding at step k"""
        init_0 = self.system.init.substitute(self.get_subs(0))
        path_0_k = self.get_paths(k)
        prop_0_k = self.get_notProps(prop, k)
        return And(path_0_k, init_0, prop_0_k)

    def run_bmc(self, prop, k):
        f = self.get_bmc(prop,k)
        print(f)
        if is_sat(f):
            print("bug find")
        if is_unsat(f):
            print("safe ")


class Test():
    # 看一下如果按照btor2格式定义迁移系统要怎么写
    # 根据counter.btor2的格式 定义一下迁移系统
    def counter(self):
        # btor2中的input/state 定义成VarExp
        node2 = VarExp("node2",Bitvec(1))
        node3 = VarExp("node3",Bitvec(1))
        node6 = VarExp("node6",Bitvec(4))
        variables = [node2.val,node3.val,node6.val]

        # btor2中的const 定义成ConstExp
        node5 = ConstExp(Bitvec(4),1)
        node19 = ConstExp(Bitvec(4),15)

        # btor2中的各个操作符号 定义成相对的Exp
        node18 = AddExp(node6,node5)
        node20 = EqExp(node6,node19)
        node21 = IteExp(node20,node5,node18)
        node22 = IteExp(node3,node21,node6)

        # btor2中的init 定义成InitExp
        node7 = InitExp(node6,node5)
        init = node7.val

        # btor2中的next 定义成TransExp
        node23 = TransExp(node6,node22)
        trans = node23.val

        # property
        node8=ConstExp(Bitvec(4),0)
        node9 = EqExp(node6,node8)
        node10 = NotExp(node9)

        return TransitionSystem(variables, init, trans) , node10.val

    def run_test(self):
        transitionSystem,prop =self.counter()
        bmc = BMC(transitionSystem)
        bmc.run_bmc(prop,2)



if __name__ == "__main__":
    Test().run_test()