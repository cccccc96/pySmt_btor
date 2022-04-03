from pysmt.shortcuts import *
from typing import *


class Trajectory():
    pass


class TrajIsBV(Trajectory):
    def __init__(self, node: str, val: int):
        self.node = node
        self.val = val

    def __str__(self):
        return "%s is %s" % (str(self.node),str(self.val))





class TrajAnd(Trajectory):
    def __init__(self, left: Trajectory, right: Trajectory):
        self.left = left
        self.right = right

    def __str__(self):
        return "%s and %s" % (str(self.left),str(self.right))


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

class SteAssert():
    def __init__(self, ant, cons):
        self.ant = ant
        self.cons = cons

    def __str__(self):
        return "%s ==> %s" % (str(self.ant),str(self.cons))