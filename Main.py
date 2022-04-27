from MC_Util.invbmc import *
from MC_Util.sim import *
from btor2_parser import btor2parser
from ste_parser import  steparser
from MC_Util.bmc import *

idx=-10

def test_preExp():
    prot = btor2parser.parse_file("case/memory.btor2")
    prot.toTS_PySmtFormat()

    bad = prot.prop_map[122]  # bad 节点
    stm_map = {}
    for next in prot.nextStatement_map.values():
        key = next.nid
        value = next.exp
        stm_map[key] = value
    print("原始bad性质： " + str(bad.nExp))
    print("调用preexp后性质:  " + str(bad.nExp.preExp(prot.sort_map, stm_map)))


def test_preExp2():
    prot = btor2parser.parse_file("case/memory.btor2")
    prot.toTS_PySmtFormat()
    flag = prot.get_var_from_id(29)
    rst = prot.get_var_from_id(9)
    random_data = prot.get_var_from_id(48)
    out_data = prot.get_var_from_id(10)
    a = UifExp(1,'and',[flag,rst],123)
    inv1 = UifExp(1,'not',[a],124)
    b = UifExp(1,'eq',[random_data,out_data],125)
    c = UifExp(1, 'not', [b], 126)
    inv2 = UifExp(1,'and',[a,c],127)
    bad = (inv2.toPySmt(prot.sort_map, {}))
    trans, constraints, badstates = prot.toTS_PySmtFormat()
    bmc = BMC(trans)
    print(serialize(bad))
    bmc.run_bmc(constraints, bad, 10)
    stm_map = {}
    for next in prot.nextStatement_map.values():
        key = next.nid
        value = next.exp
        stm_map[key] = value
    print("原始inv1性质： " + str(inv1))
    print("调用preexp后性质:  " + str(inv1.preExp(prot.sort_map, stm_map)))
    print('\n')
    print("原始inv2性质： " + str(inv2))
    print("调用preexp后性质:  " + str(inv2.preExp(prot.sort_map, stm_map)))


def test_toTS_PySmtFormat():
    prot = btor2parser.parse_file("case/memory_wrong.btor2")
    trans, constraints, badstates = prot.toTS_PySmtFormat()
    update = prot.get_update()
    return


def test_bmc():
    prot = btor2parser.parse_file("case/memory.btor2")
    prot.toTS_PySmtFormat()
    bad = prot.prop_map[122]  # bad 节点 （constrain的话直接换成对应的id号36/40/。。。）
    stm_map = {}
    for next in prot.nextStatement_map.values():
        key = next.nid
        value = next.exp
        stm_map[key] = value
    ite_exp = bad.nExp.preExp(prot.sort_map, stm_map)
    print(ite_exp)
    bad = (ite_exp.toPySmt(prot.sort_map, {}))


    trans, constraints, badstates = prot.toTS_PySmtFormat()
    bmc = BMC(trans)
    print(serialize(bad))

    bmc.run_bmc(constraints, bad, 6)

def test_invbmc():
    prot = btor2parser.parse_file("case/memory.btor2")
    trans, constraints, badstates = prot.toTS_PySmtFormat()
    bmc = INVBMC(trans, prot.get_update())
    bmc.run_invbmc2(constraints, badstates, 5)


def test_sim():
    prot = btor2parser.parse_file("case/memory_wrong.btor2")
    trans, constraints, badstates = prot.toTS_PySmtFormat()
    sim = Sim(trans)
    sim.run_sim(badstates, prot)
    bmc = BMC(trans)
    bmc.run_bmc(constraints, badstates, 4)


def test_simplified_ite():
    prot = btor2parser.parse_file("case/memory.btor2")
    prot.toTS_PySmtFormat()
    bad = prot.prop_map[122]  # bad 节点 （constrain的话直接换成对应的id号36/40/。。。）
    stm_map = {}
    for next in prot.nextStatement_map.values():
        key = next.nid
        value = next.exp
        stm_map[key] = value
    print("原始bad性质： " + str(bad.nExp))
    ite_exp = bad.nExp.preExp(prot.sort_map, stm_map)
    print("调用preexp后性质:  " + str(ite_exp))
    print('---------------------------')
    res1 = prot.simplifyIte(ite_exp)


def test_assert():


    trans, constraints, badstates = prot_btor.toTS_PySmtFormat()
    node_map = prot_btor.get_vars()
    bmc = BMC(trans)

    prot_assert = steparser.parse_file("ste_parser/assert_test")
    ant,cons,k = prot_assert.toPySmt(node_map)
    print(serialize(ant))
    print(cons)
    bmc.run_ste_bmc(ant,cons,k)



if __name__ == "__main__":
    x = BVComp(BV(1,1),BV(1,1))
    test_simplified_ite()

