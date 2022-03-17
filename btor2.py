from enum import Enum
from debug import SIMULATION_KIND, TREE_DISPLAY
from pysmt.shortcuts import Symbol, Not, And, Ite, BV, Equals
from pysmt.shortcuts import is_sat, is_unsat, Solver, TRUE, FALSE
from pysmt.typing import BOOL, BVType
import btor2parser


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


class stateType():
    def __init__(self, sid, name=None):
        self.sid = sid
        self.name = name

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
        return "bitvec %d" % (self.len)

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
        return isinstance(other, SortKind) and self.nid == other.nid and self.nodeID == other.nodeID


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
        self.indent_num = 0

    def __str__(self):
        if SIMULATION_KIND:
            return "(const %s %s)" % (str(self.sort), str(self.val))
        else:
            if TREE_DISPLAY:
                return "%s%s" % (' ' * self.indent_num, str(self.val))
            else:
                return str(self.val)

    def toPySmt(self):
        if self.typ is constEnum.const:
            if isinstance(self.sort, BVExp):
                val = int(self.val, 2)
                if self.sort.len == 1 and val == 0:
                    return FALSE()
                elif self.sort.len == 1 and val == 1:
                    return TRUE()
                elif self.sort.len != 1:
                    return BV(val, self.sort.len)
            elif isinstance(self.sort, ArrayExp):
                assert "Array 待完善"
        else:
            assert "constd consth 待完善"


class BVExp(expType):
    def __init__(self, id, len):
        self.id = id
        self.len = len

    def __str__(self):
        return "%s-bv" % (str(self.len))

    def toPySmt(self):
        if self.len == 1:
            return BOOL
        return BVType(self.len)


class ArrayExp(expType):
    def __init__(self, id, size: expType, len: expType):
        self.id = id
        self.len = len
        self.size = size

    def __str__(self):
        return "arr[%s][%s]" % (str(self.len), str(self.len))


class StateExp(expType):
    def __init__(self, id, sort: expType, name=None):
        self.id = id
        self.sort = sort
        if name is None:
            self.name = "node" + str(id)
        else:
            self.name = name
        self.indent_num = 0
        self.pre = None

    def __str__(self):
        if self.name != None:
            if SIMULATION_KIND:
                return "state-%s" % (self.name)
            else:
                if TREE_DISPLAY:
                    return ' ' * self.indent_num + ("%s" % self.name)
                else:
                    return self.name
        else:
            # return "state[%s]]" % (str(self.sort))
            if TREE_DISPLAY:
                return ' ' * self.indent_num + "state%s" % (str(self.id))
            else:
                return "state%s" % (str(self.id))

    def toPySmt(self):
        typename = self.sort.toPySmt()
        name = self.name
        return Symbol(name, typename)


class InputExp(expType):
    def __init__(self, id, typ: inputEnum, sort: expType, name=None):
        self.id = id
        self.typ = typ
        self.sort = sort
        self.indent_num = 0
        if name is None:
            self.name = "node" + str(id)
        else:
            self.name = name

    def __str__(self):
        if self.name is not None:
            if SIMULATION_KIND:
                return "input_%s" % (str(self.sort))
            else:
                if TREE_DISPLAY:
                    return "%s%s" % (' ' * self.indent_num, self.name)
                else:
                    return "%s" % self.name
        else:
            return "%sinput_%d" % (' ' * self.indent_num, self.id)

    def toPySmt(self):
        typename = self.sort.toPySmt()
        name = self.name
        return Symbol(name, typename)


# id op sExp(sid) list_nExp(nid*)
class UifExp(expType):
    def __init__(self, id, op: str, sExp: expType, nExp, indent_num=0):
        self.id = id
        self.op = op
        self.sExp = sExp  # ?
        self.nExp = nExp
        self.indent_num = indent_num

    def __str__(self):
        if TREE_DISPLAY:
            if len(self.nExp) == 2:
                self.nExp[0].indent_num = self.indent_num + 2
                self.nExp[1].indent_num = self.indent_num + 2
                str1 = ' ' * self.indent_num + str(self.op)
                str2 = '\n' + ' ' * self.indent_num + str(self.nExp[0])
                str3 = '\n' + ' ' * self.indent_num + str(self.nExp[1])
                return str1 + str2 + str3
            elif len(self.nExp) == 1:
                self.nExp[0].indent_num = self.indent_num + 2
                return "%s%s\n%s" % (' ' * self.indent_num, str(self.op), ' '.join(str(n) for n in self.nExp))
            else:
                return "error-UifExp"
        else:
            if len(self.nExp) == 2:
                self.nExp[0].indent_num = self.indent_num + 2
                self.nExp[1].indent_num = self.indent_num + 2
                return "(%s %s %s)" % (str(self.op), str(self.nExp[0]), str(self.nExp[1]))
            elif len(self.nExp) == 1:
                self.nExp[0].indent_num = self.indent_num + 2
                return "(%s %s)" % (str(self.op), str(self.nExp[0]))
            else:
                return "error-UifExp"


# id opidx sExp(sid) nExp(nid) vals(int list)
class UifIndExp(expType):
    def __init__(self, id, opidx, sExp: expType, nExp: expType, vals):
        self.id = id
        self.opidx = opidx
        self.sExp = sExp
        self.nExp = nExp
        self.vals = vals

    def __str__(self):
        return "(%s %s %s %s)" % (str(self.op), str(self.sExp), str(self.nExp), str(self.vals))


class ReadExp(expType):
    def __init__(self, id, sort: expType, mem: expType, adr: expType):
        self.id = id
        self.mem = mem
        self.adr = adr
        self.sort = sort

    def __str__(self):
        return "%s[%s]" % (str(self.mem), str(self.adr).replace(' ', ''))


# b? e1: e2
class IteExp(expType):
    def __init__(self, id, sort: expType, b: expType, e1: expType, e2: expType, indent_num):
        self.id = id
        self.b = b
        self.sort = sort
        self.e1 = e1
        self.e2 = e2
        self.indent_num = indent_num

    def __str__(self):
        if TREE_DISPLAY:
            self.b.indent_num = self.indent_num + 4
            self.e1.indent_num = self.indent_num + 4
            self.e2.indent_num = self.indent_num + 4
            str1 = '%sif\n' % (' ' * self.indent_num) + str(self.b)
            str2 = '\n%sdo\n' % (' ' * self.indent_num) + str(self.e1)
            str3 = '\n%selse\n' % (' ' * self.indent_num) + str(self.e2)
            return str1 + str2 + str3
        else:
            return "(%s? %s: %s)" % (str(self.e1), str(self.b), str(self.e2))

    def toPySmt(self):
        return Ite(self.b.toPySmt(), self.e1.toPySmt(), self.e2.toPySmt())


class StoreExp(expType):
    def __init__(self, id, sort: expType, mem: expType, adr: expType, content: expType):
        self.id = id
        self.sort = sort
        self.mem = mem
        self.adr = adr
        self.content = content

    def __str__(self):
        return "%s[%s]:=%s" % (str(self.mem), str(self.adr).replace(' ', ''), str(self.content))


class AddExp(expType):
    def __init__(self, id, sort, left, right):
        self.id = id
        self.sort = sort
        self.left = left
        self.right = right

    def toPySmt(self):
        return self.left.toPySmt() + self.right.toPySmt()


class AndExp(expType):
    def __init__(self, id, sort, left, right):
        self.id = id
        self.sort = sort
        self.left = left
        self.right = right

    def toPySmt(self):
        return And(self.left.toPySmt(), self.right.toPySmt())


class NotExp(expType):
    def __init__(self, id, sort, subExp):
        self.id = id
        self.sort = sort
        self.subExp = subExp

    def toPySmt(self):
        return Not(self.subExp.toPySmt())


class EqExp(expType):
    def __init__(self, id, sort, left, right):
        self.id = id
        self.sort = sort
        self.left = left
        self.right = right

    def toPySmt(self):
        return Equals(self.left.toPySmt(), self.right.toPySmt())


# toInit 初始化为 initval
class InitExp(expType):
    def __init__(self, id, sort, toInit: expType, initVal: expType):
        self.id = id
        self.sort = sort
        self.toInit = toInit
        self.initVal = initVal

    def __str__(self):
        return "(initial:%s is %s)" % (str(self.toInit), str(self.initVal))

    def toPySmt(self):
        return self.toInit.toPySmt().Equals(self.initVal.toPySmt())


# toInit 初始化为 initval
class NextExp(expType):
    def __init__(self, id, sort, cur: expType, pre: expType):
        self.id = id
        self.sort = sort
        self.cur = cur
        self.pre = pre
        cur.pre = self.pre

    def __str__(self):
        return "(next %s : %s)" % (str(self.pre), str(self.cur))
        # return str(self.pre)

    def toPySmt(self):
        return next_var(self.cur.toPySmt()).Equals(self.pre.toPySmt())


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
        return "%s:\n%s" % (str(self.kind), str(self.nExp))

    def toPySmt(self):
        return self.nExp.toPySmt()


class JusticeExp(expType):
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


class preExp(expType):
    def __init__(self, nowExp: expType):
        self.nowExp = nowExp
        self.preExp = self.preExp_dfs(self.nowExp)

    def __str__(self):
        return "%s" % str(self.preExp)

    def preExp_dfs(self, exp: expType):

        if isinstance(exp, StateExp):
            # print("4-------", exp, exp.pre)
            exp = exp.pre
            return exp

        if isinstance(exp, UifExp):
            # print("3-------", exp)
            if len(exp.nExp) == 2:
                exp.nExp[0] = self.preExp_dfs(exp.nExp[0])
                exp.nExp[1] = self.preExp_dfs(exp.nExp[1])
            if len(exp.nExp) == 1:
                exp.nExp[0] = self.preExp_dfs(exp.nExp[0])
        if isinstance(exp, PropertyExp):
            # print("2-------", exp)
            exp.nExp = self.preExp_dfs(exp.nExp)

        # print("1------", exp)
        return exp


def next_var(v):
    """Returns the 'next' of the given variable"""
    return Symbol("next(%s)" % v.symbol_name(), v.symbol_type())


def at_time(v, t):
    """Builds an SMT variable representing v at time t"""
    return Symbol("%s@%d" % (v.symbol_name(), t), v.symbol_type())


class TransitionSystem(object):
    # T(a,b,next(a),next(b),...)
    # 0-1时刻 T(a0,b0,a1,b1,..)
    # 1-2时刻 T(a0,b0,a1,b1,..)
    def __init__(self, variables, init, trans):
        self.variables = variables
        self.init = init
        self.trans = trans


class Btor2():
    def __init__(self, lines):
        self.node_map = {}
        self.exp_map = {}
        self.next_map = {}  # next
        self.init_map = {}  # init
        self.prop_map = {}  # 属性
        self.var_map = {}  # 变量input/state

        for line in lines:
            if isinstance(line[0], StateKind):
                if len(line) > 1:
                    line[0].state.name = line[1]
            if isinstance(line[0], InputKind):
                if len(line) > 1:
                    line[0].name = line[1]
            if isinstance(line[0], nodeType):
                self.node_map[line[0].nodeID.id] = line[0]

        for node in self.node_map.values():

            assert (isinstance(node, nodeType))

            # sortkind bv/arr
            if isinstance(node, SortKind):
                if isinstance(node.bv_or_arr, bvType):
                    exp = BVExp(node.nodeID.id, node.bv_or_arr.len)
                elif isinstance(node.bv_or_arr, ArrayType):
                    size = self.exp_map[(node.bv_or_arr.ele_typ)]
                    x_len = self.exp_map[(node.bv_or_arr.len)]
                    exp = ArrayExp(node.nodeID.id, size, x_len)
                self.exp_map[exp.id] = exp

            # inputkind input/const
            elif isinstance(node, InputKind):
                if isinstance(node.inpT, input1Type):
                    typ = node.inpT.inpEnum
                    sort = self.exp_map[(node.inpT.sortId)]
                    exp = InputExp(node.nodeID.id, typ, sort, node.name)
                    self.var_map[exp.id] = exp
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
                exp = StateExp(node.nodeID.id, sort, node.state.name)
                self.exp_map[exp.id] = exp
                self.var_map[exp.id] = exp

            # opidx 一个定义都没有，都是uifindexp
            elif isinstance(node, IndOpKind):
                op = node.opT
                exp1 = self.exp_map[node.sid]
                exp2 = self.exp_map[node.opdNid]
                vals = [node.ns1, node.ns2]
                exp = UifIndExp(node.nodeID.id, op, exp1, exp2, vals)
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
                    exp = IteExp(node.nodeID.id, sort, b, e1, e2, 0)
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
                elif node.opT == "add":
                    sid = node.sid
                    opdNids = node.opdNids
                    sort = self.exp_map[sid]
                    left = self.exp_map[opdNids[0]]
                    right = self.exp_map[opdNids[1]]
                    exp = AddExp(node.nodeID.id, sort, left, right)
                elif node.opT == "and":
                    sid = node.sid
                    opdNids = node.opdNids
                    sort = self.exp_map[sid]
                    left = self.exp_map[opdNids[0]]
                    right = self.exp_map[opdNids[1]]
                    exp = AndExp(node.nodeID.id, sort, left, right)
                elif node.opT == "eq":
                    sid = node.sid
                    opdNids = node.opdNids
                    sort = self.exp_map[sid]
                    left = self.exp_map[opdNids[0]]
                    right = self.exp_map[opdNids[1]]
                    exp = EqExp(node.nodeID.id, sort, left, right)
                elif node.opT == "not":
                    sid = node.sid
                    opdNids = node.opdNids
                    sort = self.exp_map[sid]
                    subExp = self.exp_map[opdNids[0]]
                    exp = NotExp(node.nodeID.id, sort, subExp)
                else:
                    sid = node.sid
                    opdNids = node.opdNids
                    sort = self.exp_map[sid]
                    n = [self.exp_map[opdNids[0]]]
                    if opdNids[1] is not None:
                        n.append(self.exp_map[opdNids[1]])
                    if opdNids[2] is not None:
                        n.append(self.exp_map[opdNids[2]])
                    exp = UifExp(node.nodeID.id, node.opT, sort, n, 0)
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
                self.next_map[exp.id] = exp

            elif isinstance(node, InitKind):
                sid = node.sid
                nid = node.nid
                valid = node.val
                sort = self.exp_map[sid]
                toInit = self.exp_map[nid]
                initVal = self.exp_map[valid]
                exp = InitExp(node.nodeID.id, sort, toInit, initVal)
                self.exp_map[exp.id] = exp
                self.init_map[exp.id] = exp

            elif isinstance(node, PropertyKind):
                kind = node.kind
                nid = node.nid
                nExp = self.exp_map[nid]
                exp = PropertyExp(node.nodeID.id, kind, nExp)
                self.exp_map[exp.id] = exp
                self.prop_map[exp.id] = exp

            elif isinstance(node, JusticeKind):
                exp = JusticeExp(node.nodeID.id, node.nids)
                self.exp_map[exp.id] = exp

            else:
                print(str(node) + " : unkown!")

    # display the exp_map of ine nid
    def display(self, nid, pre=False):
        if pre == True:
            preCondition = preExp(self.exp_map[nid])
            print(preCondition)
        else:
            print(self.exp_map[nid])

    def toTS_PySmtFormat(self):
        vars = []
        inits = []
        nexts = []
        props = []
        for varExp in self.var_map.values():
            vars.append(varExp.toPySmt())
        for initExp in self.init_map.values():
            inits.append(initExp.toPySmt())
        for nextExp in self.next_map.values():
            nexts.append(nextExp.toPySmt())
        for propExp in self.prop_map.values():
            props.append(propExp.toPySmt())

        return TransitionSystem(vars,And(inits),And(nexts)) , props

        print(1)
