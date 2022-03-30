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


class Sim(object):

    def __init__(self, system):
        self.system = system
        self.solver = Solver()

    def get_subs(self, i):
        # 获取时刻i和时刻i+1的变量，以map的形式存储
        subs_i = {}
        for v in self.system.variables:
            subs_i[v] = at_time(v, i)
            subs_i[next_var(v)] = at_time(v, i + 1)
        return subs_i

    def get_paths(self, k):
        # path(0,1) /\ path(1,2) ... /\ path(k-1,k)
        res = []
        for i in range(k):
            subs_i = self.get_subs(i)
            res.append(self.system.trans.substitute(subs_i))
        x = And(res)
        return And(res)

    def get_inputs(self, inputs):
        '''

        :param inputs: (Symbol,值,时刻)
        :return:
        '''
        res = []
        for input in inputs:
            res.append(at_time(input[0], input[2]).Equals(input[1]))
        return And(res)

    def get_sim(self, inputs, k):
        """init /\ path /\ notP """
        init_0 = self.system.init.substitute(self.get_subs(0))
        path_0_to_k = self.get_paths(k)
        inputs_0_to_k = self.get_inputs(inputs)
        return And(path_0_to_k, init_0, inputs_0_to_k)

    def run_sim(self, badstates,prot):
        k = 3
        inputs = [
            (Symbol('rst', BVType(1)), BV(0, 1), 0),

            (Symbol('rst', BVType(1)), BV(1, 1), 1),
            (Symbol('in_wr_addr', BVType(4)), BV(1, 4), 1),
            (Symbol('in_wr', BVType(1)), BV(1, 1), 1),
            (Symbol('in_rd', BVType(1)), BV(0, 1), 1),
            (Symbol('in_data', BVType(8)), BV(2, 8), 1),

            (Symbol('rst', BVType(1)), BV(1, 1), 2),
            (Symbol('in_rd_addr', BVType(4)), BV(1, 4), 2),
            (Symbol('in_wr', BVType(1)), BV(0, 1), 2),
            (Symbol('in_rd', BVType(1)), BV(1, 1), 2),
            (Symbol('in_data', BVType(8)), BV(2, 8), 2)
        ]

        f = self.get_sim(inputs, k)
        print(f)
        print('------')
        print(get_model(f))


    def run_sim2(self, badstates,prot):
        k = 3
        # inputs = [
        #     (Symbol('rst', BVType(1)), BV(0, 1), 0),
        #     (Symbol('mem', shortcuts.ArrayType(BVType(1),BVType(1))), Array(BVType(1),BV(1,1)), 0),
        # ]
        #
        # res = []
        # for i in range(75,120):
        #     if not isinstance(prot.exp_map[i], InputExp):
        #         res.append(Symbol("node"+str(prot.exp_map[i].id),prot.sort_map[prot.exp_map[i].sortId].toPySmt(prot.exp_map, prot.sort_map, prot.node_exp_map)).Equals(prot.node_exp_map[i].substitute(self.get_subs(0))))

        # 第一个时刻清零，第二个时刻写，第三个时刻读
        # 那么应该第三个时刻mem更新，第四个时刻out_data更新
        # input结构 (Symbol, 值， 时刻)
        inputs = [
            (Symbol('rst', BVType(1)), BV(0, 1), 0),

            (Symbol('rst', BVType(1)), BV(1, 1), 1),
            (Symbol('in_wr_addr', BVType(1)), BV(0, 1), 1),
            (Symbol('in_wr', BVType(1)), BV(1, 1), 1),
            (Symbol('in_rd', BVType(1)), BV(0, 1), 1),
            (Symbol('in_data', BVType(1)), BV(1, 1), 1),

            (Symbol('rst', BVType(1)), BV(1, 1), 2),
            (Symbol('in_rd_addr', BVType(1)), BV(0, 1), 2),
            (Symbol('in_wr', BVType(1)), BV(0, 1), 2),
            (Symbol('in_rd', BVType(1)), BV(1, 1), 2)
        ]

        f = self.get_sim(inputs, k)
        # mem= Symbol('mem2',shortcuts.ArrayType(BVType(2),BVType(2)))
        # nextmem = Symbol('nextmem2',shortcuts.ArrayType(BVType(2),BVType(2)))
        # f = nextmem.Equals(Store(mem,BV(1,2),BV(2,2)))
        print(f)
        print('------')
        print(get_model(f))
        # self.solver.add_assertion(f)
        # self.solver.solve()
        # print('-----')
        # for i in range(k + 1):
        #     print('time' + str(i))
        #     for var in self.system.variables:
        #         print(
        #             str(at_time(var, i)) + " : " + str(self.solver.get_value(at_time(self.system.variables[0], 0))))

