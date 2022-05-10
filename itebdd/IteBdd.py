from enum import Enum


# class BDD_EDGE_FLAG(Enum):
#     BDD_POS_EDGE = 0
#     BDD_NEG_EDGE = 1


class IteBddNode():
    mgr = None

    def __init__(self, *args):
        """构造函数

        Args:
            exp
        """
        self.terminal=None
        if len(args)==1:
            self.terminal = args[0]
        elif len(args)==3:
            self.left = args[0]
            self.right = args[1]
            self.condition = args[2]


    def getBddNodeInt(self):
        return self.node[0]

    def getLeft(self):
        return self.getBddNodeInt().getLeft()

    def getRight(self):
        return self.getBddNodeInt().getRight()

    def getLeftCofactor(self):
        pass

    def getRightCofactor(self):
        pass

    def getLevel(self):
        return self.getBddNodeInt().getLevel()

    def getRefCount(self):
        return self.getBddNodeInt().getRefCount()

    def dfs(self):
        if self.terminal is not None:
            return 1
        res = self.left.dfs() + self.right.dfs()
        return res

    
    def __str__(self):
        if self.terminal is not None:
            return str(self.terminal)
        else:
            return "(if %s then %s else %s)" % (str(self.condition), str(self.left), str(self.right))

    def __eq__(self, other):
        return str(self)==str(other)


class IteBddNodeInt():

 

    def __init__(self, l: IteBddNode, r: IteBddNode, level: int, refCount: int = 0, visited: bool = False):
        """不包含正负信息的BDD节点

        Args:
            l (int): 左节点
            r (int): 右节点
            level (int): level，变量顺序
            refCount (int, optional): ref. Defaults to 0.
            visited (int, optional): visited. Defaults to false.
        """
        self._left = l
        self._right = r
        self._level = level
        self._refCount = refCount
        self._visited = visited


    def getLeft(self) -> IteBddNode:
        return self._left

    def getRight(self) -> IteBddNode:
        return self._right

    def getLevel(self) -> int:
        return self._level

    def getRefCount(self) -> int:
        return self._refCount

    def isVisited(self) -> bool:
        return self._visited

    def incRefCount(self):
        self._refCount += 1

    def decRefCount(self):
        self._refCount -= 1
