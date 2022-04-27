from btor2_parser.btor2parser import *
from btor2_parser.btor2 import *
from pysmt.shortcuts import *
from MC_Util.vcdGen import *
from pysmt.smtlib.script import smtlibscript_from_formula



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
        for i in range(k):
            subs_i = self.get_subs(i)
            res.append(self.system.trans.substitute(subs_i))
        x = And(res)
        return And(res)

    def get_badstates(self,badstate, k):
        # not P(V0) /\ not P(V1) ... /\ not P(Vk)
        res = []
        for i in range(k):
            subs_i = self.get_subs(i)
            res.append(badstate.substitute(subs_i).Equals(BV(1,1)))
        return Or(res)

    def getConstrains(self,constrains,k):
        res = []
        for t in range(k+1):
            for constrain in constrains:
                # res.append(constrain)
                res.append(constrain.substitute(self.get_subs(t)).Equals(BV(1,1)))
        return And(res)



    def get_bmc2(self,constrains, badstate, k):
        """init /\ path /\ notP """
        subs_i = self.get_subs(k-1)
        init_0 = self.system.init.substitute(self.get_subs(0))
        path_0_to_k = self.get_paths(k)
        badstates_0_to_k = badstate.substitute(subs_i).Equals(BV(1, 1))
        constrains = self.getConstrains(constrains,k)
        return And(path_0_to_k,constrains, init_0, badstates_0_to_k)

    def get_bmc(self,constrains, badstate, k):
        """init /\ path /\ notP """
        init_0 = self.system.init.substitute(self.get_subs(0))
        path_0_to_k = self.get_paths(k)
        badstates_0_to_k = self.get_badstates(badstate, k)
        constrains = self.getConstrains(constrains,k)
        return And(path_0_to_k,constrains, init_0, badstates_0_to_k)

    def run_bmc2(self, constraints, badstates, k):
        with Solver() as solver:
            f = self.get_bmc2(constraints,badstates,k)
            # test = to_smtlib(f)
            # print(test)
            if is_sat(f):
                print("bug find")
            if is_unsat(f):
                print("safe ")
            solver.add_assertion(f)
            res = solver.solve()

    def run_bmc(self, constraints, badstates, k):
        with Solver() as solver:
            f = self.get_bmc(constraints,badstates,k)
            # test = to_smtlib(f)
            # print(test)
            if is_sat(f):
                print("bug find")
                return 'sat'
            if is_unsat(f):
                print("safe ")
                return 'unsat'

        # if res:
        #     self.genvcd(k+1)
            # print(at_time(self.system.variables[16],3))
            # mem = at_time(self.system.variables[16],3)
            # test = Select(mem,BV(7,4))
            # print(serialize(self.solver.get_value(test)))

    def get_bmc_smt(self, constraints, badstates, k, btor2filename:str):
        with Solver() as solver:
            smtfilename = btor2filename.replace('.btor','')+'(encodedInBmcWithK20).smt2'
            f = self.get_bmc(constraints,badstates,k)
            script = smtlibscript_from_formula(f)
            script.to_file(smtfilename)
            # file = open(smtfilename,'w')
            # file.write(test)


    def genvcd(self, k ):
        vars = []
        vcdvars = []
        mem = None
        vcdmems = []
        vcd = VcdGen('./', 'memory.vcd')
        for var in self.system.variables:
            if 'node' not in serialize(var) and 'mem' not in serialize(var):
                vars.append(var)
            elif 'mem' in serialize(var):
                mem=var


        memlen = 2**get_type(mem).index_type.width

        for i in range(memlen):
            name = serialize(mem) + '[' + str(i) + ']'
            vcdvar = vcd.addVar(name, VarType.reg, 10, 0)
            vcdmems.append(vcdvar)

        for i in range(len(vars)):
            var = vars[i]
            if i <= 8:
                vcdvar = vcd.addVar(serialize(var), VarType.wire, 10, 0)
                vcdvars.append(vcdvar)
            else:
                vcdvar = vcd.addVar(serialize(var), VarType.reg, 10, 0)
                vcdvars.append(vcdvar)



        for time in range(k):
            print(str(time)+'time')
            for i in range(memlen):
                var_attime = Select(at_time(mem,time), BV(i, get_type(mem).index_type.width))
                value_attime = int(serialize(self.solver.get_value(BVToNatural(self.solver.get_value(var_attime)))))

                a=vcdmems[i]
                b = time
                c = value_attime
                print(value_attime)
                vcd.change(vcdmems[i], time, value_attime)
            for i in range(len(vars)):
                var = vars[i]
                vcdvar = vcdvars[i]
                var_attime = at_time(var, time)
                value_attime =  int(serialize(self.solver.get_value(BVToNatural(self.solver.get_value(var_attime)))))
                vcd.change(vcdvar, time, value_attime)





    def get_ste_bmc(self,ant, cons, k):
        init_0 = self.system.init.substitute(self.get_subs(0))
        path_0_to_k = self.get_paths(k)
        return And(path_0_to_k, init_0, ant, Not(cons))

    def run_ste_bmc(self, ant, cons, k):
        f = self.get_ste_bmc(ant, cons, k)
        print(get_model(f))
        self.solver.add_assertion(f)
        res = self.solver.solve()
        if res:
            self.genvcd(k+1)




        if is_sat(f):
            print("bug find")
        if is_unsat(f):
            print("safe ")

