from vcd import *


class VcdGen:
    def __init__(self, path: str, filename: str):
        self.modname = ''
        if filename.endswith('.vcd'):
            modname = filename[:-4]
        else:
            modname = filename
            filename += '.vcd'
        self.file = open(path + filename, 'w')
        self.writer = VCDWriter(self.file)
        self.vars = dict()


if __name__ == '__main__':
    pass
