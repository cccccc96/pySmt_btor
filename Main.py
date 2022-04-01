import z3

from btor2parser import *
from pysmt.shortcuts import simplify
from pysmt import shortcuts
from bmc import *
from sim import *


def test_preExp():
    prot = parse_file("case/memory.btor2")
    prot.toTS_PySmtFormat()
    bad = prot.prop_map[122]  # bad 节点
    stm_map = {}
    for next in prot.nextStatement_map.values():
        key = next.nid
        value = next.exp
        stm_map[key] = value
    print("原始bad性质： " + str(bad.nExp))
    print("调用preexp后性质:  " + str(bad.nExp.preExp(prot.sort_map, stm_map)))


def test_toTS_PySmtFormat():
    prot = parse_file("case/memory_wrong.btor2")
    trans, constraints, badstates = prot.toTS_PySmtFormat()
    update = prot.get_update()
    return


def test_bmc():
    prot = parse_file("case/memory_wrong.btor2")
    trans, constraints, badstates = prot.toTS_PySmtFormat()
    bmc = BMC(trans)
    bmc.run_bmc(constraints, badstates, 4)


def test_sim():
    prot = parse_file("case/memory_wrong.btor2")
    trans, constraints, badstates = prot.toTS_PySmtFormat()
    sim = Sim(trans)
    sim.run_sim(badstates, prot)


def test_simplified_ite():
    '''
    遍历2^n种情况
    '''
    def _f(ite_exp, innner_ite_list, b_map, res, i):
        if i == len(inner_ite_list):
            simplified_ite_exp = ite_exp.simplified_ite({}, b_map)
            print('ite赋值：')
            print(b_map)
            print('简化后的Exp：')
            print(simplified_ite_exp)
            print('简化后的Exp调用toPySmt：')
            print(serialize(simplified_ite_exp.toPySmt(prot.sort_map, {})))
            print('---------------------------')
            idx = -10
            condition = None
            # for i in b_map:
            #     if condition is None:
            #         if b_map[i].val == '0':
            #             condition = BVNot(prot.exp_map[i].toPySmt(prot.sort_map, {}))
            #         elif b_map[i].val == '1':
            #             condition = prot.exp_map[i].toPySmt(prot.sort_map, {})
            #     else:
            #         if b_map[i].val == '0':
            #             condition = condition & BVNot(prot.exp_map[i].toPySmt(prot.sort_map, {}))
            #         elif b_map[i].val == '1':
            #             condition = condition & prot.exp_map[i].toPySmt(prot.sort_map, {})
            for i in b_map:
                if condition is None:
                    if b_map[i].val == '0':
                        condition = UifExp(1,'not',[prot.exp_map[i]],idx)
                        idx -= 1
                    elif b_map[i].val == '1':
                        condition = prot.exp_map[i]
                else:
                    if b_map[i].val == '0':
                        left = condition
                        right = UifExp(1,'not',[prot.exp_map[i]],idx)
                        idx-=1
                        condition = UifExp(1,'and',[left,right],idx)
                        idx -= 1
                    elif b_map[i].val == '1':
                        left = condition
                        right = prot.exp_map[i]
                        condition = UifExp(1, 'and',[left,right],idx)
                        idx-=1
            x = UifExp(1,'and',[condition,simplified_ite_exp],idx)
            idx-=1
            x = UifExp(1,'not',[x],idx)
            res.append(x)
            return
        b_map[innner_ite_list[i]] = ConstExp(1, '0', -1)
        _f(ite_exp, innner_ite_list, b_map, res, i + 1)
        b_map[innner_ite_list[i]] = ConstExp(1, '1', -1)
        _f(ite_exp, innner_ite_list, b_map, res, i + 1)

    prot = parse_file("case/memory.btor2")
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
    print('\n！（c1/\e1）应该恒为1 ： ')
    print(res[0])
    # print(serialize(simplify(res[1].toPySmt(prot.sort_map, {}))))
    print('再对 ！（c1/\e1）做preexp')
    test = res[0].preExp(prot.sort_map, stm_map)
    print(test)

    print('\n！（c2/\e2） :')
    print(res[1])
    print(serialize(simplify(res[1].toPySmt(prot.sort_map, {}))))
    print('再对 ！（c2/\e2）做preexp')
    test = res[1].preExp(prot.sort_map, stm_map)
    print(test)
    print(serialize(simplify(test.toPySmt(prot.sort_map, {}))))
    return res


if __name__ == "__main__":
    # test_preExp()
    test_simplified_ite()
    # test_simplified_ite()
    # test_toTS_PySmtFormat()
    # test_toTS_PySmtFormat()
    # test_bmc()
    # test_sim()
    # test_toTS_PySmtFormat()
    # test_sim()
