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

class stateType():
    def __init__(self, sid):
        self.sid = sid

    def __str__(self):
        return "state %d" % (self.sid)

    def __repr__(self):
        return "stateType(%d)" % (self.sid)

    def __eq__(self, other):
        return isinstance(other, stateType) and self.sid == other.sid

class BtorType:
    pass

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
    def __init__(self, len, ele_typ):
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
        self.id = id

    def __str__(self):
        return "nodeId %d" % (self.id)

    def __repr__(self):
        return "nodeId %d" % (self.id)

    def __eq__(self, other):
        return isinstance(other, nodeId) and self.id == other.id


class sortType:
    pass


class BvSort(sortType):
    def __init__(self, sid, bvt):
        self.sid = sid
        self.bvt = bvt

    def __str__(self):
        return "BvSort %s %s" % (str(self.sid), str(self.bvt))

    def __repr__(self):
        return "BvSort %s %s" % (str(self.sid), str(self.bvt))

    def __eq__(self, other):
        return isinstance(other, BvSort) and self.sid == other.sid and self.bvt == other.bvt


class ArraySort(sortType):
    def __init__(self, sid, arrt):
        self.sid = sid
        self.arrt = arrt

    def __str__(self):
        return "ArraySort %s %s" % (str(self.sid), str(self.arrt))

    def __repr__(self):
        return "ArraySort %s %s" % (str(self.sid), str(self.arrt))

    def __eq__(self, other):
        return isinstance(other, ArraySort) and self.sid == other.sid and self.arrt == other.arrt


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
    def __init__(self, sort0, bv_or_arr:sortType):
        self.nodeID = nodeId(sort0)
        self.bv_or_arr = bv_or_arr

    def __str__(self):
        return "Sort %s @%s" % (str(self.nodeID), str(self.bv_or_arr))

    def __repr__(self):
        return "Sort %s @%s" % (str(self.nodeID), str(self.bv_or_arr))

    def __eq__(self, other):
        return isinstance(other, SortKind) and self.nid == other.nid and self.nodeID == other.nodeID


class InputKind(nodeType):
    def __init__(self, nid, inpT:inputType):
        self.inpT = inpT
        self.nodeID = nodeId(nid)

    def __str__(self):
        return "Input %s @%s" % (str(self.inpT), str(self.nodeID))

    def __repr__(self):
        return "Input %s @%s" % (str(self.inpT), str(self.nodeID))

    def __eq__(self, other):
        return isinstance(other, InputKind) and self.nodeID == other.nodeID and self.inpT == other.inpT


class StateKind(nodeType):
    def __init__(self, nid, state:stateType):
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
                          IndOpKind) and self.nodeID == other.nodeID and self.sid==other.sid and self.opT == other.opT and self.ns1 == other.ns1 and self.opdNid == other.opdNid


class OpKind(nodeType):
    def __init__(self, nid, opT, sid, opdNids):
        self.nodeID = nodeId(nid)
        self.sid = sid
        self.opT = opT
        self.opdNids = opdNids
        if opT == "ite":
            self.opExp = IteExp(sid,opdNids[0],opdNids[1],opdNids[2])
        else:
            print("完善所有opExp")

    def __str__(self):
        return "OpNode %s(%s): %s @%s" % (str(self.opT), self.opdNids, self.sid, str(self.nodeID))

    def __repr__(self):
        return "OpNode %s(%s): %s @%s" % (str(self.opT), self.opdNids, self.sid, str(self.nodeID))

    def __eq__(self, other):
        return isinstance(other,
                          OpKind) and self.nodeID == other.nodeID and self.sid==other.sid and self.opT == other.opT and self.opdNids == other.opdNids


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
                          NextKind) and self.nid == other.nid and self.sid==other.sid and self.prenid == other.prenid and self.nodeID == other.nodeID


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
                          InitKind and self.nid == other.nid and self.sid==other.sid and self.val == other.val and self.nodeID == other.nodeID)

class PropertyKind(nodeType):
    def __init__(self, line, kind, nid):
        self.nodeID = nodeId(line)
        self.kind=kind
        self.nid=nid

    def __str__(self):
        return "PropertyKind %s @%s" % (str(self.kind), str(self.nid))

    def __repr__(self):
        return "PropertyKind %s @%s" % (str(self.kind), str(self.nid))

    def __eq__(self, other):
        return isinstance(other, PropertyKind) and self.nid == other.nid and self.kind == other.kind and self.nodeID == other.nodeID


class JusticeKind(nodeType):
    def __init__(self, line, num, *nids):
        self.nodeID = nodeId(line)
        self.nids=nids
        self.num=num

    def __str__(self):
        return "justice %s @%s" % (str(self.num), str(self.nids))

    def __repr__(self):
        return "justice %s @%s" % (str(self.num), str(self.nids))

    def __eq__(self, other):
        return isinstance(other, PropertyKind) and self.nids == other.nids and self.num == other.num and self.nodeID == other.nodeID



class expType:
    pass


class ConstExp(expType):
    def __init__(self, sortId, val, id):
        self.sortId = sortId
        self.val = val
        self.id = id

    def __str__(self):
        return " %s %d %s " % (str(self.sortId), self.val, str(self.id))

    def __repr__(self):
        return "const %s %d %s" % (str(self.sortId), self.val, str(self.id))

    def __eq__(self, other):
        return isinstance(other,
                          ConstExp) and self.sortId == other.sortId and self.id == other.id and self.val == other.val


class VarExp(expType):
    def __init__(self, sortId, id):
        self.sortId = sortId
        self.id = id

    def __str__(self):
        return " %s   %s " % (str(self.sortId), str(self.id))

    def __repr__(self):
        return "Var %s   %s" % (repr(self.sortId), repr(self.id))

    def __eq__(self, other):
        return isinstance(other, VarExp) and self.sortId == other.sortId and self.id == other.id


class InputExp(expType):
    def __init__(self, sortId, id):
        self.sortId = sortId
        self.id = id

    def __str__(self):
        return "%s   %s " % (str(self.sortId), str(self.id))

    def __repr__(self):
        return "Input %s   %s" % (repr(self.sortId), repr(self.id))

    def __eq__(self, other):
        return isinstance(other, InputExp) and self.sortId == other.sortId and self.id == other.id


class UifExp(expType):
    def __init__(self, sortId, op, es, id):
        self.sortId = sortId
        self.op = op
        self.es = es
        self.id = id

    def __str__(self):
        return "%s( %s ) :%s   " % (self.op, self.es, str(self.sortId))

    def __repr__(self):
        return "UifExp %s( %s): %s  @Node %s" % (self.op, self.es, str(self.sortId), str(self.id))

    def __eq__(self, other):
        return isinstance(other,
                          UifExp) and self.sortId == other.sortId and self.id == other.id and self.es == other.es and self.op == other.op


class UifIndExp(expType):
    def __init__(self, sortId, op, es, id, opNats):
        self.sortId = sortId
        self.op = op
        self.es = es
        self.id = id

        self.opdNats = opNats

    def __str__(self):
        return "%s( %s,%s ) :%s   " % (self.op, self.es, self.opNats, str(self.sortId))

    def __repr__(self):
        return "UifIdExp %s( %s,%s ) :%s   " % (self.op, self.es, self.opNats, str(self.sortId))

    def __eq__(self, other):
        return isinstance(other,
                          UifIndExp) and self.sortId == other.sortId and self.id == other.id and self.es == other.es and self.op == other.op and self.opdNats == other.opNats


class ReadExp(expType):
    def __init__(self, sortId, mem, adr, id):
        self.sortId = sortId
        self.mem = mem
        self.adr = adr
        self.id = id

    def __str__(self):
        return "%s[%s]  :%s   " % (self.mem, self.adr, str(self.sortId))

    def __repr__(self):
        return "mem %s[ %s]: %s  @Node %s" % (self.mem, self.adr, str(self.sortId), str(self.id))

    def __eq__(self, other):
        return isinstance(other,
                          ReadExp) and self.sortId == other.sortId and self.mem == other.mem and self.id == other.id and self.adr == other.adr


class IteExp(expType):
    def __init__(self, sortId, b, e1, e2):
        self.sortId = sortId
        self.b = b
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
    def __init__(self, sortId, mem, adre, content, id):
        self.sortId = sortId
        self.mem = mem
        self.adre = adre
        self.content = content
        self.id = id

    def __str__(self):
        return "%s[%s]<=%s  :%s   " % (self.mem, self.adre, self.content, str(self.sortId))

    def __repr__(self):
        return "%s[%s]<=%s  :%s" % (self.mem, self.adre, self.content, str(self.sortId))

    def __eq__(self, other):
        return isinstance(other,
                          StoreExp) and self.sortId == other.sortId and self.mem == other.mem and self.adre == other.adre and self.content == other.content and self.id == other.id

class Btor2():
    def __init__(self, nodes):
        self.node_map = {}
        for node in nodes:
            if isinstance(node, nodeType):
                self.node_map[node.nodeID.id] = node
