from vcd.writer import *


class VcdGen:
    def __init__(self, path: str, filename: str):
        if not path.endswith('/'):
            path += '/'
        self.modname = ''
        if filename.endswith('.vcd'):
            self.modname = filename[:-4]
        else:
            self.modname = filename
            filename += '.vcd'
        self.file = open(path + filename, 'w')
        self.writer = VCDWriter(self.file)
        self.vars = list()

    def __del__(self):
        self.writer.close()
        self.file.close()

    def addVar(self, name: str, type: VarType, size: int, init=0):
        v = self.writer.register_var(self.modname, name, type, size, init)
        self.vars.append(v)
        return v

    def change(self, var: Variable, time: TimeValue, v: VarValue):
        self.writer.change(var, time, v)


if __name__ == '__main__':
    vcd = VcdGen('./', 'counter.vcd')
    x = vcd.writer.register_var(vcd.modname,'x',VarType.string,128,'0')
    cnt = vcd.addVar('cnt', VarType.reg, 8, 0)
    c = vcd.addVar('flag', VarType.wire, 8, 0)
    clk = vcd.addVar('clk', VarType.wire, 1, 0)
    for i in range(0, 8):
        vcd.change(x, i, '123')
        vcd.change(cnt, i, 128)
        vcd.change(clk, i, ~clk.value)


