import random

INSTRUCTIONLINE = 6
### 0 check [1-2] snapshot else transfer
from header import *
if __name__ == '__main__':
    for i in range(len(clientIPs)):
        file = open("test{}".format(i),"w+")
        j = INSTRUCTIONLINE
        while(j):
            j -= 1
            type = random.randint(0,6)
            if type == 1 or type == 2:
                file.write("{:d}\n".format(type))
            else:
                tmp = i
                while clientGraph[i][tmp] == 0:
                    tmp = random.randint(0, len(clientIPs)-1)
                money = random.randint(1,3)
                print("{:d} {:d} {:d} {:d}".format(type,i,tmp,money))
                file.write("{:d} {:d} {:d} {:d}\n".format(type,i,tmp,money))
            file.write("0\n")
        file.close()