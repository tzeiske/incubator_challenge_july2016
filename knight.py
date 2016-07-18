import numpy as np
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
T=1024 #number of jumps
mod_i=29 #modulo of interest

modsums=[]
for i in range(1000000):
    modsums.append(mod_sum(T,mod_i))

print np.mean(modsums) #for T=1024 mod 1024: 511.229189, for 10 and 10:4.583518
print np.std(modsums) # for T=1024 mod 1024: 70.1039544776, for 10 and 10:2.85894504034

#probability that divisible by 7 is fraction of 0's in list of modsums
print modsums.count(0) #how often divisible by 7 when mod_i is 7: 146854 our of 1M: 0.146854, for 35 it's: 26736

#if it's divisible by 7 and 5, it must also be divisible by 35 (both prime numbers)
#probability that its divisible by 5 given that it's divisible by 7 should be 26736.0/146854=0.1820583708989881

#23 and 29 are also prime numbers. Their product is 667
#probability of sum being divisible by 23 given that its divisible by 29 is the count of 0's in the modsum list for mod_i=667 divided by the counts of 0's in the modsum list for 29
#How many times in 1M is the sum divisible by 29:34288
#Ho wmany times by 667: 3918
#ratio is 0.1142673821745217
