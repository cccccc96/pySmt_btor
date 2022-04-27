from pysmt.shortcuts import *
from typing import *
from MC_Util.PySmtUtil import *



class Trajectory():
    def toPySmt(self, node_map, t):
        return
    def path_len(self):
        return 0
    pass


class TrajIsBV(Trajectory):
    def __init__(self, node: str, val: int):
        self.node = node
        self.val = val

    def __str__(self):
        return "%s is %s" % (str(self.node),str(self.val))

    def toPySmt(self, node_map, t):
        node_FNode = node_map[self.node]
        bvtype = get_type(node_FNode)
        val_FNode = BV(self.val,bvtype.width)
        return EqualsOrIff(at_time(node_FNode,t),val_FNode)

class TrajIsVar(Trajectory):
    def __init__(self, node: str, var: str):
        self.node = node
        self.var = var

    def __str__(self):
        return "%s is %s" % (str(self.node),str(self.var))

    def toPySmt(self, node_map, t):
        node_FNode = node_map[self.node]
        bvtype = get_type(node_FNode)
        var_FNode = Symbol(self.var, bvtype)
        return EqualsOrIff(at_time(node_FNode,t),var_FNode)

class TrajAnd(Trajectory):
    def __init__(self, left: Trajectory, right: Trajectory):
        self.left = left
        self.right = right

    def __str__(self):
        return "%s and %s" % (str(self.left),str(self.right))

    def toPySmt(self, node_map, t):
        return And(self.left.toPySmt(node_map, 0), self.right.toPySmt(node_map, 0))

    def path_len(self):
        return self.left.path_len() if self.left.path_len() > self.right.path_len() else self.right.path_len()

class TrajGuard(Trajectory):
    def __init__(self, guard: any, f: Trajectory):
        self.guard = guard
        self.f = f

    def __str__(self):
        return "%s -> %s" % (str(self.guard),str(self.f))


class TrajNext(Trajectory):
    def __init__(self, f: Trajectory):
        self.f = f

    def __str__(self):
        return "N %s" % (str(self.f))

    def toPySmt(self, node_map, t):
        return self.f.toPySmt(node_map, t+1)

    def path_len(self):
        return self.f.path_len() + 1

class SteAssert():
    def __init__(self, ant:Trajectory, cons:Trajectory):
        self.ant = ant
        self.cons = cons

    def __str__(self):
        return "%s ==> %s" % (str(self.ant),str(self.cons))

    def toPySmt(self, node_map, t=None):
        k = self.ant.path_len() if self.ant.path_len() > self.cons.path_len() else self.cons.path_len()
        return self.ant.toPySmt(node_map, 0) , self.cons.toPySmt(node_map, 0), k+1

