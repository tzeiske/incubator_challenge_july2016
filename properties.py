import numpy as np
import scipy as sp
import pylab as pl
import csv
from collections import Counter

data=[]
with open('Historic_Secured_Property_Tax_Rolls.csv') as f:
    reader=csv.reader(f)
    header=reader.next()
    for line in reader:
        data.append(line)

classes=[row[6] for row in data]
class_counter=Counter(classes)
most_common=class_counter.most_common()[0]
print "most common class:",most_common[0] #Class 'D'
print "most common percentage:",float(most_common[1])/len(classes) #0.470725322714
