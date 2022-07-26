from MC_Util.invbmc import *
from MC_Util.sim import *
from btor2_parser import btor2parser
from ste_parser import steparser
from MC_Util.bmc import *
from itebdd.IteBddMgr import *
from pysmt.fnode import FNode
from pysmt.oracles import get_logic

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
    prot = btor2parser.parse_file("case/memory.btor2")
    trans, constraints, badstates = prot.toTS_PySmtFormat()
    update = prot.get_update()
    exp_map = prot.exp_map
    nextStatement_map = prot.nextStatement_map
    for k,v in nextStatement_map.items():
        print("%12s := %s" % (exp_map[v.nid],str(v.exp)))

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

    print('test',prot.exp_map[5])

    print("原始bad性质： " + str(bad.nExp))
    ite_exp = bad.nExp.preExp(prot.sort_map, stm_map)
    print("调用preexp后性质:  " + str(ite_exp))
    print(ite_exp)
    print('---------------------------')
    res1,list = prot.simplifyIte(ite_exp)
    print('第一次化简')
    print(simplify(res1.toPySmt(prot.sort_map, {})))

    print('---------------------------')
    print('调用preexp:')
    pre = list[1].preExp(prot.sort_map, stm_map)
    print('preexp的结果:')
    print(pre)
    print(serialize(simplify(pre.toPySmt(prot.sort_map, {}))))
    print('---------------------------')
    res2,list = prot.simplifyIte(pre)
    print(res2)
    print('test', prot.exp_map[5])
    print('第二次化简')
    print(res2)
    print(serialize(simplify(res2.toPySmt(prot.sort_map, {}))).replace(' ? 1_1 : 0_1',''))

    print('---------------------------')
    print('调用preexp:')
    pre = list[28].preExp(prot.sort_map, stm_map)
    print('preexp的结果:')
    print(serialize(simplify(pre.toPySmt(prot.sort_map, {}))))
    print('---------------------------')
    res3,list = prot.simplifyIte(pre)
    print('第三次化简')
    print(serialize(simplify(res3.toPySmt(prot.sort_map, {}))).replace(' ? 1_1 : 0_1',''))


def test_assert():


    trans, constraints, badstates = prot_btor.toTS_PySmtFormat()
    node_map = prot_btor.get_vars()
    bmc = BMC(trans)

    prot_assert = steparser.parse_file("ste_parser/assert_test")
    ant,cons,k = prot_assert.toPySmt(node_map)
    print(serialize(ant))
    print(cons)
    bmc.run_ste_bmc(ant,cons,k)

def get_f(i):
    prot = btor2parser.parse_file("case/memory.btor2")
    prot.toTS_PySmtFormat()
    bad = prot.prop_map[122]  # bad 节点 （constrain的话直接换成对应的id号36/40/。。。）
    stm_map = {}
    for next in prot.nextStatement_map.values():
        key = next.nid
        value = next.exp
        stm_map[key] = value
    ite_exp = bad.nExp.preExp(prot.sort_map, stm_map)
    res1,list = prot.simplifyIte(ite_exp)

    pre = list[1].preExp(prot.sort_map, stm_map)

    res2,list = prot.simplifyIte(pre)

    pre2 = list[28].preExp(prot.sort_map, stm_map)
    if(i==1):
        return prot,ite_exp
    elif(i==2):
        return prot,pre
    elif(i==3):
        return prot,pre2


def test_ite_bdd2():
    prot = btor2parser.parse_file("case/btor2_BM/ret0024_dir.btor2")
    bm = IteBddMgr(prot)
    bad = prot.prop_map[80].nExp

    f = prot.preExp(bad)
    support=bm.setSupport(f)
    split_ite_bddNode1 = bm.build(f)
    res1 = bm.generateExpListOfAllCondition(split_ite_bddNode1)
    res1_without_zero = bm.generateExpListOfAllConditionWithoutZero(split_ite_bddNode1)
    print('ite-condition 数量：', len(support))
    print(len(res1),res1)
    print(len(res1_without_zero), res1_without_zero)

    f = prot.preExp(bm.generateExpOfAllCondition(split_ite_bddNode1))
    print(f)
    support = bm.setSupport(f)
    split_ite_bddNode2 = bm.build(f)
    print('ite-condition 数量：',len(support))
    res2 = bm.generateExpListOfAllCondition(split_ite_bddNode2)
    res2_without_zero = bm.generateExpListOfAllConditionWithoutZero(split_ite_bddNode2)
    print(len(res2),res2)
    print(len(res2_without_zero),res2_without_zero)

    f = prot.preExp(bm.generateExpOfAllCondition(split_ite_bddNode2))
    print(f)
    support = bm.setSupport(f)
    split_ite_bddNode3 = bm.build(f)
    print('ite-condition 数量：',len(support))
    for i in support:
        print(prot.exp_map[i])
    res3 = bm.generateExpListOfAllCondition(split_ite_bddNode3)
    res3_without_zero = bm.generateExpListOfAllConditionWithoutZero(split_ite_bddNode3)
    print(len(res3),res3)
    print(len(res3_without_zero),res3_without_zero)

def test_ite_bdd():
    # prot = btor2parser.parse_file("case/btor2_BM/ret0024_dir.btor2")
    prot = btor2parser.parse_file("case/memory.btor2")
    bm = IteBddMgr(prot)
    # bad = prot.prop_map[80].nExp
    bad = prot.prop_map[122].nExp
    # bad = prot.prop_map[353].nExp

    print('#1:')
    f = prot.preExp(bad)
    print(f)
    support=bm.setSupport(f)
    split_ite_bddNode1 = bm.build(f)
    res1 = bm.generateExpListOfAllCondition(split_ite_bddNode1)
    res1_without_zero = bm.generateExpListOfAllConditionWithoutZero(split_ite_bddNode1)
    print('ite-condition 数量：', len(support))
    # print(len(res1),res1)
    print('分解',len(res1_without_zero), res1_without_zero)

    print('\n#2:')
    f = prot.preExp(bm.generateExpOfAllCondition(split_ite_bddNode1))
    print(f)
    support = bm.setSupport(f)
    for i in support:
        print(prot.exp_map[i])
    split_ite_bddNode2 = bm.build(f)
    print('ite-condition 数量：',len(support))
    res2 = bm.generateExpListOfAllCondition(split_ite_bddNode2)
    res2_without_zero = bm.generateExpListOfAllConditionWithoutZero(split_ite_bddNode2)
    # print(len(res2),res2)
    print('分解',len(res2_without_zero))
    for item in res2_without_zero:
        print(item)

    print('\n#3:')
    f = prot.preExp(bm.generateExpOfAllCondition(split_ite_bddNode2))
    print(f)
    support = bm.setSupport(f)
    split_ite_bddNode3 = bm.build(f)
    print('ite-condition 数量：',len(support))
    res3 = bm.generateExpListOfAllCondition(split_ite_bddNode3)
    res3_without_zero = bm.generateExpListOfAllConditionWithoutZero(split_ite_bddNode3)
    # print(len(res3),res3)
    print('分解',len(res3_without_zero),res3_without_zero)
    print(bm.generateExpOfAllCondition(split_ite_bddNode3))

    print('\n#4:')
    f = prot.preExp(bm.generateExpOfAllCondition(split_ite_bddNode3))
    # print(f)
    support = bm.setSupport(f)
    print('ite-condition 数量：', len(support))
    split_ite_bddNode4 = bm.build(f)
    print('ite-condition 数量：',len(support))
    res4 = bm.generateExpListOfAllCondition(split_ite_bddNode4)
    res4_without_zero = bm.generateExpListOfAllConditionWithoutZero(split_ite_bddNode4)
    print('分解',len(res4_without_zero))






if __name__ == "__main__":
    # test_simplified_ite()
    test_toTS_PySmtFormat()
    

