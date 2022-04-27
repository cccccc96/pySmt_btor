import sys
import os
from time import perf_counter

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)


from btor2_parser import btor2parser
from MC_Util.bmc import *
from  pysmt.shortcuts import *
import os
import sys

def test(i):
    z = Symbol('y',BVType(i+1))

if __name__ == "__main__":
    # prot_btor = btor2parser.parse_file("../case/memory_wrong.btor2")



    # print(os.listdir('../case/2018A'))
    # for file in os.listdir('../case/2018A'):
    #     filename = '../case/2018A/'+file
    #     print(filename)
    #     prot = btor2parser.parse_file(filename)
    #     trans, constraints, badstates = prot.toTS_PySmtFormat()
    #     bmc = BMC(trans)
    #     bmc.run_bmc(constraints, badstates, 4)

    filename = sys.argv[1]
    print(filename)
    prot = btor2parser.parse_file(filename)
    trans, constraints, badstates = prot.toTS_PySmtFormat()
    bmc = BMC(trans)
    start = perf_counter()
    res = bmc.run_bmc(constraints, badstates, 10)
    end = perf_counter()
    file=open('./res2.log','a+')
    file.write(filename+','+res+','+str(end-start)+'\n')
    file.close()
    print(end-start)



    # print(os.listdir('../case/mann'))
    # for file in os.listdir('../case/mann'):
    #     filename = '../case/mann/'+file
    #     print(filename)
    #     prot = btor2parser.parse_file(filename)
    #     trans, constraints, badstates = prot.toTS_PySmtFormat()
    #     bmc = BMC(trans)
    #     bmc.run_bmc(constraints, badstates, 4)