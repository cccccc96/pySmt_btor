from enum import Enum
from pysmt import shortcuts
from pysmt.shortcuts import *
from pysmt.typing import *
from MC_Util.PySmtUtil import next_var
from btor2_parser.btor2Mgr import Btor2Mgr

debug_flag = False


class SortType:
    pass


class bvType(SortType):
    def __init__(self, len):
        self.len = len

    def __str__(self):
        return "bitvec %d" % (self.len)

    def __repr__(self):
        return "bitvecType(%d)" % (self.len)

    def __eq__(self, other):
        return isinstance(other, bvType) and self.len == other.len


class ArrayType(SortType):
    def __init__(self, idx_typ, ele_typ):
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
        self.name = None

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
        print(val)
        self.sortId = sortId
        self.val = val

    def __str__(self):
        return "const%s" % self.val

    def __repr__(self):
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
    def __init__(self, nid, bv_or_arr: SortType):
        self.nodeID = nodeId(nid)
        self.bv_or_arr = bv_or_arr

    def __str__(self):
        return "Sort %s @%s" % (str(self.nodeID), str(self.bv_or_arr))

    def __repr__(self):
        return "Sort %s @%s" % (str(self.nodeID), str(self.bv_or_arr))

    def __eq__(self, other):
        return isinstance(other, SortKind) and self.nodeID == other.nodeID

    def toPySmt(self, sort_map, visited):
        if isinstance(self.bv_or_arr, bvType):
            visited[self.nodeID.id] = BVType(self.bv_or_arr.len)
            return BVType(self.bv_or_arr.len)
        elif isinstance(self.bv_or_arr, ArrayType):
            ele_typ = sort_map[self.bv_or_arr.ele_typ].toPySmt(sort_map, visited)
            idx_typ = sort_map[self.bv_or_arr.idx_typ].toPySmt(sort_map, visited)
            visited[self.nodeID.id] = shortcuts.ArrayType(idx_typ, ele_typ)
            return shortcuts.ArrayType(idx_typ, ele_typ)

    def node2Exp(self, node_exp_map):
        return node_exp_map


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

    def node2Exp(self, node_exp_map):
        if isinstance(self.inpT, input1Type):
            sortId = self.inpT.sortId
            node_exp_map[self.nodeID.id] = InputExp(sortId, self.nodeID.id, self.name)
        elif isinstance(self.inpT, constType):
            sortId = self.inpT.sortId
            val = self.inpT.val
            node_exp_map[self.nodeID.id] = ConstExp(sortId, val, self.nodeID.id)
        elif isinstance(self.inpT, constdType):
            sortId = self.inpT.sortId
            val = self.inpT.val
            node_exp_map[self.nodeID.id] = ConstExp(sortId, val, self.nodeID.id)
        elif isinstance(self.inpT, consthType):
            sortId = self.inpT.sortId
            val = self.inpT.val
            node_exp_map[self.nodeID.id] = ConstExp(sortId, val, self.nodeID.id)
        return node_exp_map


class StateKind(nodeType):
    def __init__(self, nid, sid):
        self.nodeID = nodeId(nid)
        self.sid = sid
        self.name = None

    def __str__(self):
        return "State %s @%s" % (str(self.sid), str(self.nodeID))

    def __repr__(self):
        return "State %s @%s" % (str(self.sid), str(self.nodeID))

    def __eq__(self, other):
        return isinstance(other, StateKind) and self.nodeID == other.nodeID and self.sid == other.sid

    def node2Exp(self, node_exp_map):
        sortId = self.sid
        node_exp_map[self.nodeID.id] = VarExp(sortId, self.nodeID.id, self.name)
        return node_exp_map


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

    def node2Exp(self, node_exp_map):
        sortId = self.sid
        op = self.opT
        es = node_exp_map[self.opdNid]
        vals = [self.ns1, self.ns2]
        node_exp_map[self.nodeID.id] = UifIndExp(sortId, op, es, self.nodeID.id, vals)
        return node_exp_map


class OpKind(nodeType):
    def __init__(self, nid, opT, sid, opdNids):
        self.nodeID = nodeId(nid)
        self.sid = sid
        self.opT = opT
        self.opdNids = opdNids
        self.flag = None

        # 判定and中的负数情况（beem例子）
        if self.opdNids[1] is not None and self.opdNids[1] < 0:
            self.opdNids = list(self.opdNids)
            self.opdNids[1] = -self.opdNids[1]
            self.flag = 1
        if self.opdNids[0] is not None and self.opdNids[0] < 0:
            self.opdNids = list(self.opdNids)
            self.opdNids[0] = -self.opdNids[0]
            self.flag = 0
        if self.opdNids[2] is not None and self.opdNids[2] < 0:
            self.opdNids = list(self.opdNids)
            self.opdNids[2] = -self.opdNids[2]
            self.flag = 2

    def __str__(self):
        return "OpNode %s(%s): %s @%s" % (str(self.opT), self.opdNids, self.sid, str(self.nodeID))

    def __repr__(self):
        return "OpNode %s(%s): %s @%s" % (str(self.opT), self.opdNids, self.sid, str(self.nodeID))

    def __eq__(self, other):
        return isinstance(other,
                          OpKind) and self.nodeID == other.nodeID and self.sid == other.sid and self.opT == other.opT and self.opdNids == other.opdNids

    def node2Exp(self, node_exp_map):
        if self.opT == "ite":
            test = self.nodeID.id
            opdNids = self.opdNids
            sortId = self.sid
            b = node_exp_map[opdNids[0]]
            e1 = node_exp_map[opdNids[1]]
            e2 = node_exp_map[opdNids[2]]
            node_exp_map[self.nodeID.id] = IteExp(sortId, b, e1, e2, self.nodeID.id, self.flag)
            # print(1)
        # read
        elif self.opT == "read":
            opdNids = self.opdNids
            sortId = self.sid
            mem = node_exp_map[opdNids[0]]
            adr = node_exp_map[opdNids[1]]
            node_exp_map[self.nodeID.id] = ReadExp(sortId, mem, adr, self.nodeID.id)
        elif self.opT == "write":
            opdNids = self.opdNids
            sortId = self.sid
            mem = node_exp_map[opdNids[0]]
            adr = node_exp_map[opdNids[1]]
            content = node_exp_map[opdNids[2]]
            node_exp_map[self.nodeID.id] = StoreExp(sortId, mem, adr, content, self.nodeID.id)
        else:
            sortId = self.sid
            opdNids = self.opdNids
            es = [node_exp_map[opdNids[0]]]
            if opdNids[1] is not None:
                es.append(node_exp_map[opdNids[1]])
            if opdNids[2] is not None:
                es.append(node_exp_map[opdNids[2]])
            node_exp_map[self.nodeID.id] = UifExp(sortId, self.opT, es, self.nodeID.id, self.flag)
        return node_exp_map


class NextKind(nodeType):
    def __init__(self, line, sid, curnid, prenid):
        self.nodeID = nodeId(line)
        self.sid = sid
        self.curnid = curnid
        self.prenid = prenid

    def __str__(self):
        return "line %s: Next %s := %s  " % (self.line, str(self.nid), self.prenid)

    def __repr__(self):
        return "line %s: Next %s := %s  " % (self.line, str(self.nid), self.prenid)

    def __eq__(self, other):
        return isinstance(other,
                          NextKind) and self.nid == other.nid and self.sid == other.sid and self.prenid == other.prenid and self.nodeID == other.nodeID

    def node2Exp(self, node_exp_map):
        return node_exp_map


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

    def node2Exp(self, node_exp_map):
        return node_exp_map


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

    def node2Exp(self, node_exp_map):
        return node_exp_map


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

    def node2Exp(self, node_exp_map):
        return node_exp_map


class expType:
    btor2Mgr = None

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

    def toPySmt(self, sort_map, visited):
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

    def simplified_ite(self, b_map):
        return self

    def get_inner_ites(self, ite_list):
        return


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

    def toPySmt(self, sort_map, visited):
        typename = sort_map[self.sortId].toPySmt(sort_map, visited)
        name = self.name
        return Symbol(name, typename)

    def preExp(self, sort_map, stm_map):
        if debug_flag:
            print("执行替换：  替换  %s   为   %s" % (self.name, str(stm_map[self.id])))
        return stm_map[self.id]

    def simplified_ite(self, b_map):
        return self

    def get_inner_ites(self, ite_list):
        return


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

    def toPySmt(self, sort_map, visited):
        typename = sort_map[self.sortId].toPySmt(sort_map, visited)
        name = self.name
        return Symbol(name, typename)

    def preExp(self, sort_map, stm_map):
        # input不动
        return self

    def simplified_ite(self, b_map):
        return self

    def get_inner_ites(self, ite_list):
        return


class UifExp(expType):
    def __init__(self, sortId, op, es, id, flag=None):
        self.sortId = sortId
        self.op = op
        self.es = es
        self.id = id
        self.flag = flag  # 判定有无负数

    def __str__(self):
        if (self.op == 'and'):
            return '(' + str(self.es[0]) + '&' + str(self.es[1]) + ')'
        if (self.op == 'eq'):
            return '(' + str(self.es[0]) + '=' + str(self.es[1]) + ')'
        if (self.op == 'not'):
            return '!' + str(self.es[0])
        return " %s(%s) " % (self.op, ', '.join(str(e) for e in self.es))

    def __repr__(self):
        return " %s(%s) " % (self.op, ', '.join(str(e) for e in self.es))

    def __eq__(self, other):
        return isinstance(other,
                          UifExp) and self.sortId == other.sortId and self.id == other.id and self.es == other.es and self.op == other.op

    def toPySmt(self, sort_map, visited):
        if self.op == "eq":
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            res = Ite(Equals(left_Smt, right_Smt), BV(1, 1), BV(0, 1))
            # res = BVNot(BVComp(left_Smt,right_Smt))
        elif self.op == "not":
            subExp = self.es[0]
            subExp_Smt = visited[subExp.id] if subExp.id in visited else subExp.toPySmt(sort_map, visited)
            res = BVNot(subExp_Smt)
        elif self.op == "neg":
            subExp = self.es[0]
            subExp_Smt = visited[subExp.id] if subExp.id in visited else subExp.toPySmt(sort_map, visited)
            res = BVNeg(subExp_Smt)
        elif self.op == "and":
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            if self.flag is None:
                res = BVAnd(left_Smt, right_Smt)
            elif self.flag == 1:
                res = BVAnd(left_Smt, BVNot(right_Smt))
            elif self.flag == 0:
                res = BVAnd(BVNot(left_Smt), (right_Smt))
        elif self.op == "or":
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            if self.flag is None:
                res = BVOr(left_Smt, right_Smt)
            elif self.flag == 1:
                res = BVOr(left_Smt, BVNot(right_Smt))
            elif self.flag == 0:
                res = BVOr(BVNot(left_Smt), (right_Smt))
        elif self.op == "add":
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            res = left_Smt + right_Smt
        elif self.op == "concat":
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            res = BVConcat(left_Smt, right_Smt)
        elif self.op == "redor":
            subExp = self.es[0]
            subExp_Smt = visited[subExp.id] if subExp.id in visited else subExp.toPySmt(sort_map, visited)
            len = sort_map[subExp.sortId].bv_or_arr.len
            res = BVExtract(subExp_Smt, 0, 0)
            for i in range(1, len):
                res = BVOr(res, BVExtract(subExp_Smt, i, i))
        elif self.op == "ult" or self.op == 'slt':
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            res = Ite(BVULT(left_Smt, right_Smt), BV(1, 1), BV(0, 1))
        elif self.op == 'xor':
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            res = BVXor(left_Smt, right_Smt)
        elif self.op == 'xnor':
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            res = BVNot(BVXor(left_Smt, right_Smt))
        elif self.op == 'sub':
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            res = BVSub(left_Smt, right_Smt)
        elif self.op == 'mul':
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            res = BVMul(left_Smt, right_Smt)
        elif self.op == 'redand':
            subExp = self.es[0]
            subExp_Smt = visited[subExp.id] if subExp.id in visited else subExp.toPySmt(sort_map, visited)
            len = sort_map[subExp.sortId].bv_or_arr.len
            res = BVExtract(subExp_Smt, 0, 0)
            for i in range(1, len):
                res = BVAnd(res, BVExtract(subExp_Smt, i, i))
        elif self.op == "ulte":
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            res = Ite(Or(BVULT(left_Smt, right_Smt), EqualsOrIff(left_Smt, right_Smt)), BV(1, 1), BV(0, 1))
        elif self.op == "srl":
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            res = BVLShr(left_Smt, right_Smt)
        elif self.op == "sll":
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            res = BVLShl(left_Smt, right_Smt)
        elif self.op == 'ugt':
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            res = Ite(BVUGT(left_Smt, right_Smt), BV(1, 1), BV(0, 1))
        elif self.op == 'ugte':
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            res = Ite(Or(BVUGT(left_Smt, right_Smt), EqualsOrIff(left_Smt, right_Smt)), BV(1, 1), BV(0, 1))
        elif self.op == "neq":
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            res = Ite(Equals(left_Smt, right_Smt), BV(0, 1), BV(1, 1))
        elif self.op == "sra":
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            res = BVAShr(left_Smt, right_Smt)
        elif self.op == "srem":
            left = self.es[0]
            right = self.es[1]
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            right_Smt = visited[right.id] if right.id in visited else right.toPySmt(sort_map, visited)
            res = BVSRem(left_Smt, right_Smt)
        else:
            print(self.op + ' unkonwn')
        visited[self.id] = res
        return res

    def preExp(self, sort_map, stm_map):
        es = []
        for e in self.es:
            es.append(e.preExp(sort_map, stm_map))
        return expType.btor2Mgr.createUifExp(self.sortId, self.op, es)

    def simplified_ite(self, b_map):
        global idx
        es = []
        for e in self.es:
            es.append(e.simplified_ite(b_map))
        return expType.btor2Mgr.createUifExp(self.sortId, self.op, es)

    def get_inner_ites(self, ite_list):
        for e in self.es:
            e.get_inner_ites(ite_list)


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

    def toPySmt(self, sort_map, visited):
        if self.op == "sext":
            left = self.es
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            res = BVSExt(left_Smt, self.opdNats[0])
        elif self.op == "uext":
            left = self.es
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            res = BVZExt(left_Smt, self.opdNats[0])
        elif self.op == "slice":
            left = self.es
            left_Smt = visited[left.id] if left.id in visited else left.toPySmt(sort_map, visited)
            res = BVExtract(left_Smt, self.opdNats[1], self.opdNats[0])
        else:
            assert "known"
        visited[self.id] = res
        return res

    def preExp(self, sort_map, stm_map):
        es = self.es.preExp(sort_map, stm_map)
        return expType.btor2Mgr.createUifIndExp(self.sortId, self.op, es, self.opdNats)

    def simplified_ite(self, b_map):
        global idx
        es = self.es.simplified_ite(b_map)
        return expType.btor2Mgr.createUifIndExp(self.sortId, self.op, es, self.opdNats)

    def get_inner_ites(self, ite_list):
        self.es.get_inner_ites(ite_list)


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

    def toPySmt(self, sort_map, visited):
        mem_Smt = visited[self.mem.id] if self.mem.id in visited else self.mem.toPySmt(sort_map, visited)
        adr_Smt = visited[self.adr.id] if self.adr.id in visited else self.adr.toPySmt(sort_map, visited)

        res = Select(mem_Smt, adr_Smt)
        visited[self.id] = res
        return res

    def preExp(self, sort_map, stm_map):
        mem = self.mem.preExp(sort_map, stm_map)
        adr = self.adr.preExp(sort_map, stm_map)
        return expType.btor2Mgr.createReadExp(self.sortId, mem, adr)

    def simplified_ite(self, b_map):
        mem = self.mem.simplified_ite(b_map)
        adr = self.adr.simplified_ite(b_map)
        return expType.btor2Mgr.createReadExp(self.sortId, mem, adr)

    def get_inner_ites(self, ite_list):
        self.mem.get_inner_ites(ite_list)
        self.adr.get_inner_ites(ite_list)


class IteExp(expType):
    def __init__(self, sortId, b, e1, e2, id, flag=None):
        self.sortId = sortId
        self.b = b
        self.e1 = e1
        self.e2 = e2
        self.id = id
        self.flag = flag  # 负数判定

    def __str__(self):

        return "(if %s then %s else %s)" % (str(self.b), str(self.e1), str(self.e2))

    def __repr__(self):
        return "(?%s:%s,%s)" % (str(self.b), str(self.e1), str(self.e2))

    def __eq__(self, other):
        return isinstance(other,
                          IteExp) and self.sortId == other.sortId and self.b == other.b and self.e1 == other.e1 and self.e2 == other.e2 and self.id == other.id

    def toPySmt(self, sort_map, visited):
        if self.b.toPySmt(sort_map, visited).get_type() is BOOL:
            b_Smt = visited[self.b.id] if self.b.id in visited else self.b.toPySmt(sort_map, visited)
            e1_Smt = visited[self.e1.id] if self.e1.id in visited else self.e1.toPySmt(sort_map, visited)
            e2_Smt = visited[self.e2.id] if self.e2.id in visited else self.e2.toPySmt(sort_map, visited)
            res = Ite(b_Smt, e1_Smt, e2_Smt)
        else:
            b_Smt = visited[self.b.id] if self.b.id in visited else self.b.toPySmt(sort_map, visited)
            e1_Smt = visited[self.e1.id] if self.e1.id in visited else self.e1.toPySmt(sort_map, visited)
            e2_Smt = visited[self.e2.id] if self.e2.id in visited else self.e2.toPySmt(sort_map, visited)
            if self.flag is None:
                res = Ite(Equals(b_Smt, BV(1, 1)), e1_Smt, e2_Smt)
            elif self.flag == 0:
                res = Ite(Equals(BVNot(b_Smt), BV(1, 1)), e1_Smt, e2_Smt)
            elif self.flag == 1:
                res = Ite(Equals((b_Smt), BV(1, 1)), BVNot(e1_Smt), e2_Smt)
            elif self.flag == 2:
                res = Ite(Equals((b_Smt), BV(1, 1)), e1_Smt, BVNot(e2_Smt))
        visited[self.id] = res
        return res

    def preExp(self, sort_map, stm_map):
        b = self.b.preExp(sort_map, stm_map)
        e1 = self.e1.preExp(sort_map, stm_map)
        e2 = self.e2.preExp(sort_map, stm_map)
        return expType.btor2Mgr.createIteExp(self.sortId, b, e1, e2)

    def simplified_ite(self, b_map):
        if self.b.id not in b_map:
            global idx
            e1 = self.e1.simplified_ite(b_map)
            e2 = self.e2.simplified_ite(b_map)
            res = expType.btor2Mgr.createIteExp(self.sortId, self.b, e1, e2, self.flag)
            return res
        b = b_map[self.b.id]
        e1 = self.e1.simplified_ite(b_map)
        e2 = self.e2.simplified_ite(b_map)
        if b == 1:
            return e1
        elif b == 0:
            return e2

    def get_inner_ites(self, ite_list):
        if self.b.id not in ite_list:
            ite_list.append(self.b.id)
        self.b.get_inner_ites(ite_list)
        self.e1.get_inner_ites(ite_list)
        self.e2.get_inner_ites(ite_list)


class StoreExp(expType):
    def __init__(self, sortId, mem, adre, content, id):
        self.sortId = sortId
        self.mem = mem
        self.adre = adre
        self.content = content
        self.id = id

    def __str__(self):
        return "(%s[%s]<=%s)" % (str(self.mem), str(self.adre), str(self.content))

    def __repr__(self):
        return "(%s[%s]<=%s)" % (str(self.mem), str(self.adre), str(self.content))

    def __eq__(self, other):
        return isinstance(other,
                          StoreExp) and self.sortId == other.sortId and self.mem == other.mem and self.adre == other.adre and self.content == other.content and self.id == other.id

    def toPySmt(self, sort_map, visited):
        mem_Smt = visited[self.mem.id] if self.mem.id in visited else self.mem.toPySmt(sort_map, visited)
        adre_Smt = visited[self.adre.id] if self.adre.id in visited else self.adre.toPySmt(sort_map, visited)
        content_Smt = visited[self.content.id] if self.content.id in visited else self.content.toPySmt(sort_map,
                                                                                                       visited)
        res = Store(mem_Smt, adre_Smt, content_Smt)
        visited[self.id] = res
        return res

    def preExp(self, sort_map, stm_map):
        mem = self.mem.preExp(sort_map, stm_map)
        adre = self.adre.preExp(sort_map, stm_map)
        content = self.content.preExp(sort_map, stm_map)
        return expType.btor2Mgr.createStoreExp(self.sortId, mem, adre, content)

    def simplified_ite(self, b_map):
        mem = self.mem.simplified_ite(b_map)
        adre = self.adre.simplified_ite(b_map)
        content = self.content.simplified_ite(b_map)
        return expType.btor2Mgr.createStoreExp(self.sortId, mem, adre, content)


    def get_inner_ites(self, ite_list):
        self.mem.get_inner_ites(ite_list)
        self.adre.get_inner_ites(ite_list)
        self.content.get_inner_ites(ite_list)


# 存储init信息
class Init():
    def __init__(self, sortId, toInit: expType, initVal: expType, id):
        self.id = id
        self.sortId = sortId
        self.toInit = toInit
        self.initVal = initVal

    def __str__(self):
        return "(initial:%s is %s)" % (str(self.toInit), str(self.initVal))

    def toPySmt(self, sort_map, visited):
        return self.toInit.toPySmt(sort_map, visited).Equals(self.initVal.toPySmt(sort_map, visited))


'''
老师要求的Stament：
    nid:=exp
'''


class Statement():
    def __init__(self, nid: INT, exp: expType, flag=None):
        self.nid = nid
        self.exp = exp
        self.flag = flag

    def __str__(self):
        return "(next %s : %s)" % (str(self.nid), str(self.exp))

    def toPySmt(self, exp_map, sort_map, visited):
        if self.flag is None:
            return next_var(exp_map[self.nid].toPySmt(sort_map, visited)).Equals(
                self.exp.toPySmt(sort_map, visited))
        else:
            return next_var(exp_map[self.nid].toPySmt(sort_map, visited)).Equals(
                BVNot(self.exp.toPySmt(sort_map, visited)))


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

    def toPySmt(self, sort_map, visited):
        return self.nExp.toPySmt(sort_map, visited)


# 存储justice
class Justice():
    def __init__(self, id, num: str, nExps):
        self.id = id
        self.num = num
        self.nExps = nExps

    def __str__(self):
        return "%s %s " % (str(self.num), str(self.nExps))


class Btor2():
    def __init__(self, lines):
        self.mgr = Btor2Mgr(lines)

    def getBtor2Mgr(self):
        return self.mgr
