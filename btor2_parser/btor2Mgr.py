from btor2_parser import btor2
from pysmt.shortcuts import *
from MC_Util.PySmtUtil import *

idx=10000

class Btor2Mgr():
    ref = 0

    def __init__(self, lines):
        btor2.expType.btor2Mgr= self

        '''
        语法分析
        '''
        self.node_map = {}
        for line in lines:
            if isinstance(line[0], btor2.StateKind):
                if len(line) > 1:
                    line[0].name = line[1]
            if isinstance(line[0], btor2.InputKind):
                if len(line) > 1:
                    line[0].name = line[1]
            if isinstance(line[0], btor2.PropertyKind) and line[0].kind == "output":
                self.node_map[line[0].nid].name = line[1]
            if isinstance(line[0], btor2.nodeType):
                self.node_map[line[0].nodeID.id] = line[0]

        ref = len(self.node_map)
        '''
        老师要求的exp和statement
        '''
        self.exp_map = {}  # exp存储在这里
        self.nextStatement_map = {}  # next存储在这里

        #  node2Exp
        for node in self.node_map.values():
            self.exp_map = node.node2Exp(self.exp_map)
        # nextDict
        for node in self.node_map.values():
            if isinstance(node, btor2.NextKind):
                if node.prenid < 0:
                    self.nextStatement_map[node.nodeID.id] = btor2.Statement(node.curnid, self.exp_map[-node.prenid], True)
                else:
                    self.nextStatement_map[node.nodeID.id] = btor2.Statement(node.curnid, self.exp_map[node.prenid])

        '''
            我定义PySmt迁移系统需要的
        '''
        self.sort_map = {}  # sort存在这里
        self.init_map = {}  # init存在这里
        self.prop_map = {}  # 属性存在这里
        self.var_map = {}  # 变量input/state 存在这里

        for node in self.node_map.values():
            if isinstance(node, btor2.SortKind):
                self.sort_map[node.nodeID.id] = node

        for node in self.node_map.values():
            if isinstance(node, btor2.InitKind):
                toInit = self.exp_map[node.nid]
                initVal = self.exp_map[node.val]
                self.init_map[node.nodeID.id] = btor2.Init(node.sid, toInit, initVal, node.nodeID.id)

        for i in self.exp_map:
            if isinstance(self.exp_map[i], (btor2.InputExp, btor2.VarExp)):
                self.var_map[i] = self.exp_map[i]

        for node in self.node_map.values():
            if isinstance(node, btor2.PropertyKind):
                self.prop_map[node.nodeID.id] = btor2.Property(node.kind, self.exp_map[node.nid], node.nodeID.id)

    def toTS_PySmtFormat(self):

        vars = []
        inits = []
        nexts = []
        constraints = []
        badstates = []

        for varExp in self.var_map.values():
            vars.append(varExp.toPySmt(self.sort_map, {}))
        for init in self.init_map.values():
            inits.append(init.toPySmt(self.sort_map, {}))
        for next in self.nextStatement_map.values():
            nexts.append(next.toPySmt(self.exp_map, self.sort_map, {}))
        for prop in self.prop_map.values():
            if prop.kind is btor2.PropertyEnum.constraint:
                # 待修改： constraint 应该类似assume？要加到每一步里，参照一下pono，之后记得处理
                constraints.append(prop.toPySmt(self.sort_map, {}))
            elif prop.kind is btor2.PropertyEnum.bad:
                badstates.append(prop.toPySmt(self.sort_map, {}))

        # return TransitionSystem(vars, And(inits), nexts[7]), constraints, badstates
        return TransitionSystem(vars, And(inits), And(nexts)), constraints, badstates[0]

    def get_var_from_id(self, id):
        return self.var_map[id]

    def get_vars(self):
        vars = {}
        for varExp in self.var_map.values():
            vars[varExp.name] = (varExp.toPySmt(self.sort_map, {}))
        return vars

    def get_update(self):
        res = dict()
        for next in self.nextStatement_map.values():
            key = self.exp_map[next.nid].toPySmt(self.sort_map, {})
            value = next.exp.toPySmt(self.sort_map, {})
            res[key] = value
        return res

    def createUifExp(self, sortId, op, es):
        Btor2Mgr.ref+=1
        self.exp_map[Btor2Mgr.ref]=btor2.UifExp(sortId, op, es, Btor2Mgr.ref)
        return self.exp_map[Btor2Mgr.ref]

    def createUifIndExp(self, sortId,op, es, opdNats):
        Btor2Mgr.ref+=1
        self.exp_map[Btor2Mgr.ref]= btor2.UifIndExp(sortId, op, es, Btor2Mgr.ref, opdNats)
        return self.exp_map[Btor2Mgr.ref]

    def createReadExp(self, sortId, mem, adr):
        Btor2Mgr.ref += 1
        self.exp_map[Btor2Mgr.ref] = btor2.ReadExp(sortId, mem,adr,Btor2Mgr.ref)
        return self.exp_map[Btor2Mgr.ref]

    def createIteExp(self, sortId,b,e1,e2,flag):
        Btor2Mgr.ref += 1
        self.exp_map[Btor2Mgr.ref] = btor2.IteExp(sortId,b,e1,e2,Btor2Mgr.ref,flag)
        return self.exp_map[Btor2Mgr.ref]

    def createStoteExp(self, sortId, mem, adre, content):
        Btor2Mgr.ref += 1
        self.exp_map[Btor2Mgr.ref] = btor2.StoreExp(sortId, mem, adre,content, Btor2Mgr.ref)
        return self.exp_map[Btor2Mgr.ref]

    def simplifyIte(self, ite_exp):
        def _f(ite_exp, innner_ite_list, b_map, res, i):
            """
           遍历2^n种情况
           :param ite_exp: 待化简的表达式
           :param innner_ite_list: ite_exp中的所有ite，用nodeid存成一个list
           :param b_map: 全排列用的辅助表
           :param res:结果存在这里
           :param i:递归深度
           :return:
           """
            if i == len(innner_ite_list):
                simplified_ite_exp = ite_exp.simplified_ite({}, b_map)
                condition = None
                # 计算一下当前情况的 condition ， 0代表某个inner_ite的b取非，1代表某个inner_ite的b取正
                for i in b_map:
                    if condition is None:
                        if b_map[i] == 0:
                            condition = self.createUifExp(1, 'not', [self.exp_map[i]])
                        elif b_map[i] == 1:
                            condition = self.exp_map[i]
                    else:
                        if b_map[i] == 0:
                            left = condition
                            right = self.createUifExp(1, 'not', [self.exp_map[i]])
                            condition = self.createUifExp(1, 'and', [left, right])
                        elif b_map[i] == 1:
                            left = condition
                            right = self.exp_map[i]
                            condition = self.createUifExp(1, 'and', [left, right])
                x = self.createUifExp(1, 'and', [condition, simplified_ite_exp])
                res.append(x)
                return
            b_map[innner_ite_list[i]] = 0
            _f(ite_exp, innner_ite_list, b_map, res, i + 1)
            b_map[innner_ite_list[i]] = 1
            _f(ite_exp, innner_ite_list, b_map, res, i + 1)

        global idx
        inner_ite_list = []
        ite_exp.get_inner_ites(inner_ite_list, [])
        print('inner')
        for i in inner_ite_list:
            print(i, self.exp_map[i])
        inner_ite_list.sort()
        if len(inner_ite_list) == 0:
            print('没有ite')
            return
        res = []
        _f(ite_exp, inner_ite_list, {}, res, 0)

        print('内部ite个数：' + str(len(inner_ite_list)))
        not0list = []
        for i in range(len(res)):
            print('----')
            print('f' + str(i))
            item = res[i]
            print(serialize(simplify(item.toPySmt(self.sort_map, {}))).replace(' ? 1_1 : 0_1', ''))
            solver = Solver()
            if (is_sat(simplify(item.toPySmt(self.sort_map, {})).Equals(BV(1, 1)))):
                not0list.append(i)
        print('不为0的fi：')
        print(not0list)

        print('----')
        simpliedite = self.createUifExp(1, 'or', [res[0], res[1]])
        for i in range(2, len(res)):
            simpliedite = self.createUifExp(1, 'or', [simpliedite, res[i]])
        # 返回f1\/f2...\/fn 和 [f1,f2,...,fn]
        return simpliedite, res

    def ToPySmtFormat(self, exp):
        return exp.toPySmt(self.sort_map,{})


