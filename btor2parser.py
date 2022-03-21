from lark import Lark, Transformer, v_args, exceptions
import btor2
from bmc import *

grammar = r"""

    num: UINT                                                                 

    uint: UINT                                      

    symbol: CNAME                                  

    nid: num                                      

    sid: num                                        

    const: "const" sid UINT                        

    constd: "constd" sid ["-"] uint                 

    consth: "consth" sid CNAME

    input: "input" sid                              ->input_input
            | "one" sid                             ->input_one
            | "ones" sid                            ->input_ones
            | "zero" sid                            ->input_zero
            | const                                 ->input_const
            | constd                                ->input_constd
            | consth                                ->input_consth

    state: "state" sid                              

    bitvec: "bitvec" num

    array: "array" sid sid

    op: OP

    opidx: OPIDX

    node:    sid "sort" (array | bitvec)                                   ->node_sort
            | nid input                                                    ->node_input
            | nid state                                                    ->node_state 
            | nid opidx sid nid uint [uint]                                ->node_opidx
            | nid op sid nid [nid [nid]]                                   ->node_op 
            | nid "init" sid nid nid                                       ->node_init
            | nid "next" sid nid nid                                       ->node_next
            | nid BCFO nid                                                 ->node_property
            | nid "justice" num (nid)+                                     ->node_justice

    comment: ";" /[^\n]+/

    line:    comment                                                        ->comment       
            | node [symbol] [comment]                                       ->line
            | "\n"                                                          ->newline

    btor:    (line "\n")+                                                   ->btor


    COMMENT.2: ";" /[^\n]*/
    WHITESPACE.2: /[ \t\f]/+ 
    OP.2: "not" 
        | "inc" | "dec" | "neg" 
        | "redand" | "redor" | "redxor"
        | "iff" | "implies" 
        | "eq" | "neq" 
        | "sgt" | "ugt" | "sgte" | "ugte" | "slt" | "ult" | "slte" | "ulte"
        | "and" | "nand" | "nor" | "or" | "xnor" | "xor"
        | "rol" | "ror" | "sll" | "sra" | "srl"
        | "add" | "mul" | "sdiv" | "udiv" | "smod" | "srem" | "urem" |"sub"
        | "saddo" | "uaddo" | "sdivo" | "udivo" | "smulo" | "umulo" | "ssubo" | "usubo"
        | "concat"
        | "read"
        | "ite"
        | "write"
    OPIDX.2: "sext" | "uext" | "slice"
    BCFO.2: "bad" | "constraint" | "fair" | "output"
    INT: DIGIT+
    UINT.2: INT | "-" INT


    %import common.NEWLINE
    %import common.CNAME
    %import common.WS
    %import common.ESCAPED_STRING
    %import common.DIGIT
    %ignore WHITESPACE

"""


@v_args(inline=True)
class BtorTransformer(Transformer):
    def __init__(self):
        pass

    # num 返回int类型
    def num(self, val):
        assert (int(val) != 0)
        return int(val)

    # uint 返回int类型
    def uint(self, val):
        return int(val)

    # symbol 返回str类型
    def symbol(self, name):
        return str(name)

    # nid 返回int类型
    def nid(self, num):
        return num

    # sid 返回int类型
    def sid(self, num):
        return num

    # const.val 二进制返回str类型
    def const(self, sid, val):
        # assert是否是二进制
        return [sid, str(val)]

    # cosnt.uint 十进制返回str类型
    def constd(self, sid, uint):
        return [sid, str(uint)]

    # const.val 十六进制返回str类型
    def consth(self, sid, val):
        # assert是否是十六进制
        return [sid, str(val)]

    def input_input(self, sid):
        return btor2.input1Type(btor2.inputEnum.input, sid)

    def input_one(self, sid):
        return btor2.input1Type(btor2.inputEnum.one, sid)

    def input_ones(self, sid):
        return btor2.input1Type(btor2.inputEnum.ones, sid)

    def input_zero(self, sid):
        return btor2.input1Type(btor2.inputEnum.zero, sid)

    def input_const(self, const):
        return btor2.constType(const[0], const[1])

    def input_constd(self, const):
        return btor2.constType(const[0], const[1])

    def input_consth(self, const):
        return btor2.consthType(const[0], const[1])

    def state(self, sid):
        return sid

    def bitvec(self, num):
        return btor2.bvType(num)

    def array(self, len, ele_typ):
        return btor2.ArrayType(len, ele_typ)

    def op(self, name):
        return str(name)

    def opidx(self, name):
        return str(name)

    def node_sort(self, sort0, bv_or_arr):
        return btor2.SortKind(sort0, bv_or_arr)

    def node_input(self, nid, input):
        return btor2.InputKind(nid, input)

    def node_state(self, nid, state):
        return btor2.StateKind(nid, state)

    def node_opidx(self, nid, opT, sid, opdNid, ns1, ns2):
        return btor2.IndOpKind(nid, opT, sid, opdNid, ns1, ns2)

    def node_op(self, nid, opT, sid, *nids):
        return btor2.OpKind(nid, opT, sid, nids)

    def node_init(self, line, sid, nid, val):
        return btor2.InitKind(line, sid, nid, val)

    def node_next(self, line, sid, nid, prenid):
        return btor2.NextKind(line, sid, nid, prenid)

    def node_property(self, line, name, nid):
        return btor2.PropertyKind(line, str(name), nid)

    def node_justice(self, line, num, *nids):
        return btor2.JusticeKind(line, num, nids)

    def comment(self, comment):
        return "comment"

    def line(self, node, symbol, comment):
        return [node, symbol]

    def newline(self):
        return "\n"

    def btor(self, *line):
        return btor2.Btor2(line)


btor2_parser = Lark(grammar, start="btor", parser="lalr", transformer=BtorTransformer())


def parse_file(filename):
    with open(filename, "r") as f:
        return btor2_parser.parse(f.read())


if __name__ == "__main__":
    x = (ArrayType(BVType(1),BVType(1)))
    in_wr = Symbol("in_wr",BVType(1))
    in_wr_addr = Symbol("in_wr_addr",BVType(1))
    node45 = Symbol("node45",BVType(1))
    val = BV(1,1)

    comp = BVComp(in_wr_addr,node45)
    a = BVAnd(in_wr,comp)
    b = BVULT(node45,val)
    d = a.get_type()
    c = b.get_type()
    f = BVAnd(a,b)
    Symbol("x",ArrayType(BVType(1),BVType(1)))
    prot = parse_file("case/memory.btor2")
    # prot.display(nid=121)
    x = prot.toTS_PySmtFormat()
    # prot.display(nid=122, pre=False)
