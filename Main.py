import z3

from btor2parser import *
from pysmt.shortcuts import simplify
from bmc import *

def test_preExp():
    prot = parse_file("case/memory.btor2")
    bad = prot.prop_map[122] # bad 节点
    stm_map = {}
    for next in prot.next_map.values():
        stm_map[next.cur.id] = next.pre
    print("原始bad性质： "+str(bad.nExp))
    print("调用preexp后性质:  "+str(bad.nExp.preExp(prot.sort_map,stm_map)))

def test_toTS_PySmtFormat():
    prot = parse_file("case/memory_wrong.btor2")
    # for i in range(190, 300):
    #     print(i)
    #     if i in prot.exp_map:
    #         print(str(prot.exp_map[i]))
    trans , prop = prot.toTS_PySmtFormat()

def test_bmc():
    prot = parse_file("case/memory_wrong.btor2")
    trans , prop = prot.toTS_PySmtFormat()
    bmc = BMC(trans)
    bmc.run_bmc(prop[5],3)

if __name__ == "__main__":
    # test_toTS_PySmtFormat()
    test_toTS_PySmtFormat()
    # test_toTS_PySmtFormat()