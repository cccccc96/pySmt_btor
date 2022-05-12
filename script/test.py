import os

sufix='2019C'

print(os.listdir('../case/'+sufix))
for file in os.listdir('../case/'+sufix):
    filename = '../case/'+sufix+'/'+file
    if 'smt2' not in filename:
        os.system('python main.py '+filename)

# print(os.listdir('../case/2019C'))
# for file in os.listdir('../case/2019C'):
#     filename = '../case/2019C/'+file
#     os.system('python main.py '+filename)