from lark import Lark, Transformer, v_args, exceptions
#
# grammar = r"""
#     ?num: /[1-9][0-9]*/
#     ?uint: INT
#     ?symbol: CNAME
#     ?nid: num
#     ?sid: num
#     ?const: 'const' sid /[0-1]+/
#     ?constd: 'constd' sid  uint
#             | 'constd' sid "-" uint
#     ?consth: 'consth' sid /[0-9a-fA-F]+/
#     ?input: /['input''one''ones''zero']/ sid
#             | const
#             | constd
#             | consth
#     ?state: 'state' sid
#     ?bitvec: 'bitvec' num
#     ?array: 'array' sid sid
#     ?opidx:'ext'|'slice'
#     ?op: 'not'|'inc'|'dec'|'neg'|'redand'|'redor'|
#     ?node: sid 'sort' array
#         | sid 'sort' bitvec
#         | nid input
#         | nid state
#         | nid opidx sid nid uint uint
#         | nid opidx sid nid uint
#         | nid op sid nid nid nid
#         | nid op sid nid nid
#         | nid op sid nid
#         | nid 'init' sid nid nid
#         | nid 'next' sid nid nid
#         | nid 'bad' nid
#         | nid 'constraint' nid
#         | nid 'fair' nid
#         | nid 'output' nid
#         | nid 'justice' num /nid+/
#     ?line:  node
#         | node symbol
#     ?btor: btor line
#         | line
#
#
#     ?const_decl: CNAME ":" INT
#     ?consts: "const" (const_decl ";")*                    -> consts
#
#     ?type_constr: CNAME                                   -> var_type
#         | "boolean"                                       -> boolean_type
#         | "1" ".." CNAME                                  -> scalarset_type
#         | "scalarset" "(" CNAME ")"                       -> scalarset_type
#         | "union" "{" type_constr ("," type_constr)* "}"  -> union_type
#         | "enum" "{" CNAME ("," CNAME)* "}"               -> enum_type
#         | "array" "[" type_constr "]" "of" type_constr    -> array_type
#         | "record" (type_decl ";")* "end"                 -> record_type
#     ?type_decl: CNAME ":" type_constr
#     ?types: "type" (type_decl ";")*                       -> types
#
#     ?var_decl: CNAME ":" type_constr
#     ?vars: "var" (var_decl ";")*                          -> vars
#
#     ?atom_expr: CNAME                                     -> unknown_expr
#         | atom_expr "." CNAME                             -> field_name
#         | atom_expr "[" expr "]"                          -> array_index
#         | "forall" var_decl "do" expr "end"               -> forall_expr
#         | "(" expr ")"
#
#     ?neg_expr: "!" atom_expr                              -> neg_expr
#         | atom_expr
#
#     ?eq_expr: neg_expr "=" neg_expr                       -> eq_expr
#         | neg_expr "!=" neg_expr                          -> ineq_expr
#         | neg_expr
#
#     ?and_expr: eq_expr "&" and_expr
#         | eq_expr
#
#     ?or_expr: and_expr "|" or_expr
#         | and_expr
#
#     ?imp_expr: or_expr "->" imp_expr
#         | or_expr
#
#     ?expr: imp_expr
#
#     ?cmd: "undefine" atom_expr                            -> undefine_cmd
#         | atom_expr ":=" expr                             -> assign_cmd
#         | "for" var_decl "do" cmds "end"                  -> forall_cmd
#         | "if" expr "then" cmds ("elsif" expr "then" cmds)* ("else" cmds)? "end"  -> if_cmd
#
#     ?cmds: (cmd ";")*                                     -> cmds
#
#     ?startstate: "startstate" ESCAPED_STRING cmds "endstartstate" ";"
#                 | "ruleset" var_decls "do" startstate "endruleset" ";"
#
#     ?rule: "rule" ESCAPED_STRING expr "==>" "begin" cmds "endrule" ";"
#
#     ?var_decls: var_decl (";" var_decl)*                  -> var_decls
#
#     ?rules:rule (rule)*
#
#     ?ruleset: "ruleset" var_decls "do" rules "endruleset" ";"
#
#     ?invariant: "invariant" ESCAPED_STRING expr ";"         -> invariant
#                 | "ruleset" var_decls "do" "invariant" ESCAPED_STRING expr ";" "endruleset" ";"  -> invariants
#
#     ?prot_decl: rule | ruleset | invariant
#
#     ?protocol: consts types vars startstate (prot_decl)*
#
#     COMMENT: ";" /[^\n]*/ NEWLINE
#
#     %import common.NEWLINE
#     %import common.CNAME
#     %import common.WS
#     %import common.INT
#     %import common.ESCAPED_STRING
#     %ignore WS
#     %ignore COMMENT
#
# """

# grammar = r"""
#     ?num: /[1-9][0-9]*/
#     ?nums: "num" (num ";")*
#     ?test: "-"
# """


grammar = r"""

    num: /[1-9][0-9]*/

    uint: INT

    symbol: CNAME

    nid: num

    sid: num

    const: "const" sid /[0-1]+/

    constd: "constd" sid ["-"] uint

    consth: "consth" sid /[0-9a-fA-F]+/

    input: "input" sid  
            | "one" sid
            | "ones" sid 
            | "zero" sid
            | const
            | constd
            | consth

    state: "state" sid

    bitvec: "bitvec" num

    array: "array" sid sid
    
    op: "not" 
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
        
    opidx: "sext" | "uext" | "slice"
 
    ?node:    sid "sort" array 
            | sid "sort" bitvec                                     
            | nid (input | state)
            | nid opidx sid nid uint [uint]
            | nid op sid nid [nid [nid]]
            | nid ("init" | "next") sid nid nid
            | nid ("bad" | "constraint" | "fair" | "output") nid
            | nid "justice" num (nid)+
            


    ?line: node2 [symbol] 

    ?btor:    (line)+ 
             

    COMMENT: ";" /[^\n]*/ NEWLINE

    %import common.NEWLINE
    %import common.CNAME
    %import common.WS
    %import common.INT
    %import common.ESCAPED_STRING
    %ignore WS
    %ignore COMMENT

"""

@v_args(inline=True)
class BtorTransformer(Transformer):
    def __init__(self):
        pass

    # def num(self,v):
    #     return v
    #
    # def bitvec(self,num):
    #     return num
    #
    # def nodebitvec(self,sid,bitvec):
    #     return sid





murphi_parser = Lark(grammar, start="btor", parser="lalr", transformer=BtorTransformer())


def parse_file(filename):
    with open(filename, "r") as f:
        return murphi_parser.parse(f.read())


if __name__ == "__main__":
    prot = parse_file("case/test.btor")
    print(prot.pretty())

