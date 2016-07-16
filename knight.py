import numpy as np
import scipy as sp
import pylab as pl
import random

allowed_moves = {0:[4,6],1:[6,8],2:[7,9],3:[4,8],4:[0,3,9],5:[],6:[0,1,7],7:[2,6],8:[1,3],9:[2,4]}

def mod_sum(T,mod_i):
    position=0 #always start at 0
    totsum=0
    for step in range(T):
        #print "step:",step+1
        #print "position:",position
        #print "taking step"
        position=random.choice(allowed_moves[position])
        #print "new position:",position
        totsum+=position
        #print "new sum:",totsum
    modsum=totsum%mod_i
    #print "modulo base",mod_i,"is:",modsum
    return modsum

#sample 1M times
T=10 #number of jumps
mod_i=10 #modulo of interest

modsums=[]
for i in range(1000000):
    modsums.append(mod_sum(T,mod_i))

print np.mean(modsums) #for T=1024 mod 1024: 511.229189, for 10 and 10:4.583518
print np.std(modsums) # for T=1024 mod 1024: 70.1039544776, for 10 and 10:2.85894504034


    
