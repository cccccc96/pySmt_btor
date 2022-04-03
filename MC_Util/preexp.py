from pysmt.shortcuts import *
from btor_parser import btor2parser
import PySmtUtil
import vcd


def next_var(v):
    """Returns the 'next' of the given variable"""
    return Symbol("next(%s)" % v.symbol_name(), v.symbol_type())


def at_time(v, t):
    """Builds an SMT variable representing v at time t"""
    return Symbol("%s@%d" % (v.symbol_name(), t), v.symbol_type())


class TransitionSystem(object):
    """Trivial representation of a Transition System."""

    def __init__(self, variables, init, trans, update):
        self.variables = variables
        self.init = init
        self.trans = trans
        self.update = update
        self.next_map = dict()
        for v in self.variables:
            self.next_map[v] = next_var(v)

    @classmethod
    def buildFrom(cls, ts: PySmtUtil.TransitionSystem, constraints, update):
        constraint = And(map(lambda x: x.Equals(BV(1, 1)), constraints))
        init = And(constraint, ts.init)
        trans = And(constraint, ts.trans)
        return cls(ts.variables, init, trans, update)

    @classmethod
    def buildFromBtor(cls, file: str):
        prot = btor2parser.parse_file(file)
        old_ts, constraints, bads = prot.toTS_PySmtFormat()
        update = prot.get_update()
        return cls.buildFrom(old_ts, constraints, update), bads


class KInduction:
    def __init__(self, system, prop):
        self.system = system
        self.prop = prop
        self.strength = prop

    def get_subs(self, i):
        """Builds a map from x to x@i and from x' to x@(i+1), for all x in system."""
        subs_i = {}
        for v in self.system.variables:
            subs_i[v] = at_time(v, i)
            subs_i[next_var(v)] = at_time(v, i + 1)
        return subs_i

    def get_unrolling(self, k):
        """Unrolling of the transition relation from 0 to k:

        E.g. T(0,1) & T(1,2) & ... & T(k-1,k)
        """
        res = []
        for i in range(k + 1):
            subs_i = self.get_subs(i)
            res.append(self.system.trans.substitute(subs_i))
        return And(res)

    def get_simple_path(self, k):
        """Simple path constraint for k-induction:
        each time encodes a different state
        """
        res = []
        for i in range(k + 1):
            subs_i = self.get_subs(i)
            for j in range(i + 1, k + 1):
                state = []
                subs_j = self.get_subs(j)
                for v in self.system.variables:
                    v_i = v.substitute(subs_i)
                    v_j = v.substitute(subs_j)
                    state.append(Not(EqualsOrIff(v_i, v_j)))
                res.append(Or(state))
        return And(res)

    def get_k_hypothesis(self, k):
        """Hypothesis for k-induction: each state up to k-1 fulfills the property"""
        res = []
        for i in range(k):
            subs_i = self.get_subs(i)
            res.append(self.prop.substitute(subs_i))
        return And(res)

    def get_bmc(self, k):
        """Returns the BMC encoding at step k"""
        init_0 = self.system.init.substitute(self.get_subs(0))
        prop_k = self.prop.substitute(self.get_subs(k))
        return And(self.get_unrolling(k), init_0, Not(prop_k))

    def get_k_induction(self, k):
        """Returns the K-Induction encoding at step K"""
        subs_k = self.get_subs(k)
        prop_k = self.prop.substitute(subs_k)
        return And(self.get_unrolling(k),
                   self.get_k_hypothesis(k),
                   self.get_simple_path(k),
                   Not(prop_k))

    def check_property(self):
        """Interleaves BMC and K-Ind to verify the property."""
        print("Checking property %s..." % self.prop)
        for b in range(100):
            f = self.get_bmc(b)
            print("   [BMC]    Checking bound %d..." % (b + 1))
            if is_sat(f):
                print("--> Bug found at step %d" % (b + 1))
                return

            f = self.get_k_induction(b)
            print("   [K-IND]  Checking bound %d..." % (b + 1))
            if is_unsat(f):
                print("--> The system is safe!")
                return
            else:
                print("   [STRONG] Strengthen the property.")
                self.strength = self.strength.substitute(self.system.update)
                self.prop = And(self.strength, self.prop)


def counter(bit_count):
    """Counter example with n bits and reset signal."""

    # Example Counter System (SMV-like syntax)
    #
    # VAR bits: word[bit_count];
    #     reset: boolean;
    #
    # INIT: bits = 0 & reset = FALSE;
    #
    # TRANS: next(bits) = bits + 1
    # TRANS: next(bits = 0) <-> next(reset)

    from pysmt.typing import BVType
    bits = Symbol("bits", BVType(bit_count))
    nbits = next_var(bits)
    reset = Symbol("r", BOOL)
    variables = [bits, reset]

    init = bits.Equals(0) & Not(reset)

    trans = nbits.Equals(bits + 1) & (nbits.Equals(0)).Iff(bits.Equals(10) | reset)

    update = dict()
    update[bits] = Ite(bits.Equals(10) | reset, BV(1, 8), bits + 1)

    # A true invariant property: (reset -> bits = 0)
    true_prop = BVULT(bits, BV(20, 8))

    # A false invariant property: (bits != 2**bit_count-1)
    false_prop = BVULT(bits, BV(8, 8))

    return TransitionSystem(variables, init, trans, update), [true_prop, false_prop]


def testCounter():
    ts, props = counter(8)
    print(ts.update)
    ind = KInduction(ts, props[0])
    ind.check_property()
    print(props[0])
    inv = InvSearch(ts, props[0])
    inv.run_with_preexp()


class InvSearch:
    def __init__(self, system: TransitionSystem, prop):
        self.system = system
        self.prop = prop
        self.invs = [prop]
        self.idx = 0
        self.slv = Solver()
        self.next_map = self.system.next_map
        self.preprop = prop

    def get_model(self):
        res = TRUE()
        for v in self.system.variables:
            res = And(res, EqualsOrIff(v, self.slv.get_model()[v]))
        return res

    def run(self):
        self.slv.add_assertion(self.prop)
        self.slv.add_assertion(self.system.trans)
        while self.idx < len(self.invs):
            if self.slv.is_sat(Not(substitute(self.invs[self.idx], self.next_map))):
                print(self.get_model())
                model = self.get_model()
                if self.slv.is_sat(And(model, self.system.init)):
                    print("sat.")
                    return False
                self.invs.append(Not(model))
                self.slv.add_assertion(self.invs[-1])
            else:
                self.idx += 1
        print("unsat.\ninv: ")
        print(And(self.invs))
        return True

    def run_with_preexp(self):
        self.slv.add_assertion(self.prop)
        self.slv.add_assertion(self.system.trans)
        while self.idx < len(self.invs):
            if self.slv.is_sat(Not(substitute(self.invs[self.idx], self.next_map))):
                self.preprop = simplify(substitute(self.preprop, self.system.update))
                print("add:", end=" ")
                print(self.preprop)
                if self.slv.is_sat(And(Not(self.preprop), self.system.init)):
                    print("sat.")
                    return False
                self.invs.append(self.preprop)
                self.slv.add_assertion(self.invs[-1])
            else:
                self.idx += 1
        print("unsat.\ninv: ")
        print(And(self.invs))
        return True


def vcdTry():
    file = open("counter.vcd", "w")
    writer = vcd.VCDWriter(file)
    reset = writer.register_var('counter', 'reset', 'wire', 1, init=0)
    counter_var = writer.register_var('counter', 'x', 'reg', size=8, init=0)
    for i in range(0, 8):
        writer.change(reset, i, ~reset.value)
        writer.change(counter_var, i, counter_var.value + 1)
    writer.close()
    file.close()


if __name__ == '__main__':
    ts, bads = TransitionSystem.buildFromBtor("../case/memory_assert.btor2")
    # inv = InvSearch(ts, bads[0].Equals(BV(0, 1)))
    # inv.run()
    ind = KInduction(ts, bads[0].Equals(BV(0, 1)))
    ind.check_property()
