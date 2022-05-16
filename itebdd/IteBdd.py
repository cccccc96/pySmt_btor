from enum import Enum
from typing import List
from pysmt.shortcuts import *
import logging

logging.basicConfig(level=logging.INFO)



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

    def dfs(self,conditonList:List,resList:List):
        if self.terminal is not None:
            conditonList.append(self.terminal)
            f = IteBddNode.mgr.prot.createAndExpFromArray(conditonList)
            resList.append(f)
            conditonList.pop()
            return

        conditonList.append(self.condition)
        self.left.dfs(conditonList,resList)
        conditonList.pop()

        conditonList.append(IteBddNode.mgr.prot.createNotExp(self.condition))
        self.right.dfs(conditonList,resList)
        conditonList.pop()

    def dfs_without_zero(self,conditonList:List,resList:List):
        if self.terminal is not None:
            conditonList.append(self.terminal)
            f = IteBddNode.mgr.prot.createAndExpFromArray(conditonList)
            if str(simplify(IteBddNode.mgr.prot.ToPySmtFormat(self.terminal))) != '0_1':
                resList.append(f)
            conditonList.pop()
            return

        conditonList.append(self.condition)
        self.left.dfs_without_zero(conditonList,resList)
        conditonList.pop()

        conditonList.append(IteBddNode.mgr.prot.createNotExp(self.condition))
        self.right.dfs_without_zero(conditonList,resList)
        conditonList.pop()
    
    def __str__(self):
        if self.terminal is not None:
            return str(self.terminal)
        else:
            return "(if %s then %s else %s)" % (str(self.condition), str(self.left), str(self.right))

    def __eq__(self, other):
        return str(self)==str(other)


