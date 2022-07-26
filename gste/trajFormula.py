from pysmt.shortcuts import *
class TrajForm:
    def __init__(self, formula, fromTime, toTime):
        self.formula = formula
        self.fromTime = fromTime
        self.toTime = toTime


class TrajAssertions:
    def __init__(self):
        self.antList = []
        self.consList = []

    def addAnt(self, ant):
        # antecedent
        self.antList.append(ant)

    def addCons(self, cons):
        # consequence
        self.consList.append(cons)

    def getFromT(self, T):
        # 取出从T时刻开始的(T,T) / (T,T+1)
        # return: (T,T2)
        res = []
        for ant in self.antList:
            if ant.fromTime == T:
                if (ant.fromTime,ant.toTime) not in res:
                    res.append((ant.fromTime,ant.toTime))
        return res

    def getAntFromTo(self, fromTime, toTime):
        res = []
        for ant in self.antList:
            if ant.fromTime == fromTime and ant.toTime == toTime:
                res.append(ant.formula)
        return And(res)

    def getAntListFromTo(self, fromTime, toTime):
        # 根据fromTime 和 toTime 获取对应的AntList列表
        res = []
        for ant in self.antList:
            if ant.fromTime == fromTime and ant.toTime == toTime:
                res.append(ant.formula)
        return res

    def getConsFromTo(self, fromTime, toTime):
        # 根据fromTime 和 toTime 获取对应的ConsList列表
        res = []
        for cons in self.consList:
            if cons.fromTime == fromTime and cons.toTime == toTime:
                res.append(cons.formula)
        if len(res)==0:
            return TRUE()
        return And(res)