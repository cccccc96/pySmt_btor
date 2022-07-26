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
        self.state_set = set()


class GSTE(object):

    def __init__(self, system, trajAssertion:TrajAssertions,states):
        self.system = system
        self.trajAssertion = trajAssertion
        self.states = states

    def get_subs(self, i):
        # 获取时刻i和时刻i+1的变量，以map的形式存储
        subs_i = {}
        for v in self.system.variables:
            subs_i[v] = at_time(v, i)
            subs_i[next_var(v)] = at_time(v, i+1)
        return subs_i

    def get_variables_at_time_i(self,i):
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

    def printAllSmt(self,formula, keys):
        with Solver() as solver:
            solver.add_assertion(formula)
            while solver.solve():
                partial_model = [EqualsOrIff(k, solver.get_value(k)) for k in keys]
                # print(partial_model)
                solver.add_assertion(Not(And(partial_model)))


    def run_gste(self):
        f = None
        visted = set()
        edge_queue = []
        edgeList_from_0 = self.trajAssertion.getFromT(0)
        init_0 = self.system.init.substitute(self.get_subs(0))
        for edge in edgeList_from_0:
            edge_queue.append((edge,1,init_0))
        while len(edge_queue) != 0:
            (edge,i,ant_) = edge_queue.pop()
            visted.add(edge)
            source = edge[0]
            sink = edge[1]
            # path
            unroll = self.get_paths(i)
            # ant
            ant_source_sink = self.trajAssertion.getAntFromTo(source,sink)
            ant_source_sink_cur = ant_source_sink.substitute(self.get_subs(i-1))
            ant_ = ant_ & ant_source_sink_cur
            # cons
            cons = self.trajAssertion.getConsFromTo(source,sink)
            not_cons_cur = Not(cons).substitute(self.get_subs(i))
            f = And(unroll,ant_,not_cons_cur)
            if is_sat(And(unroll,ant_,not_cons_cur)):
                return False
            edgeList_from_source = self.trajAssertion.getFromT(sink)

            keys = self.get_variables_at_time_i(i)
            self.printAllSmt(And(unroll,ant_),keys)

            for edge in edgeList_from_source:
                if edge not in visted:
                    edge_queue.append((edge,i+1,ant_))
        return True




def memoryTrajAssertion():
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
            EqualsOrIff(in_wr_addr, Za),
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
    btor = btor2parser.parse_file("../case/memory22.btor2")
    trans, constraints, badstates = btor.toTS_PySmtFormat()
    trajAssertion = memoryTrajAssertion()
    gste = GSTE(trans,trajAssertion,btor.get_VarExps_in_SymbolList())
    print(gste.run_gste())




testGSTEMC()
