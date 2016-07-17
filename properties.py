import numpy as np
from scipy import stats
import pylab as pl
import csv
from collections import Counter
pl.ion()

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

lot_nums=[row[4] for row in data]
unique_properies=np.unique(lot_nums)

property_dict={}
for row in data:
    prop_i=row[4]
    if prop_i in property_dict:
        ass_list=property_dict[prop_i]
    else:
        ass_list=[]
    ass_list.append(row)
    property_dict[prop_i]=ass_list

assessment_nums=[len(prop) for prop in property_dict.values()]

#get only last of each assessments for each property:
latest_assessments=[]
unknown_year=[]
for prop_i in property_dict:
    prop_assessments=property_dict[prop_i]
    if prop_i=='7085015': #this property has a messed up row where year is an empty string which is probably year 2011 (the only one missing)
        for row in prop_assessments:
            if row[0]=='':
                row[0]='2011'
    years_i=[int(row[0]) for row in prop_assessments]
    latest_year=np.argmax(years_i)
    latest_assessment_i=prop_assessments[latest_year]
    latest_assessments.append(latest_assessment_i)

#improvement value is row index 36
improvements=[]
improvements_non0=[]
for row in latest_assessments:
    improvement=float(row[36])
    improvements.append(improvement)
    if improvement!=0:
        improvements_non0.append(improvement)

print np.median(improvements_non0) #209240.0

neighborhoods=[row[2] for row in data]
unique_neighborhoods=np.unique(neighborhoods)

#latest assessments per neighborhood:
neighborhood_dict={}
for row in latest_assessments:
    neigh=row[2]
    if neigh in neighborhood_dict:
        ass_list=neighborhood_dict[neigh]
    else:
        ass_list=[]
    ass_list.append(row)
    neighborhood_dict[neigh]=ass_list

#neighborhood code '047' not present at all in latest_assessments but present in original data. Must have changed to another code later on. Looking at some examples it probably is the same as 04T and was just mis typed at digitization

neighborhood_improvements={}
average_improvements={}
for neigh in neighborhood_dict:
    improvement_list=[float(row[36]) for row in neighborhood_dict[neigh] if float(row[36])!=0]
    neighborhood_improvements[neigh]=improvement_list
    average_improvements[neigh]=np.mean(improvement_list)

print np.min(average_improvements.values())#least improvement:143839.184557
print np.max(average_improvements.values())#least improvement:15559895.9167
diff=15559895.9167-143839.184557
print diff #15416056.7321

#growth rate of land values: P=P_0*exp(rt), in in years --> figure out r. ln(P) = ln(P_0)+r*t--> use linear regression of ln(P) against t!
#linear regression for each property and then average or average property value over all properties for each year and then linear regression using the STDev as weight??

#assessments per year:
year_dict={}
for row in data:
    year=int(row[0])
    if year in year_dict:
        ass_list=year_dict[year]
    else:
        ass_list=[]
    ass_list.append(row)
    year_dict[year]=ass_list

yearly_land_values={}
mean_land_values={}
for year in year_dict:
    land_values=[]
    for row in year_dict[year]:
        if row[37]!='':
            land_val=float(row[37])
            if land_val!=0 and land_val!='':
                land_values.append(land_val)
    yearly_land_values[year]=land_values
    mean_land_values[year]=[np.mean(land_values),np.std(land_values)]


pl.figure()
pl.errorbar(mean_land_values.keys(),[item[0] for item in mean_land_values.values()],yerr=[item[1] for item in mean_land_values.values()],fmt='.')

pl.figure()
pl.plot(mean_land_values.keys(),[np.log(item[0]) for item in mean_land_values.values()],'.')

slope,intercept,r_val,p_val,stderr = stats.linregress(mean_land_values.keys(),[np.log(item[0]) for item in mean_land_values.values()])
pl.plot(mean_land_values.keys(),np.array(mean_land_values.keys())*slope+intercept,'-')
print slope#0.0487460724514
print intercept#-85.1777429706
#ln(P0)=-85.177743-->P0=np.exp(-85.1777429706)=1.0180667341755475e-37 (it's so tiny because I used the full years as x-values and not year offsets. 1.0180667341755475e-37 is the theoretical price in the year 0 (2016 years ago).
pl.figure()
pl.plot(mean_land_values.keys(),[item[0] for item in mean_land_values.values()],'.')
pl.plot(mean_land_values.keys(),np.exp(intercept)*np.exp(slope*np.array(mean_land_values.keys())),'-')
