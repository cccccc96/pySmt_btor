from enum import Enum
from debug import SIMULATION_KIND, TREE_DISPLAY
from pysmt import shortcuts
from pysmt.shortcuts import *
from pysmt.typing import *
from PySmtUtil import next_var, at_time, TransitionSystem


# def indent(s, num_space, first_line=None):
#     lines = s.split('\n')
#     if first_line is None:
#         return '\n'.join(' ' * num_space + line for line in lines)
#     else:
#         res = ' ' * first_line + lines[0]
#         if len(lines) > 1:
#             res += '\n' + '\n'.join(' ' * num_space + line for line in lines[1:])
#         return res


class BtorType:
    pass


class bvType(BtorType):
    def __init__(self, len):
        self.len = len

    def __str__(self):
        return "bitvec %d" % (self.len)

    def __repr__(self):
        return "bitvecType(%d)" % (self.len)

    def __eq__(self, other):
        return isinstance(other, bvType) and self.len == other.len


class ArrayType(BtorType):
    def __init__(self, ele_typ, idx_typ):
        self.idx_typ = idx_typ
        self.ele_typ = ele_typ

    def __str__(self):
        return "array [%s] of %s" % (str(self.idx_typ), str(self.ele_typ))

    def __repr__(self):
        return "ArrayType(%d, %s)" % (self.idx_typ, repr(self.ele_typ))

    def __eq__(self, other):
        return isinstance(other, ArrayType) and self.idx_typ == other.idx_typ and self.ele_typ == other.ele_typ


class sortId:
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return "sortId %d" % (self.id)

    def __repr__(self):
        return "sortId %d" % (self.len)

    def __eq__(self, other):
        return isinstance(other, sortId) and self.id == other.id


class nodeId:
    def __init__(self, id, name=None):
        self.id = int(id)
        self.name = name
        self.node_kind = "idle"

    def __str__(self):
        return "nodeId %d" % (self.id)

    def __repr__(self):
        return "nodeId %d" % (self.id)

    def __eq__(self, other):
        return isinstance(other, nodeId) and self.id == other.id


class inputEnum(Enum):
    input = 0
    one = 1
    ones = 2
    zero = 3


class inputType:
    pass


class input1Type(inputType):
    def __init__(self, inpEnum, sortId):
        self.inpEnum = inpEnum
        self.sortId = sortId

    def __str__(self):
        return "input %s %s" % (self.inpEnum, str(self.sortId))

    def __repr__(self):
        return "input %s %s" % (self.inpEnum, str(self.sortId))

    def __eq__(self, other):
        return isinstance(other, input1Type) and self.sortId == other.sortId


class constType(inputType):
    def __init__(self, sortId, val):
        self.sortId = sortId
        self.val = val

    def __str__(self):
        return "const-%s" % self.val

    def __repr__(self):
        return "const-%s" % self.val

    def __eq__(self, other):
        return isinstance(other, constType) and self.sortId == other.sortId and self.val == other.val


class constdType(inputType):
    def __init__(self, sortId, val):
        self.sortId = sortId
        self.val = val

    def __str__(self):
        if SIMULATION_KIND:
            return "constd %s %s" % (str(self.sortId), self.val)
        else:
            return "const%s" % self.val

    def __repr__(self):
        if SIMULATION_KIND:
            return "constd %s %s" % (str(self.sortId), self.val)
        else:
            return "const%s" % self.val

    def __eq__(self, other):
        return isinstance(other, constdType) and self.sortId == other.sortId and self.val == other.val


class consthType(inputType):
    def __init__(self, sortId, val):
        self.sortId = sortId
        self.val = val

    def __str__(self):
        return "const %s %s" % (str(self.sortId), self.val)

    def __repr__(self):
        return "const %s %s" % (str(self.sortId), self.val)

    def __eq__(self, other):
        return isinstance(other, consthType) and self.sortId == other.sortId and self.val == other.val


class indOpEnum(Enum):
    SliceOp = 0
    Uext = 1
    Sext = 2


class opEnum(Enum):
    Add = 0
    Sub = 1
    Neg = 2
    Inc = 3
    Dec = 4
    ReadOp = 5
    WriteOp = 6
    IteOp = 7


class nodeType:
    pass


class SortKind(nodeType):
    def __init__(self, sort0, bv_or_arr: BtorType):
        self.nodeID = nodeId(sort0)
        self.bv_or_arr = bv_or_arr

    def __str__(self):
        return "Sort %s @%s" % (str(self.nodeID), str(self.bv_or_arr))

    def __repr__(self):
        return "Sort %s @%s" % (str(self.nodeID), str(self.bv_or_arr))

    def __eq__(self, other):
        return isinstance(other, SortKind) and self.nodeID == other.nodeID

    def toPySmt(self, sort_map):
        if isinstance(self.bv_or_arr, bvType):
            return BVType(self.bv_or_arr.len)
        elif isinstance(self.bv_or_arr, ArrayType):
            ele_typ = BVType(self.bv_or_arr.ele_typ)
            idx_typ = BVType(self.bv_or_arr.idx_typ)
            return shortcuts.ArrayType(ele_typ, idx_typ)


class InputKind(nodeType):
    def __init__(self, nid, inpT: inputType, name=None):
        self.inpT = inpT
        self.nodeID = nodeId(nid)
        self.name = name

    def __str__(self):
        return "Input %s @%s" % (str(self.inpT), str(self.nodeID))

    def __repr__(self):
        return "Input %s @%s" % (str(self.inpT), str(self.nodeID))

    def __eq__(self, other):
        return isinstance(other, InputKind) and self.nodeID == other.nodeID and self.inpT == other.inpT


class StateKind(nodeType):
    def __init__(self, nid, state):
        self.sid = state
        self.nodeID = nodeId(nid)

    def __str__(self):
        return "State %s @%s" % (str(self.sid), str(self.nodeID))

    def __repr__(self):
        return "State %s @%s" % (str(self.sid), str(self.nodeID))

    def __eq__(self, other):
        return isinstance(other, StateKind) and self.nodeID == other.nodeID and self.sid == other.sid


class IndOpKind(nodeType):
    def __init__(self, nid, opT, sid, opdNid, ns1, ns2):
        self.nodeID = nodeId(nid)
        self.sid = sid
        self.opT = opT
        self.opdNid = opdNid
        self.ns1 = ns1
        self.ns2 = ns2

    def __str__(self):
        return "IndOpNode %s(%s): %s @%s" % (str(self.opT), self.opdNid, self.sid, str(self.nodeID))

    def __repr__(self):
        return "IndOpNode %s(%s): %s @%s" % (str(self.opT), self.opdNid, self.sid, str(self.nodeID))

    def __eq__(self, other):
        return isinstance(other,
                          IndOpKind) and self.nodeID == other.nodeID and self.sid == other.sid and self.opT == other.opT and self.ns1 == other.ns1 and self.opdNid == other.opdNid


class OpKind(nodeType):
    def __init__(self, nid, opT, sid, opdNids):
        self.nodeID = nodeId(nid)
        self.sid = sid
        self.opT = opT
        self.opdNids = opdNids

    def __str__(self):
        return "OpNode %s(%s): %s @%s" % (str(self.opT), self.opdNids, self.sid, str(self.nodeID))

    def __repr__(self):
        return "OpNode %s(%s): %s @%s" % (str(self.opT), self.opdNids, self.sid, str(self.nodeID))

    def __eq__(self, other):
        return isinstance(other,
                          OpKind) and self.nodeID == other.nodeID and self.sid == other.sid and self.opT == other.opT and self.opdNids == other.opdNids


class NextKind(nodeType):
    def __init__(self, line, sid, nid, prenid):
        self.nodeID = nodeId(line)
        self.sid = sid
        self.nid = nid
        self.prenid = prenid

    def __str__(self):
        return "line %s: Next %s := %s  " % (self.line, str(self.nid), self.prenid)

    def __repr__(self):
        return "line %s: Next %s := %s  " % (self.line, str(self.nid), self.prenid)

    def __eq__(self, other):
        return isinstance(other,
                          NextKind) and self.nid == other.nid and self.sid == other.sid and self.prenid == other.prenid and self.nodeID == other.nodeID


class InitKind(nodeType):
    def __init__(self, line, sid, nid, val):
        self.nodeID = nodeId(line)
        self.nid = nid
        self.sid = sid
        self.val = val

    def __str__(self):
        return "line %s:init %s := %s  " % (self.line, str(self.nid), self.val)

    def __repr__(self):
        return "line %s:init %s := %s  " % (self.line, str(self.nid), self.val)

    def __eq__(self, other):
        return isinstance(other,
                          InitKind and self.nid == other.nid and self.sid == other.sid and self.val == other.val and self.nodeID == other.nodeID)


class PropertyKind(nodeType):
    def __init__(self, line, kind, nid):
        self.nodeID = nodeId(line)
        self.kind = kind
        self.nid = nid

    def __str__(self):
        return "PropertyKind %s @%s" % (str(self.kind), str(self.nid))

    def __repr__(self):
        return "PropertyKind %s @%s" % (str(self.kind), str(self.nid))

    def __eq__(self, other):
        return isinstance(other,
                          PropertyKind) and self.nid == other.nid and self.kind == other.kind and self.nodeID == other.nodeID


class JusticeKind(nodeType):
    def __init__(self, line, num, *nids):
        self.nodeID = nodeId(line)
        self.nids = nids
        self.num = num

    def __str__(self):
        return "justice %s @%s" % (str(self.num), str(self.nids))

    def __repr__(self):
        return "justice %s @%s" % (str(self.num), str(self.nids))

    def __eq__(self, other):
        return isinstance(other,
                          PropertyKind) and self.nids == other.nids and self.num == other.num and self.nodeID == other.nodeID


class expType:
    def __str__(self):
        return "exptype"


class ConstExp(expType):
    def __init__(self, sortId, val, id):
        self.sortId = sortId
        self.val = val
        self.id = id

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return str(self.val)

    def __eq__(self, other):
        return isinstance(other,
                          ConstExp) and self.sortId == other.sortId and self.id == other.id and self.val == other.val

    def toPySmt(self, sort_map):
        sort = sort_map[self.sortId].bv_or_arr
        if isinstance(sort, bvType):
            val = int(self.val, 2)
            return BV(val, sort.len)
        elif isinstance(sort, ArrayType):
            idx_typ = sort.idx_typ
            val = int(self.val, 2)
            return Array(idx_typ, val)

    def preExp(self, sort_map, stm_map):
        return self


class VarExp(expType):
    def __init__(self, sortId, id, name=None):
        self.sortId = sortId
        self.id = id
        if name is None:
            self.name = "node" + str(id)
        else:
            self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def toPySmt(self, sort_map):
        typename = sort_map[self.sortId].toPySmt(sort_map)
        name = self.name
        return Symbol(name, typename)

    def preExp(self, sort_map, stm_map):
        print("执行替换：  替换  node%d   为   %s" % (self.id,str(stm_map[self.id])))
        return stm_map[self.id]


class InputExp(expType):
    def __init__(self, sortId, id, name=None):
        self.sortId = sortId
        self.id = id
        if name is None:
            self.name = "node" + str(id)
        else:
            self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, InputExp) and self.sortId == other.sortId and self.id == other.id

    def toPySmt(self, sort_map):
        typename = sort_map[self.sortId].toPySmt(sort_map)
        name = self.name
        return Symbol(name, typename)

    def preExp(self, sort_map, stm_map):
        # input不动
        return self


class UifExp(expType):
    def __init__(self, sortId, op, es, id):
        self.sortId = sortId
        self.op = op
        self.es = es
        self.id = id

    def __str__(self):
        return " %s(%s) " % (self.op, ', '.join(str(e) for e in self.es))

    def __repr__(self):
        return " %s(%s) " % (self.op, ', '.join(str(e) for e in self.es))

    def __eq__(self, other):
        return isinstance(other,
                          UifExp) and self.sortId == other.sortId and self.id == other.id and self.es == other.es and self.op == other.op

    def toPySmt(self, sort_map):
        if self.op == "eq":
            left = self.es[0]
            right = self.es[1]
            return BVComp(left.toPySmt(sort_map), right.toPySmt(sort_map))
        elif self.op == "not":
            subExp = self.es[0]
            return BVNot(subExp.toPySmt(sort_map))
        elif self.op == "and":
            left = self.es[0]
            right = self.es[1]
            return BVAnd(left.toPySmt(sort_map), right.toPySmt(sort_map))
        elif self.op == "or":
            left = self.es[0]
            right = self.es[1]
            return BVOr(left.toPySmt(sort_map), right.toPySmt(sort_map))
        elif self.op == "add":
            left = self.es[0]
            right = self.es[1]
            return left.toPySmt(sort_map) + right.toPySmt(sort_map)
        elif self.op == "concat":
            left = self.es[0]
            right = self.es[1]
            return BVConcat(left.toPySmt(sort_map), right.toPySmt(sort_map))
        elif self.op == "redor":
            # BVRor是reduce吗？
            subExp = self.es[0]
            len = sort_map[subExp.sortId].bv_or_arr.len
            test = BVRor(subExp.toPySmt(sort_map), len)
            x = Ite(BVRor(subExp.toPySmt(sort_map), len).Equals(BV(1,len)),BV(1,1),BV(0,1))
            return x
        elif self.op == "ult":
            left = self.es[0]
            right = self.es[1]
            return Ite(BVULT(left.toPySmt(sort_map), right.toPySmt(sort_map)),BV(1,1),BV(0,1))
        else:
            assert "not support"

    def preExp(self, sort_map, stm_map):
        es = []
        for e in self.es:
            es.append(e.preExp(sort_map, stm_map))
        return UifExp(self.sortId, self.op, es, self.id)


class UifIndExp(expType):
    def __init__(self, sortId, op, es, id, opNats):
        self.sortId = sortId
        self.op = op
        self.es = es
        self.id = id
        self.opdNats = opNats

    def __str__(self):
        return "%s(%s,%s)" % (self.op, str(self.es), str(self.opdNats))

    def __repr__(self):
        return "%s(%s,%s)" % (self.op, str(self.es), str(self.opdNats))

    def __eq__(self, other):
        return isinstance(other,
                          UifIndExp) and self.sortId == other.sortId and self.id == other.id and self.es == other.es and self.op == other.op and self.opdNats == other.opNats

    def toPySmt(self, sort_map):
        if self.op == "sext":
            left = self.es
            return BVSExt(left.toPySmt(sort_map), self.opdNats[0])
        elif self.op == "uext":
            left = self.es
            return BVZExt(left.toPySmt(sort_map), self.opdNats[0])
        elif self.op == "slice":
            left = self.es
            return BVExtract(left.toPySmt(sort_map), self.opdNats[0], self.opdNats[1])
        else:
            assert "known"

    def preExp(self, sort_map, stm_map):
        es = self.es.preExp(sort_map, stm_map)
        return UifExp(self.sortId, es, self.id, self.opdNats)


class ReadExp(expType):
    def __init__(self, sortId, mem, adr, id):
        self.sortId = sortId
        self.mem = mem
        self.adr = adr
        self.id = id

    def __str__(self):
        return "%s[%s]" % (str(self.mem), str(self.adr))

    def __repr__(self):
        return "%s[%s]" % (str(self.mem), str(self.adr))

    def __eq__(self, other):
        return isinstance(other,
                          ReadExp) and self.sortId == other.sortId and self.mem == other.mem and self.id == other.id and self.adr == other.adr

    def toPySmt(self, sort_map):
        return Select(self.mem.toPySmt(sort_map), self.adr.toPySmt(sort_map))

    def preExp(self, sort_map, stm_map):
        mem = self.mem.preExp(sort_map, stm_map)
        adr = self.adr.preExp(sort_map, stm_map)
        return ReadExp(self.sortId, mem, adr, self.id)


class IteExp(expType):
    def __init__(self, sortId, b, e1, e2, id):
        self.sortId = sortId
        self.b = b
        self.e1 = e1
        self.e2 = e2
        self.id = id

    def __str__(self):
        return "(if %s then %s else %s)" % (str(self.b), str(self.e1), str(self.e2))

    def __repr__(self):
        return "(?%s:%s,%s)" % (str(self.b), str(self.e1), str(self.e2))

    def __eq__(self, other):
        return isinstance(other,
                          IteExp) and self.sortId == other.sortId and self.b == other.b and self.e1 == other.e1 and self.e2 == other.e2 and self.id == other.id

    def toPySmt(self, sort_map):
        sort_of_b = sort_map[self.b.sortId]
        if self.b.toPySmt(sort_map).get_type() is BOOL:
            return Ite(self.b.toPySmt(sort_map), self.e1.toPySmt(sort_map), self.e2.toPySmt(sort_map))
        else:
            return Ite(Equals(self.b.toPySmt(sort_map), BV(1, 1)), self.e1.toPySmt(sort_map), self.e2.toPySmt(sort_map))

    def preExp(self, sort_map, stm_map):
        b = self.b.preExp(sort_map, stm_map)
        e1 = self.e1.preExp(sort_map, stm_map)
        e2 = self.e2.preExp(sort_map, stm_map)
        return IteExp(self.sortId, b, e1, e2, self.id)


class StoreExp(expType):
    def __init__(self, sortId, mem, adre, content, id):
        self.sortId = sortId
        self.mem = mem
        self.adre = adre
        self.content = content
        self.id = id

    def __str__(self):
        return "(%s[%s]<=%s)" % (self.mem, self.adre, self.content)

    def __repr__(self):
        return "(%s[%s]<=%s)" % (self.mem, self.adre, self.content)

    def __eq__(self, other):
        return isinstance(other,
                          StoreExp) and self.sortId == other.sortId and self.mem == other.mem and self.adre == other.adre and self.content == other.content and self.id == other.id

    def toPySmt(self, sort_map):
        return Store(self.mem.toPySmt(sort_map), self.adre.toPySmt(sort_map), self.content.toPySmt(sort_map))

    def preExp(self, sort_map, stm_map):
        mem = self.mem.preExp(sort_map, stm_map)
        adre = self.adre.preExp(sort_map, stm_map)
        content = self.content.preExp(sort_map, stm_map)
        return StoreExp(self.sortId, mem, adre, content, self.id)


# 存储init信息
class Init():
    def __init__(self, sortId, toInit: expType, initVal: expType, id):
        self.id = id
        self.sortId = sortId
        self.toInit = toInit
        self.initVal = initVal

    def __str__(self):
        return "(initial:%s is %s)" % (str(self.toInit), str(self.initVal))

    def toPySmt(self, sort_map):
        return self.toInit.toPySmt(sort_map).Equals(self.initVal.toPySmt(sort_map))


# 存储next信息
class Next():
    def __init__(self, sortId, cur: expType, pre: expType, id):
        self.id = id
        self.sortId = sortId
        self.cur = cur
        self.pre = pre

    def __str__(self):
        return "(next %s : %s)" % (str(self.pre), str(self.cur))
        # return str(self.pre)

    def toPySmt(self, sort_map):
        return next_var(self.cur.toPySmt(sort_map)).Equals(self.pre.toPySmt(sort_map))


class PropertyEnum(Enum):
    bad = 0
    constraint = 1
    fair = 2
    output = 3


# 存储bad/constrain...
class Property():
    def __init__(self, kind: str, nExp: expType, id):
        self.id = id
        if kind == "bad":
            self.kind = PropertyEnum.bad
        elif kind == "constraint":
            self.kind = PropertyEnum.constraint
        elif kind == "fair":
            self.kind = PropertyEnum.fair
        elif kind == "output":
            self.kind = PropertyEnum.output
        self.nExp = nExp

    def __str__(self):
        return "%s:\n%s" % (str(self.kind), str(self.nExp))

    def toPySmt(self, sort_map):
        return self.nExp.toPySmt(sort_map)


# 存储justice
class Justice():
    def __init__(self, id, num: str, nExps):
        self.id = id
        self.num = num
        self.nExps = nExps

    def __str__(self):
        return "%s %s " % (str(self.num), str(self.nExps))


def findNodes(exp: expType):
    nodes = []

    if isinstance(exp, UifExp):
        nodes.append(exp.nExp)

    return nodes


class Btor2():
    def __init__(self, lines):
        self.sort_map = {}
        self.node_map = {}
        self.exp_map = {}
        self.next_map = {}  # next
        self.init_map = {}  # init
        self.prop_map = {}  # 属性
        self.var_map = {}  # 变量input/state

        for line in lines:
            if isinstance(line[0], StateKind):
                if len(line) > 1:
                    line[0].name = line[1]
            if isinstance(line[0], InputKind):
                if len(line) > 1:
                    line[0].name = line[1]
            if isinstance(line[0], PropertyKind) and line[0].kind == "output":
                self.node_map[line[0].nid].name = line[1]
            if isinstance(line[0], nodeType):
                self.node_map[line[0].nodeID.id] = line[0]


        for node in self.node_map.values():

            assert (isinstance(node, nodeType))

            # sortkind bv/arr
            if isinstance(node, SortKind):
                self.sort_map[node.nodeID.id] = node

            # inputkind input/const
            elif isinstance(node, InputKind):
                if isinstance(node.inpT, input1Type):
                    sortId = node.inpT.sortId
                    exp = InputExp(sortId, node.nodeID.id, node.name)
                    self.var_map[exp.id] = exp
                elif isinstance(node.inpT, constType):
                    sortId = node.inpT.sortId
                    val = node.inpT.val
                    exp = ConstExp(sortId, val, node.nodeID.id)
                elif isinstance(node.inpT, constdType):
                    sortId = node.inpT.sortId
                    val = node.inpT.val
                    exp = ConstExp(sortId, val, node.nodeID.id)
                elif isinstance(node.inpT, consthType):
                    sortId = node.inpT.sortId
                    val = node.inpT.val
                    exp = ConstExp(sortId, val, node.nodeID.id)
                self.exp_map[exp.id] = exp


            # statekind
            elif isinstance(node, StateKind):
                sortId = node.sid
                exp = VarExp(sortId, node.nodeID.id, node.name)
                self.exp_map[exp.id] = exp
                self.var_map[exp.id] = exp

            # opidx 一个定义都没有，都是uifindexp
            elif isinstance(node, IndOpKind):
                sortId = node.sid
                op = node.opT
                es = self.exp_map[node.opdNid]
                vals = [node.ns1, node.ns2]
                exp = UifIndExp(sortId, op, es, node.nodeID.id, vals)
                self.exp_map[exp.id] = exp

            # op 只有readexp/iteexp/storeexp， 其他都是uifexp
            elif isinstance(node, OpKind):
                # ite
                if node.opT == "ite":
                    opdNids = node.opdNids
                    sortId = node.sid
                    b = self.exp_map[opdNids[0]]
                    e1 = self.exp_map[opdNids[1]]
                    e2 = self.exp_map[opdNids[2]]
                    exp = IteExp(sortId, b, e1, e2, node.nodeID.id)
                # read
                elif node.opT == "read":
                    opdNids = node.opdNids
                    sortId = node.sid
                    mem = self.exp_map[opdNids[0]]
                    adr = self.exp_map[opdNids[1]]
                    exp = ReadExp(sortId, mem, adr, node.nodeID.id)
                elif node.opT == "write":
                    opdNids = node.opdNids
                    sortId = node.sid
                    mem = self.exp_map[opdNids[0]]
                    adr = self.exp_map[opdNids[1]]
                    content = self.exp_map[opdNids[2]]
                    exp = StoreExp(sortId, mem, adr, content, node.nodeID.id)
                else:
                    sortId = node.sid
                    opdNids = node.opdNids
                    es = [self.exp_map[opdNids[0]]]
                    if opdNids[1] is not None:
                        es.append(self.exp_map[opdNids[1]])
                    if opdNids[2] is not None:
                        es.append(self.exp_map[opdNids[2]])
                    exp = UifExp(sortId, node.opT, es, node.nodeID.id)
                self.exp_map[exp.id] = exp

            elif isinstance(node, NextKind):
                sortId = node.sid
                nid = node.nid
                prenid = node.prenid
                cur = self.exp_map[nid]
                pre = self.exp_map[prenid]
                exp = Next(sortId, cur, pre, node.nodeID.id)
                self.next_map[exp.id] = exp

            elif isinstance(node, InitKind):
                sortId = node.sid
                nid = node.nid
                valid = node.val
                toInit = self.exp_map[nid]
                initVal = self.exp_map[valid]
                exp = Init(sortId, toInit, initVal, node.nodeID.id)
                self.init_map[exp.id] = exp

            elif isinstance(node, PropertyKind):
                kind = node.kind
                nid = node.nid
                nExp = self.exp_map[nid]
                exp = Property(kind, nExp, node.nodeID.id)
                self.prop_map[exp.id] = exp

            elif isinstance(node, JusticeKind):
                exp = Justice(node.num, node.nids, node.nodeID.id)
                self.prop_map[exp.id] = exp

            else:
                print(str(node) + " : unkown!")

    def toTS_PySmtFormat(self):
        vars = []
        inits = []
        nexts = []
        props = []
        for varExp in self.var_map.values():
            vars.append(varExp.toPySmt(self.sort_map))
        for init in self.init_map.values():
            inits.append(init.toPySmt(self.sort_map))
        for next in self.next_map.values():
            nexts.append(next.toPySmt(self.sort_map))
        for prop in self.prop_map.values():
            props.append(prop.toPySmt(self.sort_map))

        return TransitionSystem(vars, And(inits), And(nexts)), props
