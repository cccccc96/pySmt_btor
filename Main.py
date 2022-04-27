from MC_Util.invbmc import *
from MC_Util.sim import *
from btor_parser import btor2parser
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
    '''
    遍历2^n种情况
    '''
    def _f(ite_exp, innner_ite_list, b_map, res, i):
        global idx
        if i == len(inner_ite_list):
            simplified_ite_exp = ite_exp.simplified_ite({}, b_map)
            print('ite赋值：')
            print(b_map)
            print('简化后的Exp：')
            print(simplified_ite_exp)
            print('简化后的Exp调用toPySmt：')
            print(serialize(simplified_ite_exp.toPySmt(prot.sort_map, {})))
            print('---------------------------')
            # 计算condition，把b_map全部与起来
            condition = None
            for i in b_map:
                if condition is None:
                    if b_map[i] == 0:
                        condition = (UifExp(1,'not',[prot.exp_map[i]],idx))
                        idx -= 1
                    elif b_map[i] == 1:
                        condition = prot.exp_map[i]
                else:
                    if b_map[i] == 0:
                        left = condition
                        right = UifExp(1,'not',[prot.exp_map[i]],idx)
                        idx-=1
                        condition = UifExp(1,'and',[left,right],idx)
                        idx -= 1
                    elif b_map[i] == 1:
                        left = condition
                        right = prot.exp_map[i]
                        condition = UifExp(1, 'and',[left,right],idx)
                        idx-=1
            print(condition)
            x = UifExp(1,'and',[condition,simplified_ite_exp],idx)
            idx-=1
            res.append(x)
            return
        b_map[innner_ite_list[i]] = 0
        _f(ite_exp, innner_ite_list, b_map, res, i + 1)
        b_map[innner_ite_list[i]] = 1
        _f(ite_exp, innner_ite_list, b_map, res, i + 1)

    prot = btor2parser.parse_file("case/memory.btor2")
    prot.toTS_PySmtFormat()
    bad = prot.prop_map[122]  # bad 节点 （constrain的话直接换成对应的id号36/40/。。。）
    stm_map = {}
    for next in prot.nextStatement_map.values():
        key = next.nid
        value = next.exp
        stm_map[key] = value
    ite_exp = bad.nExp.preExp(prot.sort_map, stm_map)
    print("原始bad性质： " + str(bad.nExp))
    print("调用preexp后性质:  " + str(ite_exp))
    print('---------------------------')
    inner_ite_list = []
    ite_exp.get_inner_ites(inner_ite_list,[])
    inner_ite_list.sort()
    if len(inner_ite_list)==0:
        print('没有ite')
        return
    res = []
    _f(ite_exp, inner_ite_list, {}, res, 0)
    print(idx)
    for i in range(len(res)):
        res[i]=res[i].toPySmt(prot.sort_map, {})
    simpliedite = BVOr(res[0],res[1])
    for i in range(2,len(res)):
        simpliedite = BVOr(simpliedite,res[i])
    print(simplify(simpliedite))
    # print('\n！（c1/\e1）应该恒为1 ： ')
    # print(res[0])
    # # print(serialize(simplify(res[1].toPySmt(prot.sort_map, {}))))
    # print('再对 ！（c1/\e1）做preexp')
    # test = res[0].preExp(prot.sort_map, stm_map)
    # print(test)
    #
    # print('\n！（c2/\e2） :')
    # print(res[1])
    # print(serialize((res[1].toPySmt(prot.sort_map, {}))))
    # print('再对 ！（c2/\e2）做preexp')
    # test = res[1].preExp(prot.sort_map, stm_map)
    # print(test)
    # print(serialize((test.toPySmt(prot.sort_map, {}))))

    return res

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
    # test_preExp()
    # test_simplified_ite()
    # test_invbmc()
    # test_sim()
    # test_simplified_ite()
    # test_toTS_PySmtFormat()
    # test_toTS_PySmtFormat()
    test_simplified_ite()

    # test_sim()
    # test_toTS_PySmtFormat()
    # test_sim()
    # solver =Solver('btor')
