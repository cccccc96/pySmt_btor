from lark import Lark, Transformer, v_args, exceptions
import trajForm


grammar = r"""

    trajectory : CNAME "is" INT                                            -> trajbv
                | trajectory "and" trajectory                               -> trajand
                | CNAME "->" trajectory                                     -> trajguard
                | "N" trajectory                                              -> trajnext
            
    ants: trajectory
    
    cons: trajectory

    steassert:    ants "==>"  cons                                         -> steassert 



    %import common.NEWLINE
    %import common.CNAME
    %import common.WS
    %import common.INT
    %import common.ESCAPED_STRING
    %ignore WS

"""


@v_args(inline=True)
class SteTransformer(Transformer):
    def __init__(self):
        pass

    def trajbv(self, node, val):
        return trajForm.TrajIsBV(str(node),int(val))

    def trajand(self, left, right):
        return trajForm.TrajAnd(left , right)

    def trajguard(self, guard, f):
        return trajForm.TrajGuard(guard,f)

    def trajnext(self, f):
        return trajForm.TrajNext(f)

    def ants(self, ant):
        return ant

    def cons(self, cons):
        return cons

    def steassert(self, ant, cons):
        return trajForm.SteAssert(ant,cons)

ste_parser = Lark(grammar, start="steassert", parser="lalr", transformer=SteTransformer())


def parse_file(filename):
    with open(filename, "r") as f:
        return ste_parser.parse(f.read())

if __name__ == "__main__":
    prot = parse_file("assert_test")
    print(prot)
