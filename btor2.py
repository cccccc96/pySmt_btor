from enum import Enum
from sqlite3 import OptimizedUnicode
from tkinter.simpledialog import SimpleDialog


def indent(s, num_space, first_line=None):
    lines = s.split('\n')
    if first_line is None:
        return '\n'.join(' ' * num_space + line for line in lines)
    else:
        res = ' ' * first_line + lines[0]
        if len(lines) > 1:
            res += '\n' + '\n'.join(' ' * num_space + line for line in lines[1:])
        return res


class BtorType:
    pass


class stateType():
    def __init__(self, sid):
        self.sid = sid

    def __str__(self):
        return "state %d" % (self.sid)

    def __repr__(self):
        return "stateType(%d)" % (self.sid)

    def __eq__(self, other):
        return isinstance(other, stateType) and self.sid == other.sid


class bvType(BtorType):
    def __init__(self, len):
        self.len = len

    def __str__(self):
        return "’bitvec %d" % (self.len)

    def __repr__(self):
        return "bitvecType(%d)" % (self.len)

    def __eq__(self, other):
        return isinstance(other, bvType) and self.len == other.len


class ArrayType(BtorType):
    def __init__(self, ele_typ, len):
        self.len = len
        self.ele_typ = ele_typ

    def __str__(self):
        return "array [%d] of %s" % (self.len, self.ele_typ)

    def __repr__(self):
        return "ArrayType(%d, %s)" % (self.len, repr(self.ele_typ))

    def __eq__(self, other):
        return isinstance(other, ArrayType) and self.len == other.len and self.ele_typ == other.ele_typ


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
    def __init__(self, id):
        self.id = int(id)

    def __str__(self):
        return "nodeId %d" % (self.id)

    def __repr__(self):
        return "nodeId %d" % (self.id)

    def __eq__(self, other):
        return isinstance(other, nodeId) and self.id == other.id


# class sortType:
#     pass
#
#
# class BvSort(sortType):
#     def __init__(self, sid, bvt):
#         self.sid = sid
#         self.bvt = bvt
#
#     def __str__(self):
#         return "BvSort %s %s" % (str(self.sid), str(self.bvt))
#
#     def __repr__(self):
#         return "BvSort %s %s" % (str(self.sid), str(self.bvt))
#
#     def __eq__(self, other):
#         return isinstance(other, BvSort) and self.sid == other.sid and self.bvt == other.bvt
#
#
# class ArraySort(sortType):
#     def __init__(self, sid, arrt):
#         self.sid = sid
#         self.arrt = arrt
#
#     def __str__(self):
#         return "ArraySort %s %s" % (str(self.sid), str(self.arrt))
#
#     def __repr__(self):
#         return "ArraySort %s %s" % (str(self.sid), str(self.arrt))
#
#     def __eq__(self, other):
#         return isinstance(other, ArraySort) and self.sid == other.sid and self.arrt == other.arrt
#

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
        return "const %s %s" % (str(self.sortId), self.val)

    def __repr__(self):
        return "const %s %s" % (str(self.sortId), self.val)

    def __eq__(self, other):
        return isinstance(other, constType) and self.sortId == other.sortId and self.val == other.val


class constdType(inputType):
    def __init__(self, sortId, val):
        self.sortId = sortId
        self.val = val

    def __str__(self):
        return "const %s %s" % (str(self.sortId), self.val)

    def __repr__(self):
        return "const %s %s" % (str(self.sortId), self.val)

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
        return isinstance(other, SortKind) and self.nid == other.nid and self.nodeID == other.nodeID


class InputKind(nodeType):
    def __init__(self, nid, inpT: inputType):
        self.inpT = inpT
        self.nodeID = nodeId(nid)

    def __str__(self):
        return "Input %s @%s" % (str(self.inpT), str(self.nodeID))

    def __repr__(self):
        return "Input %s @%s" % (str(self.inpT), str(self.nodeID))

    def __eq__(self, other):
        return isinstance(other, InputKind) and self.nodeID == other.nodeID and self.inpT == other.inpT


class StateKind(nodeType):
    def __init__(self, nid, state: stateType):
        self.state = state
        self.nodeID = nodeId(nid)

    def __str__(self):
        return "State %s @%s" % (str(self.state), str(self.nodeID))

    def __repr__(self):
        return "State %s @%s" % (str(self.state), str(self.nodeID))

    def __eq__(self, other):
        return isinstance(other, StateKind) and self.nodeID == other.nodeID and self.state == other.state


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
        self.nid = nid
        self.sid = sid
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
    pass


class constEnum(Enum):
    const = 0
    constd = 1
    consth = 2


# const sortType val(整形/二进制/十六进制)
class ConstExp(expType):
    # def __init__(self, sortId, val:, id):
    def __init__(self, id, typ: constEnum, sort: expType, val: str):
        self.id = id
        self.sort = sort
        self.val = val
        self.typ = typ

    # def __str__(self):
    #     return " %s %s " % (str(self.sort), self.val)
    #
    # def __repr__(self):
    #     return "const %s %s" % (str(self.sort), self.val)
    #
    # def __eq__(self, other):
    #     return isinstance(other,
    #                       ConstExp) and self.sort == other.sort and self.val == other.val


class BVExp(expType):
    def __init__(self, id, len):
        self.id = id
        self.len = len

    def __str__(self):
        return " %s   %s " % (str(self.id), str(self.len))

    def __repr__(self):
        return "Var %s   %s" % (repr(self.id), repr(self.len))

    def __eq__(self, other):
        return isinstance(other, BVExp) and self.id == other.id and self.len == other.len


class ArrayExp(expType):
    def __init__(self, id, size: expType, len: expType):
        self.id = id
        self.len = len
        self.size = size

    def __str__(self):
        return " %s   %s " % (str(self.id), str(self.len))

    def __repr__(self):
        return "Var %s   %s" % (repr(self.id), repr(self.len))

    def __eq__(self, other):
        return isinstance(other, ArrayExp) and self.id == other.id and self.len == other.len


class StateExp(expType):
    def __init__(self, id, sort: expType):
        self.id = id
        self.sort = sort

    def __str__(self):
        return " %s   %s " % (str(self.id), str(self.sort))

    def __repr__(self):
        return "Var %s   %s" % (repr(self.id), repr(self.sort))

    def __eq__(self, other):
        return isinstance(other, StateExp) and self.id == other.id and self.sort == other.sort


class InputExp(expType):
    def __init__(self, id, typ: inputEnum, sort: expType):
        self.id = id
        self.typ = typ
        self.sort = sort

    def __str__(self):
        return "%s   %s " % (str(self.typ), str(self.id))

    def __repr__(self):
        return "Input %s   %s" % (repr(self.typ), repr(self.id))

    def __eq__(self, other):
        return isinstance(other, InputExp) and self.typ == other.typ and self.id == other.id


# id op sExp(sid) list_nExp(nid*)
class UifExp(expType):
    def __init__(self, id, op: str, sExp: expType, nExp):
        self.id = id
        self.op = op
        self.sExp = sExp
        self.nExp = nExp

    def __str__(self):
        return "%s( %s ) :%s   " % (self.op, str(self.sExp), str(self.id))

    def __repr__(self):
        return "UifExp %s( %s):  @Node %s" % (self.op, str(self.sExp), str(self.id))

    def __eq__(self, other):
        return isinstance(other,
                          UifExp) and self.sortId == other.sortId and self.id == other.id and self.es == other.es and self.op == other.op


# id opidx sExp(sid) nExp(nid) vals(int list)
class UifIndExp(expType):
    def __init__(self, id, opidx, sExp: expType, nExp: expType, vals):
        self.id = id
        self.opidx = opidx
        self.sExp = sExp
        self.nExp = nExp
        self.vals = vals

    def __str__(self):
        return "%s( %s,%s ) :%s   " % (self.opidx, str(self.sExp), (self.nExp), str(self.id))

    def __repr__(self):
        return "UifIdExp %s( %s,%s ) :%s   " % (self.op, self.es, self.opNats, str(self.sortId))

    def __eq__(self, other):
        return isinstance(other,
                          UifIndExp) and self.sortId == other.sortId and self.id == other.id and self.es == other.es and self.op == other.op and self.opdNats == other.opNats


class ReadExp(expType):
    def __init__(self, id, sort: expType, mem: expType, adr: expType):
        self.id = id
        self.mem = mem
        self.adr = adr
        self.sort = sort

    def __str__(self):
        return "%s[%s]  :%s   " % (self.mem, self.adr, str(self.sortId))

    def __repr__(self):
        return "mem %s[ %s]: %s  @Node %s" % (self.mem, self.adr, str(self.sortId), str(self.id))

    def __eq__(self, other):
        return isinstance(other,
                          ReadExp) and self.sortId == other.sortId and self.mem == other.mem and self.id == other.id and self.adr == other.adr


# b?e1:e2
class IteExp(expType):
    def __init__(self, id, sort: expType, b: expType, e1: expType, e2: expType):
        self.id = id
        self.b = b
        self.sort = sort
        self.e1 = e1
        self.e2 = e2

    def __str__(self):
        return "?%s:%s,%s  :%s   " % (self.b, self.e1, self.e2, str(self.sortId))

    def __repr__(self):
        return "IteExp ?%s:%s,%s  :%ss" % (self.b, self.e1, self.e2, str(self.sortId))

    def __eq__(self, other):
        return isinstance(other,
                          IteExp) and self.sortId == other.sortId and self.b == other.b and self.e1 == other.e1 and self.e2 == other.e2 and self.id == other.id


class StoreExp(expType):
    def __init__(self, id, sort: expType, mem: expType, adr: expType, content: expType):
        self.id = id
        self.sort = sort
        self.mem = mem
        self.adr = adr
        self.content = content

    def __str__(self):
        return "%s[%s]<=%s  :%s   " % (self.mem, self.adre, self.content, str(self.sortId))

    def __repr__(self):
        return "%s[%s]<=%s  :%s" % (self.mem, self.adre, self.content, str(self.sortId))

    def __eq__(self, other):
        return isinstance(other,
                          StoreExp) and self.sortId == other.sortId and self.mem == other.mem and self.adre == other.adre and self.content == other.content and self.id == other.id


# toInit 初始化为 initval
class InitExp(expType):
    def __init__(self, id, sort, toInit: expType, initVal: expType):
        self.id = id
        self.sort = sort
        self.toInit = toInit
        self.initVal = initVal

    def __str__(self):
        return "init %s : %s" % (str(self.toInit), str(self.initVal))

    def __repr__(self):
        return "init %s : %s" % (str(self.toInit), str(self.initVal))


# toInit 初始化为 initval
class NextExp(expType):
    def __init__(self, id, sort, cur: expType, pre: expType):
        self.id = id
        self.sort = sort
        self.cur = cur
        self.pre = pre

    def __str__(self):
        return "next %s : %s" % (str(self.cur), str(self.pre))

    def __repr__(self):
        return "next %s : %s" % (str(self.cur), str(self.pre))


class PropertyEnum(Enum):
    bad = 0
    constraint = 1
    fair = 2
    output = 3


class PropertyExp(expType):
    def __init__(self, id, kind: str, nExp: expType):
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
        return "%s %s " % (str(self.kind), str(self.nExp))

    def __repr__(self):
        return "%s %s " % (str(self.kind), str(self.nExp))


class JusticeExp(expType):
    def __init__(self, id, num: str, nExps):
        self.id = id
        self.num = num
        self.nExps = nExps

    def __str__(self):
        return "%s %s " % (str(self.num), str(self.nExps))

    def __repr__(self):
        return "%s %s " % (str(self.num), str(self.nExps))


class Btor2():
    def __init__(self, nodes):
        self.node_map = {}
        self.exp_map = {}
        for node in nodes:
            if isinstance(node, nodeType):
                self.node_map[node.nodeID.id] = node
        for node in self.node_map.values():
            assert (isinstance(node, nodeType))
            # sortkind bv/arr
            if isinstance(node, SortKind):
                if isinstance(node.bv_or_arr, bvType):
                    exp = BVExp(node.nodeID.id, node.bv_or_arr.len)
                elif isinstance(node.bv_or_arr, ArrayType):
                    size = self.exp_map[(node.bv_or_arr.ele_typ)]
                    len = self.exp_map[(node.bv_or_arr.len)]
                    exp = ArrayExp(node.nodeID.id, size, len)
                self.exp_map[exp.id] = exp
            # inputkind input/const
            elif isinstance(node, InputKind):
                if isinstance(node.inpT, input1Type):
                    typ = node.inpT.inpEnum
                    sort = self.exp_map[(node.inpT.sortId)]
                    exp = InputExp(node.nodeID.id, typ, sort)
                elif isinstance(node.inpT, constType):
                    typ = constEnum.const
                    sort = self.exp_map[node.inpT.sortId]
                    val = node.inpT.val
                    exp = ConstExp(node.nodeID.id, typ, sort, val)
                elif isinstance(node.inpT, constdType):
                    typ = constEnum.constd
                    sort = self.exp_map[node.inpT.sortId]
                    val = node.inpT.val
                    exp = ConstExp(node.nodeID.id, typ, sort, val)
                elif isinstance(node.inpT, consthType):
                    typ = constEnum.consth
                    sort = self.exp_map[node.inpT.sortId]
                    val = node.inpT.val
                    exp = ConstExp(node.nodeID.id, typ, sort, val)
                self.exp_map[exp.id] = exp
            # inputkind state
            elif isinstance(node, StateKind):
                sort = self.exp_map[node.state.sid]
                exp = StateExp(node.nodeID.id, sort)
                self.exp_map[exp.id] = exp
            # opidx 一个定义都没有，都是uifindexp
            elif isinstance(node, IndOpKind):
                op = node.opT
                exp1 = self.exp_map[node.sid]
                exp2 = self.exp_map[node.opdNid]
                vals = [node.ns1, node.ns2]
                exp = UifIndExp(node.nodeID.id,op, exp1, exp2, vals)
                self.exp_map[exp.id] = exp
            # op 只有readexp/iteexp/storeexp， 其他都是uifexp
            elif isinstance(node, OpKind):
                # ite
                if node.opT == "ite":
                    sid = node.sid
                    opdNids = node.opdNids
                    sort = self.exp_map[sid]
                    b = self.exp_map[opdNids[0]]
                    e1 = self.exp_map[opdNids[1]]
                    e2 = self.exp_map[opdNids[2]]
                    exp = IteExp(node.nodeID.id, sort, b, e1, e2)
                # read
                elif node.opT == "read":
                    sid = node.sid
                    opdNids = node.opdNids
                    sort = self.exp_map[sid]
                    mem = self.exp_map[opdNids[0]]
                    adr = self.exp_map[opdNids[1]]
                    exp = ReadExp(node.nodeID.id, sort, mem, adr)
                elif node.opT == "write":
                    sid = node.sid
                    opdNids = node.opdNids
                    sort = self.exp_map[sid]
                    mem = self.exp_map[opdNids[0]]
                    adr = self.exp_map[opdNids[1]]
                    content = self.exp_map[opdNids[2]]
                    exp = StoreExp(node.nodeID.id, sort, mem, adr, content)
                else:
                    sid = node.sid
                    opdNids = node.opdNids
                    sort = self.exp_map[sid]
                    n = [self.exp_map[opdNids[0]]]
                    if opdNids[1] is not None:
                        n.append(self.exp_map[opdNids[1]])
                    if opdNids[2] is not None:
                        n.append(self.exp_map[opdNids[2]])
                    exp = UifExp(node.nodeID.id,node.opT , sort, n)
                self.exp_map[exp.id] = exp
            elif isinstance(node, NextKind):
                sid = node.sid
                nid = node.nid
                prenid = node.prenid
                sort = self.exp_map[sid]
                cur = self.exp_map[nid]
                pre = self.exp_map[prenid]
                exp = NextExp(node.nodeID.id, sort, cur, pre)
                self.exp_map[exp.id] = exp
            elif isinstance(node, InitKind):
                sid = node.sid
                nid = node.nid
                valid = node.val
                sort = self.exp_map[sid]
                toInit = self.exp_map[nid]
                initVal = self.exp_map[valid]
                exp = InitExp(node.nodeID.id, sort, toInit, initVal)
                self.exp_map[exp.id] = exp
            elif isinstance(node, PropertyKind):
                kind = node.kind
                nid = node.nid
                nExp = self.exp_map[nid]
                exp = PropertyExp(node.nodeID.id, kind, nExp)
                self.exp_map[exp.id] = exp
            elif isinstance(node, JusticeKind):
                exp = JusticeExp(node.nodeID.id, node.nids)
                self.exp_map[exp.id] = exp
            else:
                print(str(node)+" : unkown!")
