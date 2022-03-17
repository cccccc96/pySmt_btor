from pysmt.shortcuts import *


def next_var(v):
    """Returns the 'next' of the given variable"""
    return Symbol("next(%s)" % v.symbol_name(), v.symbol_type())


def at_time(v, t):
    """Builds an SMT variable representing v at time t"""
    return Symbol("%s@%d" % (v.symbol_name(), t), v.symbol_type())


class TransitionSystem(object):
    """Trivial representation of a Transition System."""

    def __init__(self, variables, init, trans, update: dict):
        self.variables = variables
        self.init = init
        self.trans = trans
        self.update = update


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
            subs_i[next_var(v)] = at_time(v, i+1)
        return subs_i

    def get_unrolling(self, k):
        """Unrolling of the transition relation from 0 to k:

        E.g. T(0,1) & T(1,2) & ... & T(k-1,k)
        """
        res = []
        for i in range(k+1):
            subs_i = self.get_subs(i)
            res.append(self.system.trans.substitute(subs_i))
        return And(res)

    def get_simple_path(self, k):
        """Simple path constraint for k-induction:
        each time encodes a different state
        """
        res = []
        for i in range(k+1):
            subs_i = self.get_subs(i)
            for j in range(i+1, k+1):
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
            print("   [BMC]    Checking bound %d..." % (b+1))
            if is_sat(f):
                print("--> Bug found at step %d" % (b+1))
                return

            f = self.get_k_induction(b)
            print("   [K-IND]  Checking bound %d..." % (b+1))
            if is_unsat(f):
                print("--> The system is safe!")
                return
            else:
                print("--> Strengthen the property.")
                self.strength = self.strength.substitute(self.system.update)
                self.prop = And(self.strength, self.prop)


if __name__ == '__main__':
    pass
