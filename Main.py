import z3

from btor2parser import *
from pysmt.shortcuts import simplify
from pysmt import shortcuts
from bmc import *
from sim import *


def test_preExp():
    prot = parse_file("case/memory.btor2")
    bad = prot.prop_map[122]  # bad 节点
    stm_map = {}
    for next in prot.next_map.values():
        stm_map[next.cur.id] = next.pre
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
        # 到达一种情况
        if i == len(inner_ite_list):
            simplified_ite_exp = ite_exp.simplified_ite({}, b_map)
            # exp
            res[0].append(simplified_ite_exp)
            # pysmt公式
            res[1].append((simplified_ite_exp.toPySmt(prot.sort_map, {})))
            return
        b_map[innner_ite_list[i]] = ConstExp(1, '0', -1)
        _f(ite_exp, innner_ite_list, b_map, res, i + 1)
        b_map[innner_ite_list[i]] = ConstExp(1, '1', -1)
        _f(ite_exp, innner_ite_list, b_map, res, i + 1)

    prot = parse_file("case/memory_wrong.btor2")
    # 随便拿一个ite测一下
    ite118 = prot.exp_map[118]
    inner_ite_list = []
    ite118.get_inner_ites(inner_ite_list)
    inner_ite_list.sort()
    res = [[], []]
    _f(ite118, inner_ite_list, {}, res, 0)
    return res


if __name__ == "__main__":
    test_simplified_ite()
    # test_toTS_PySmtFormat()
    # test_toTS_PySmtFormat()
    # test_bmc()
    # test_sim()
    # test_toTS_PySmtFormat()
    # test_sim()
