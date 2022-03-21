from btor2parser import *


def test_preExp():
    prot = parse_file("case/memory.btor2")
    bad = prot.prop_map[122] # bad 节点
    stm_map = {}
    for next in prot.next_map.values():
        stm_map[next.cur.id] = next.pre
    print("原始bad性质： "+str(bad.nExp))
    print("调用preexp后性质:  "+str(bad.nExp.preExp(prot.sort_map,stm_map)))

def test_toTS_PySmtFormat():
    prot = parse_file("case/memory.btor2")
    trans , prop = prot.toTS_PySmtFormat()

if __name__ == "__main__":
    test_preExp()
    # test_toTS_PySmtFormat()