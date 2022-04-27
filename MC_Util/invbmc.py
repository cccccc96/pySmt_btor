from btor2_parser.btor2parser import *



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


class INVBMC(object):

    def __init__(self, system, update):
        self.system = system
        self.update = update
        self.solver = Solver()

    def get_subs(self, i):
        # 获取时刻i和时刻i+1的变量，以map的形式存储
        subs_i = {}
        for v in self.system.variables:
            subs_i[v] = at_time(v, i)
            subs_i[next_var(v)] = at_time(v, i+1)
        return subs_i

    def get_preexp(self,f, k):
        map = {}
        for key in self.update:
            map[key.substitute(self.get_subs(k))]= self.update[key].substitute(self.get_subs(k-1))
        return f.substitute(map)

    def get_paths(self, k):
        # path(0,1) /\ path(1,2) ... /\ path(k-1,k)
        res = []
        for i in range(k):
            subs_i = self.get_subs(i)
            res.append(self.system.trans.substitute(subs_i))
        x = And(res)
        return And(res)

    def get_inits(self, k):
        res = []
        for i in range(k):
            subs_i = self.get_subs(i)
            res.append(self.system.init.substitute(subs_i))
        return Or(res)

    def getConstrains(self,constrains,k):
        res = []
        for t in range(k+1):
            for constrain in constrains:
                # res.append(constrain)
                res.append(constrain.substitute(self.get_subs(t)).Equals(BV(1,1)))
        return And(res)

    def get_invbmc(self,constrains, badstate, k):
        bad_at_k = badstate.substitute(self.get_subs(k)).Equals(BV(1,1))
        path_0_to_k = self.get_paths(k)
        inits_0_to_k = self.get_inits(k)
        constrains = self.getConstrains(constrains,k)
        return And(path_0_to_k,constrains, bad_at_k, inits_0_to_k)

    def get_invbmc2(self, constrains, badstate, k):
        bad_list = [badstate.substitute(self.get_subs(k))]
        for i in range(k):
            bad_list.append(self.get_preexp(bad_list[i], k-i))
        for i in range(k+1):
            bad_list[i] = bad_list[i].Equals(BV(1,1))
        badstates_k_to_0 = And(bad_list)
        inits_0_to_k = self.get_inits(k)
        constrains_0_to_k = self.getConstrains(constrains, k-1)
        return And(constrains_0_to_k,badstates_k_to_0,inits_0_to_k)


    def run_invbmc2(self, constraints, badstates, k):
        f = self.get_invbmc2(constraints,badstates[0],k)
        print(get_model(f))
        if is_sat(f):
            print("bug find")
        if is_unsat(f):
            print("safe ")


    def run_invbmc(self, constraints, badstates, k):

        f = self.get_invbmc(constraints,badstates[0],k)
        print(get_model(f))
        if is_sat(f):
            print("bug find")
        if is_unsat(f):
            print("safe ")


