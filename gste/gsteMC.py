from pysmt.shortcuts import *
from trajFormula import *
from btor2_parser import btor2parser
from queue import Queue
from pysmt.oracles import get_logic


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


class GSTE(object):

    def __init__(self, system, trajAssertion: TrajAssertions, states):
        self.system = system
        self.trajAssertion = trajAssertion
        self.states = states
        self.stateSets = {}

    def get_subs(self, i):
        # 获取时刻i和时刻i+1的变量，以map的形式存储
        subs_i = {}
        for v in self.system.variables:
            subs_i[v] = at_time(v, i)
            subs_i[next_var(v)] = at_time(v, i + 1)
        return subs_i

    def get_variables_at_time_i(self, i):
        res = []
        for v in self.states:
            res.append(at_time(v, i))
        return res

    def get_paths(self, k):
        # path(0,1) /\ path(1,2) ... /\ path(k-1,k)
        res = []
        for i in range(k):
            subs_i = self.get_subs(i)
            res.append(self.system.trans.substitute(subs_i))
        x = And(res)
        return And(res)

    def is_new(self, stateSet, edge):
        def eq(state1, state2):
            for i in range(len(state1)):
                if not is_sat(EqualsOrIff(state1[i], state2[i])):
                    return False
            return True

        # 判断stateSet是不是有新增
        # 如果有返回True，如果没有返回False
        if edge not in self.stateSets:
            return True
        stateSet_ = self.stateSets[edge]

        for item1 in stateSet:
            flag = False
            for item2 in stateSet_:
                if eq(item1, item2):
                    flag = True
            if not flag:
                # print('--notin--',item1)
                return True
            # if item not in stateSet_:
            #     return True
        return False

    def compute_and_add_stateSet(self, formula, keys, edge):
        # 计算formula对应的状态集(stateSet)
        # 如果stateSet是新增的，加入stateSets表并返回True
        # 如果stateSet是之前已有的，返回False，
        with Solver() as solver:
            stateSet = []
            solver.add_assertion(formula)
            while solver.solve():
                partial_model = [EqualsOrIff(k, solver.get_value(k)) for k in keys]
                print(partial_model)
                stateSet.append([solver.get_value(k) for k in keys])
                solver.add_assertion(Not(And(partial_model)))
            if self.is_new(stateSet, edge):
                self.stateSets[edge] = stateSet
                return True
            else:
                return False

    def run_gste(self):
        f = None
        visted = set()
        edge_queue = []
        edgeList_from_0 = self.trajAssertion.getFromT(0)
        for edge in edgeList_from_0:
            edge_queue.insert(0, (edge, 1, TRUE()))
        while len(edge_queue) != 0:
            print(','.join(str(edge) for (edge, i, ant_) in edge_queue))
            (edge, i, ant_) = edge_queue.pop()
            print(edge)
            print(i)
            source = edge[0]
            sink = edge[1]
            # path
            unroll = self.get_paths(i)
            # ant
            ant_source_sink = self.trajAssertion.getAntFromTo(source, sink)
            ant_source_sink_cur = ant_source_sink.substitute(self.get_subs(i - 1))
            ant_ = ant_ & ant_source_sink_cur
            print(serialize(ant_))
            # cons
            cons = self.trajAssertion.getConsFromTo(source, sink)
            not_cons_cur = Not(cons).substitute(self.get_subs(i))

            if is_sat(And(unroll, ant_, not_cons_cur)):
                return False

            edgeList_from_source = self.trajAssertion.getFromT(sink)
            keys = self.get_variables_at_time_i(i)
            # keys = self.system.variables
            if self.compute_and_add_stateSet(And(unroll, ant_), keys, edge):
                for edge in edgeList_from_source:
                    edge_queue.insert(0, (edge, i + 1, ant_))
        return True


def memory22TrajAssertion():
    trajAssertion = TrajAssertions()
    rst_n = Symbol('rst_n', BVType(1))
    in_wr = Symbol('in_wr', BVType(1))
    in_rd = Symbol('in_rd', BVType(1))
    in_data = Symbol('in_data', BVType(2))
    in_rd_addr = Symbol('in_rd_addr', BVType(2))
    in_wr_addr = Symbol('in_wr_addr', BVType(2))
    out_data = Symbol('out_data', BVType(2))
    half_depth = BV(2, 2)
    Za = Symbol('Za', BVType(2))
    Zd = Symbol('Zd', BVType(2))

    ant_0_1 = EqualsOrIff(rst_n, BV(0, 1))
    trajAssertion.addAnt(TrajForm(ant_0_1, 0, 1))

    ant_1_2 = And(
        EqualsOrIff(rst_n, BV(1, 1)),
        EqualsOrIff(in_wr, BV(1, 1)),
        EqualsOrIff(in_rd, BV(0, 1)),
        EqualsOrIff(in_wr_addr, Za),
        BVULT(in_wr_addr, half_depth),
        EqualsOrIff(in_data, Zd)
    )
    trajAssertion.addAnt(TrajForm(ant_1_2, 1, 2))

    ant_2_2 = And(
        EqualsOrIff(rst_n, BV(1, 1)),
        Or(
            And(EqualsOrIff(in_wr, BV(0, 1)), EqualsOrIff(in_rd, BV(1, 1))),
            Not(EqualsOrIff(in_wr_addr, Za)),
        ),
    )
    trajAssertion.addAnt(TrajForm(ant_2_2, 2, 2))

    ant_2_3 = And(
        EqualsOrIff(rst_n, BV(1, 1)),
        EqualsOrIff(in_wr, BV(0, 1)),
        EqualsOrIff(in_rd, BV(1, 1)),
        EqualsOrIff(in_rd_addr, Za),
    )
    trajAssertion.addAnt(TrajForm(ant_2_3, 2, 3))

    cons_2_3 = EqualsOrIff(out_data, Zd)
    trajAssertion.addCons(TrajForm(cons_2_3, 2, 3))
    return trajAssertion


def memory11TrajAssertion():
    trajAssertion = TrajAssertions()
    rst_n = Symbol('rst_n', BVType(1))
    in_wr = Symbol('in_wr', BVType(1))
    in_rd = Symbol('in_rd', BVType(1))
    in_data = Symbol('in_data', BVType(1))
    in_rd_addr = Symbol('in_rd_addr', BVType(1))
    in_wr_addr = Symbol('in_wr_addr', BVType(1))
    out_data = Symbol('out_data', BVType(1))
    half_depth = BV(1, 1)
    Za = Symbol('Za', BVType(1))
    Zd = Symbol('Zd', BVType(1))

    ant_0_1 = EqualsOrIff(rst_n, BV(0, 1))
    trajAssertion.addAnt(TrajForm(ant_0_1, 0, 1))

    ant_1_2 = And(
        EqualsOrIff(rst_n, BV(1, 1)),
        EqualsOrIff(in_wr, BV(1, 1)),
        EqualsOrIff(in_rd, BV(0, 1)),
        EqualsOrIff(in_wr_addr, Za),
        # BVULT(in_wr_addr, half_depth),
        EqualsOrIff(in_data, Zd)
    )
    trajAssertion.addAnt(TrajForm(ant_1_2, 1, 2))

    ant_2_2 = And(
        EqualsOrIff(rst_n, BV(1, 1)),
        Or(
            And(EqualsOrIff(in_wr, BV(0, 1)), EqualsOrIff(in_rd, BV(1, 1))),
            Not(EqualsOrIff(in_wr_addr, Za)),
        ),
    )
    trajAssertion.addAnt(TrajForm(ant_2_2, 2, 2))

    ant_2_3 = And(
        EqualsOrIff(rst_n, BV(1, 1)),
        EqualsOrIff(in_wr, BV(0, 1)),
        EqualsOrIff(in_rd, BV(1, 1)),
        EqualsOrIff(in_rd_addr, Za),
    )
    trajAssertion.addAnt(TrajForm(ant_2_3, 2, 3))

    cons_2_3 = EqualsOrIff(out_data, Zd)
    trajAssertion.addCons(TrajForm(cons_2_3, 2, 3))
    return trajAssertion


def testGSTEMC():
    btor = btor2parser.parse_file("../case/memory11_simple.btor2")
    trans, constraints, badstates = btor.toTS_PySmtFormat()
    trajAssertion = memory11TrajAssertion()
    gste = GSTE(trans, trajAssertion, btor.get_VarExps_in_SymbolList())
    # gste = GSTE(trans, trajAssertion, trans.variables)
    print(gste.run_gste())


testGSTEMC()
