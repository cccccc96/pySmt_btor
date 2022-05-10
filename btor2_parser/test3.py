
class k():
    def __init__(self,val):
        self.val = val 
    
    def __eq__(self, o):
        return self.val==o.val


class k2():
    def __init__(self,val):
        self.val = val 
    
    def __eq__(self, o):
        return self.val==o.val

map = dict()

str=''
for i in range(10000):
    str+='dsadsadsadad'

print(str)
map[str] = 1
# if (k(1),k2(2)) in map:
#     print(1)