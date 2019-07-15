import os, sys, json, time


#######################
# parameters
#######################
epochs = int(sys.argv[1])
activate = sys.argv[2]
dropout = float(sys.argv[3])

print(sys.argv)

#######################
# Out of memory Error
#######################
arr = []
for i in range(1200):
    a = bytearray(10000000)
    time.sleep(0.1)
    arr.append(a)


