from itebdd.IteBdd import *


from btor2_parser.btor2 import *


class IteBddMgr():
    def __init__(self, prot):
        self._uniqueTable={}
        self._computedTable = {}
        self._supports = [] # IteBddNode list
        self.prot = prot

        # 静态变量初始化
        IteBddNode.mgr = self


    def uniquify(self, l:IteBddNode,r:IteBddNode,condition:expType):
        """ 判断(l,r,level)是否在_uniqueTable中，
            如果在，返回值
            如果不在，创建一个新的BDDNode

        Args:
            l (_type_): 左节点
            r (_type_): 右节点
            condition (_type_): level

        Returns:
            Null/bddNodeInt
        """
        n = None
        key = str(l)+str(r)+str(condition)
        if key not in self._uniqueTable:
            n = IteBddNode(l,r,condition)
            self._uniqueTable[key] = n 
        return self._uniqueTable[key] 
    
    def setSupport(self, f:expType, reverse=False):
        self._supports.clear()
        """传入f,计算support,support为consitions和顺序 

        Args:
            f (expType): exp
            reverse: 顺序反转_
        """
        inner_ite_list = []
        f.get_inner_ites(inner_ite_list)
        print(inner_ite_list)
        for item in inner_ite_list:
            self._supports.append(item)
        if reverse==True:
            self._supports.reverse()
        return self._supports
    
    def getSupport(self, level:int):
        return self._supports[level]
    
    def bddKey(self, f:expType, e:expType=None):
        if e is None:
            return str(f)
        return str(f)+str(e)

    def checkTerminal(self,f:expType):
        
        # 判断内部是否有ite节点
        inner_ite_list = []
        f.get_inner_ites(inner_ite_list)
        if len(inner_ite_list)==0:
            return IteBddNode(f) 
        else:
            return None 
    
    def getLevel(self,f:expType()):
        """获取top condition

        Args:
            f (expType): 公式

        Returns:
            condition: condition
        """
        inner_ite_list = []
        f.get_inner_ites(inner_ite_list)
        for item in self._supports:
            if item in inner_ite_list:
                return self.prot.exp_map[item]

    def getLeftCofactor(self,f:expType,condition:expType):
        b_map = {}
        b_map[int(condition.id)] = 0
        return f.simplified_ite( b_map)

    def getRightCofactor(self,f:expType,condition:expType):
        b_map = {}
        b_map[int(condition.id)] = 1
        return f.simplified_ite( b_map)

    def compare(self, a:expType, b:expType):
        return str(a)==str(b)
    
    def build(self,f:expType):
        """构造BDD

        Args:
            f (expType): 传入一个大的exp,可能是任意类型的exp
        """

        # terminal 情况，没有内部的ite节点/
        if self.checkTerminal(f) is not None:
            res = self.checkTerminal(f)
            k = self.bddKey(f)
            self._computedTable[k] = res
            return res
        
        
        # 获取top condition
        condition = self.getLevel(f)

        k = self.bddKey(f, condition)

        # 已经算过了的，从表里拿
        if k in self._computedTable:
            return self._computedTable[k]

        # recursion
        fl = self.getLeftCofactor(f, condition)
        t = self.build(fl)

        fr = self.getRightCofactor(f,condition)
        e = self.build(fr)

        # # 删除冗余节点
        if t == e :
            self._computedTable[k] = t
            return t 
        
        res = self.uniquify(t,e,condition)
        self._computedTable[k] = res

        return res

    def generateExpListOfAllCondition(self,f:IteBddNode):
        """获取所有情况，返回一个数组

        :param f: IteBddNode
        :return:
        """
        resList = []
        f.dfs([],resList)
        return resList

    def generateExpListOfAllConditionWithoutZero(self,f:IteBddNode):
        """获取所有情况，返回一个数组

        :param f: IteBddNode
        :return:
        """

        resList = []
        f.dfs_without_zero([],resList)
        return resList

    def generateExpOfAllCondition(self,f:IteBddNode):
        """获取所有情况，返回一个exp

        :param f: IteBddNode
        :return:
        """
        resList = self.generateExpListOfAllCondition(f)
        return self.prot.createOrExpFromArray(resList)


        
        



        
    