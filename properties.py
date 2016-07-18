import numpy as np
from scipy import stats
import pylab as pl
import csv
from collections import Counter
pl.ion()
from ast import literal_eval
from geopy.distance import VincentyDistance as vincenty

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

#neighborhood code '047' not present at all in latest_assessments but present in original data. Must have changed to another code later on. Looking at some examples it probably is the same as 04T and was just mistyped at digitization

neighborhood_improvements={}
average_improvements={}
for neigh in neighborhood_dict:
    improvement_list=[float(row[36]) for row in neighborhood_dict[neigh] if float(row[36])!=0]
    neighborhood_improvements[neigh]=improvement_list
    average_improvements[neigh]=np.mean(improvement_list)

del average_improvements['']

min_imp=np.min(average_improvements.values())
max_imp=np.max(average_improvements.values())
print min_imp#least improvement:143839.184557
print max_imp#least improvement:5229619.56759
diff=max_imp-min_imp
print diff #5085780.38303

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
            if land_val!=0:
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

#SF_coord=(‎37.773972,‎-122.431297)

neighborhood_list=neighborhood_dict.keys()
neighborhood_list.remove('')
neighborhood_locations={}
neigh_location_means={}
for neigh in neighborhood_list:
    location_list=[]
    for row in neighborhood_dict[neigh]:
        try:
            location=row[-1]
            if location!='':
                location=list(literal_eval(location))
                if location[0]>37 and location[0]<38 and location[1]<-122 and location[1]>-123:
                    location_list.append(location)
                else:
                    print location
            else:
                pass
        except:
            print row
    location_list=np.array(location_list)
    neighborhood_locations[neigh]=location_list
    mean_x=np.mean(location_list[:,0])
    mean_y=np.mean(location_list[:,1])
    std_x=np.std(location_list[:,0])
    std_y=np.std(location_list[:,1])
    neigh_location_means[neigh]=[mean_x,mean_y,std_x,std_y]

neigh_areas={}

for neigh in neighborhood_list:
    neighborhood_coords=neigh_location_means[neigh]
    neighborhood_center=(neighborhood_coords[0],neighborhood_coords[1])
    fake_point_x=(neighborhood_coords[0]+neighborhood_coords[2],neighborhood_coords[1])
    fake_point_y=(neighborhood_coords[0],neighborhood_coords[1]+neighborhood_coords[3])
    a=vincenty(neighborhood_center, fake_point_x).km
    b=vincenty(neighborhood_center, fake_point_y).km
    area=np.pi*a*b
    neigh_areas[neigh]=area
    
total_area=np.sum(neigh_areas.values())
print total_area#31.9950435419 square km
print np.max(neigh_areas.values())#3.0345566135

#get only first of each assessments for each property:
first_assessments=[]
unknown_year=[]
for prop_i in property_dict:
    prop_assessments=property_dict[prop_i]
    if prop_i=='7085015': #this property has a messed up row where year is an empty string which is probably year 2011 (the only one missing)
        for row in prop_assessments:
            if row[0]=='':
                row[0]='2011'
    years_i=[int(row[0]) for row in prop_assessments]
    first_year=np.argmin(years_i)
    first_assessment_i=prop_assessments[first_year]
    first_assessments.append(first_assessment_i)

units_by_year={}
for row in first_assessments:
    built_year=row[8]
    if built_year!='':
        built_year=int(built_year)
        num_units=int(row[13])
        if num_units>0:
            if built_year in units_by_year:
                units_by_year[built_year]=units_by_year[built_year]+[num_units]
            else:
               units_by_year[built_year]=[num_units] 

year_list=np.sort(units_by_year.keys())
before_1950=[]
after_1950=[]
for year in units_by_year:
    if 1776<=year<1950:
        before_1950=before_1950+units_by_year[year]
    elif 1950<=year<=2015:
        after_1950=after_1950+units_by_year[year]

units_before=np.mean(before_1950)#2.1199384930804714
units_after=np.mean(after_1950)#2.5397953504302779

print units_after-units_before#0.41985685735

zip_dict={}
for row in latest_assessments:
    zip_code=row[39]
    if zip_code in zip_dict:
        zip_dict[zip_code]=zip_dict[zip_code]+[row]
    else:
        zip_dict[zip_code]=[row]

zip_units={}
zip_ratios={}
for zip_code in zip_dict:
    zip_list=[]
    for row in zip_dict[zip_code]:
        bedrooms=row[10]
        units=row[13]
        if bedrooms!='' and units!='' and bedrooms!='0' and units!='0':
            bedrooms=int(bedrooms)
            units=int(units)
            zip_list.append([units,bedrooms])
    if zip_list==[]:
        print zip_code
    else:
        zip_ray=np.array(zip_list)
        zip_units[zip_code]=zip_ray
        mean_units=np.mean(zip_ray[:,0])
        mean_bedrooms=np.mean(zip_ray[:,1])
        ratio=mean_bedrooms/mean_units
        zip_ratios[zip_code]=ratio

del zip_ratios['']

max_zip = zip_ratios.keys()[np.argmax(zip_ratios.values())]#
print zip_ratios[max_zip],max_zip#3.80756013746 94116

zip_properties={}
area_ratios={}
for zip_code in zip_dict:
    property_list=[]
    lot_list=[]
    area_list=[]
    for row in zip_dict[zip_code]:
        property_area=row[19]
        lot_area=row[21]
        if lot_area!='' and property_area!='' and lot_area!='0' and property_area!='0':
            property_area=float(property_area)
            lot_area=float(lot_area)
            property_list.append(property_area)
            lot_list.append(lot_area)
            area_list.append([property_area,lot_area])
    if area_list==[]:
        print zip_code
    else:
        zip_properties[zip_code]=zip_list
        mean_property_area=np.mean(property_list)
        mean_lot_area=np.mean(lot_list)
        ratio=mean_property_area/mean_lot_area
        print mean_property_area,mean_lot_area,ratio
        area_ratios[zip_code]=ratio

del area_ratios['']

max_zip = area_ratios.keys()[np.argmax(area_ratios.values())]#
print area_ratios[max_zip],max_zip#13.5872646159 94104


