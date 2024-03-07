
# coding: utf-8

# In[1]:

import xml.etree.ElementTree as ET
import time
import re
import copy
from datetime import datetime, date, time, timedelta
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# In[2]:

rootDir = '/awips/chps_share/sa/schade/ohrfc_sa/'
modelRootDir = rootDir+'Models/ReleaseOptions/'
modelWorkingDir = modelRootDir+'work/'

modelOutputDir = modelRootDir+'pi-output/'
modelInputDir = modelRootDir+'pi-input/'

modelResultFile = modelOutputDir+'pi-output.xml'
CHPSInterfaceFile = modelInputDir+'pi-input.xml'
CHPSRunInfoFile = modelInputDir+'pi-run.xml'
modelLogFile = modelWorkingDir+'log.txt'

LogFH = open(modelLogFile,'w')
LogFH.write("Log from ReleaseOptions.py")
LogFH.close

ET.register_namespace('',"http://www.wldelft.nl/fews/PI")

runTree = ET.parse(CHPSRunInfoFile)
currentDateElem = runTree.find("{http://www.wldelft.nl/fews/PI}time0")
currentDate = currentDateElem.get('date')
currentTime = currentDateElem.get('time')
currentDT = datetime.strptime(currentDate+" "+currentTime, "%Y-%m-%d %H:%M:%S")
currentTimestamp = currentDT.strftime("%Y-%m-%dT%H:%M:%S")


# In[3]:

def createSeries(hin,parm,rng,values):
    hout = copy.deepcopy(hin)
    forecastStartDateElem = header.find("{http://www.wldelft.nl/fews/PI}startDate")
    forecastStartDate = forecastStartDateElem.get('date')
    forecastStartTime = forecastStartDateElem.get('time')
    # print parm, hin.find("{http://www.wldelft.nl/fews/PI}parameterId").text
    hout.find("{http://www.wldelft.nl/fews/PI}parameterId").text = parm
    series = ET.Element("series")
    
    series.append(hout)
    len(rng)
    
    if (len(rng) == len(df[tsID])):
      for n in range(0,len(rng)-1):
        #stringDT = rng[n]
        #dt = datetime.strptime(stringDT, "%Y-%m-%d %H:%M:%S")
        #print rng[n],values[n],rng[n].strftime("%Y-%m-%d")
        event = ET.SubElement(series,"event")
        event.set("date", rng[n].strftime("%Y-%m-%d"))
        event.set("time", rng[n].strftime("%H:%M:%S"))
        event.set("value", '%.5f' % values[n])
        event.set("flag", '0')
    else:
      print "Nope"
    
    #series.getroot().append(series)
    # Here's what the event line includes:
    #    <event date="2015-03-10" time="12:00:00" value="35.966396" flag="0"/>
#    for value in values:
#        event = ET.SubElement(series,"event")
#        event.set("date", '%.5f' % value)
#        event.set("time", '%.5f' % value)
#        event.set("value", '%.5f' % value)
#        event.set("flag", '0' % value)
        #ET.dump(event)
    #return series
    #tree = ET.ElementTree(series)
    return series


# In[4]:

def createRepeat(index,ident,df,dates):

  aaa = df.loc[index,ident]
  #print aaa

  ldRpt = pd.concat([aaa] * (len(df)/len(aaa)+1),ignore_index=True)
  xx = ldRpt.values[:len(dates)]
  #print ldRpt
  return pd.Series(xx,index=dates)


# In[5]:

# Read the file, make an ET, and find interesting things

tree = ET.parse(CHPSInterfaceFile)

header = tree.find("{http://www.wldelft.nl/fews/PI}series/{http://www.wldelft.nl/fews/PI}header")
#ET.dump(header)
#forecastStartDateElem = tree.find("{http://www.wldelft.nl/fews/PI}series/{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}startDate")
forecastStartDateElem = header.find("{http://www.wldelft.nl/fews/PI}startDate")
forecastStartDate = forecastStartDateElem.get('date')
forecastStartTime = forecastStartDateElem.get('time')
forecastStartDT = datetime.strptime(forecastStartDate+" "+forecastStartTime, "%Y-%m-%d %H:%M:%S")

forecastEndDateElem = header.find("{http://www.wldelft.nl/fews/PI}endDate")
forecastEndDate = forecastEndDateElem.get('date')
forecastEndTime = forecastEndDateElem.get('time')
forecastEndDT = datetime.strptime(forecastEndDate+" "+forecastEndTime, "%Y-%m-%d %H:%M:%S")

rng = pd.date_range(start=forecastStartDT, end=forecastEndDT, freq='6H')
obsRng = pd.date_range(start=forecastStartDT, end=forecastEndDT, freq='6H')

dt = tree.find("{http://www.wldelft.nl/fews/PI}series/{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}timeStep")
#ET.dump(dt)
#dtUnit = dt.get('unit')
#dtMult = dt.get('multiplier')
# Load everything into a Pandas DataFrame.

df = pd.DataFrame()
tsIDs = []

# First timeseries from the input file.


for ts in tree.findall('.//{http://www.wldelft.nl/fews/PI}series'):
  for header in ts.findall('.//{http://www.wldelft.nl/fews/PI}header'):
    parm = header.find(".//{http://www.wldelft.nl/fews/PI}parameterId")
    loca = header.find(".//{http://www.wldelft.nl/fews/PI}locationId")
    # We will assume the locationID needs to be one connected to 
    # the SQIN timeseries, although the file may contain other 
    # locationIDs.
    if parm.text == 'SQIN':
        simID = loca.text
    if parm.text == 'RQOT':
        relID = loca.text
    if parm.text == 'QIN':
        obsID = loca.text
    
    tsID = parm.text + "_" + loca.text
    #tsIDs.append(tsID)
    #print tsID
    inputData = []
    datetimeArray = []
    for event in ts.iterfind('.//{http://www.wldelft.nl/fews/PI}event'):
      try:
        value = float(event.get('value'))
        if value > -0.001 and value < 0.001:
          value = 0       
        if value > 100000 or value < -10000:
          value = np.nan
        if value == -999:
            value = np.nan
        time = event.get('time')
        date = event.get('date')      
        dt = datetime.strptime(date+" "+time, "%Y-%m-%d %H:%M:%S")
        timestamp = dt.strftime("%Y-%m-%dT%H:%M:%S")
        inputData.append(value)
        datetimeArray.append(dt)
      except:
        print('This did not work!')
    df[tsID] = pd.Series(inputData,index=datetimeArray,dtype='float64')


# Next construct the different outputs.

# Match Inflows (ResOpt-MF) - Copy the SQIN for all the inflow into the ResOpt. 
tsID = 'ResOpt-MF'
tsIDs.append(tsID)
df[tsID] = df['SQIN_'+simID]

# Persistance Flows (ResOpt-PF) - Copy the latest QIN into the ResOpt.
tsID = 'ResOpt-PF'
tsIDs.append(tsID)
df[tsID] = df['RQOT_'+relID][df[forecastStartDT:currentDT]['RQOT_'+relID].last_valid_index()]

# Owner's Schedule (ResOpt-OS) - ResOpt from the owner into the ResOpt.
tsID = 'ResOpt-OS'
tsIDs.append(tsID)
df[tsID] = df['RQOT_'+relID]

# Repeat Last Day (ResOpt-LD) - Repeat QIN for previous 24 hours for the full extent of the ResOpt.
tsID = 'ResOpt-LD'
tsIDs.append(tsID)
lastDay = df[currentDT+timedelta(minutes=-(24*60)):currentDT+timedelta(minutes=-1)]['QIN_'+obsID]

pat = lastDay/lastDay.sum()
patNoI = pd.Series(pat.values)
#pat*len(df)/len(pat)+1
#np.tile(pat,(len(df)/len(pat)+1,1))
#rng = df.index
patRpt = pd.concat([pat] * (len(df)/len(pat)+1),ignore_index=True)
#len(rng)
xx = patRpt.values[:len(rng)]
ts = pd.Series(xx,index=rng)
df['Pat'] = ts
df[tsID] = ts*df['ResOpt-OS']
#df.loc[lastDay.index,:]

df[tsID] = createRepeat(lastDay.index,'QIN_'+obsID,df,rng)

# Scale LD Peaking to MF (ResOpt-MFP) - Normalize last 24 hours to create a peaking pattern, and apply that pattern to the MF ResOpt.
tsID = 'ResOpt-MFP'
df[tsID] = df['Pat']*df['ResOpt-MF']

# Scale LD Peaking to PF (ResOpt-PFP) - Normalize last 24 hours to create a peaking pattern, and apply that pattern to the PF ResOpt. 
tsID = 'ResOpt-PFP'
df[tsID] = df['Pat']*df.loc[lastDay.index,'ResOpt-PF'].sum()

# Scale LD Peaking to OS (ResOpt-OSP) - Normalize last 24 hours to create a peaking pattern, and apply that pattern to the OS ResOpt.
tsID = 'ResOpt-OSP'
df[tsID] = df['Pat']*df.loc[lastDay.index,'ResOpt-OS'].sum()



#print df['ResOpt-MF']
print df['ResOpt-MF'].resample('1D')

#aaa = df.loc[lastDay.index,'QIN_'+obsID]
#print aaa

#ldRpt = pd.concat([aaa] * (len(df)/len(aaa)+1),ignore_index=True)
#xx = ldRpt.values[:len(rng)]
#print ldRpt
#ts = pd.Series(xx,index=rng)
#print ts
#df[tsID] = ts
#test = df['Pat']*1000
#ts
#np.random.randn(len(rng))
#df

#patRptDF = pd.DataFrame({'patterns':patRpt})
#patRpt #DF
#df.index
#df.join(patRpt)


# In[7]:

df['ResOpt_MF']


# In[16]:

# This makes a blank output ElementTree.
outtree = copy.deepcopy(tree)
for ts in outtree.iter("{http://www.wldelft.nl/fews/PI}TimeSeries"):
  for series in ts.findall("{http://www.wldelft.nl/fews/PI}series"):
    #parm = series.find("{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}parameterId").text
    #print parm
    ts.remove(series)
#ET.dump(outtree)


# In[17]:

#ts = df['RQOT_KIZP1'].last_valid_index()
df['RQOT_KIZP1'][df['RQOT_KIZP1'].last_valid_index()]


# In[20]:

# >>> Working to here!  Need to add date, time and flag to output!
df = df.fillna(-999.0)
for tsOut in tsIDs:
  #ET.dump(header)
  lmno = createSeries(header,tsOut,rng,df[tsOut])
  #ET.dump(header)
    
#lmno
#ET.dump(lmno)
  outtree.getroot().append(lmno)

#ET.dump(outtree)
#outtree.getroot()
outtree.write(modelResultFile)


# if (len(rng) == len(df[tsID])):
#     print "YES"
# else:
#     print "Nope"

# In[4]:

forecastIntervalElem = tree.find("{http://www.wldelft.nl/fews/PI}series/{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}timeStep")
forecastIntervalValue = int(forecastIntervalElem.get('multiplier'))
forecastIntervalUnits = forecastIntervalElem.get('unit')

if (forecastIntervalUnits == 'hour'):
  interval = timedelta(hours=forecastIntervalValue)
else:
  interval = timedelta(seconds=forecastIntervalValue)

print interval.seconds


# In[5]:

dt = datetime.strptime(forecastStartDate+" "+forecastStartTime, "%Y-%m-%d %H:%M:%S")
timestamp = dt.strftime("%Y-%m-%dT%H:%M:%S")

print timestamp


# In[34]:

currentDT+timedelta(days=-1)


# In[8]:

df.index


# In[55]:

pd.__version__


# In[18]:

parm = series.find('{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}parameterId').text


# In[67]:

lastDay*pat


# In[88]:

df['RQOT_KIZP1']


# In[103]:

df['RQOT_KIZP1'].shift(-2)


# In[104]:

ts12 = df['RQOT_KIZP1'].shift(-2).resample('D', how = 'sum', loffset='-12H')
ts18 = df['RQOT_KIZP1'].shift(-2).resample('D', how = 'sum', loffset='-6H')
ts00 = df['RQOT_KIZP1'].shift(-2).resample('D', how = 'sum')
ts06 = df['RQOT_KIZP1'].shift(-2).resample('D', how = 'sum', loffset='6H')
patdf = pd.DataFrame({'ts12':ts12, 'ts18':ts18,'ts00':ts00,'ts06':ts06})
patdf


# In[125]:

s1 = df['RQOT_KIZP1'].shift(2).resample('D', how = 'sum', loffset='-12H')
s2 = df['RQOT_KIZP1'].shift(2).resample('D', how = 'sum', loffset='-6H')
s3 = df['RQOT_KIZP1'].shift(2).resample('D', how = 'sum')
s4 = df['RQOT_KIZP1'].shift(2).resample('D', how = 'sum', loffset='6H')
#dfR = pd.DataFrame({'data':df['RQOT_KIZP1'].shift(2).resample('D', how = 'sum', loffset='-6H')})
#pd.merge(dfL,dfR,left_index=True, right_index=True, how='outer')
pd.concat([s1,s2,s3,s4]).sort_index()


# In[58]:

test1 = df.join(pat * (len(df)/len(pat)+1),columns=['test'])
test1[currentDT+timedelta(minutes=-(24*60-1)):currentDT]


# In[20]:

df.shift(4)['RQOT_KIZP1']


# In[11]:

events


# In[12]:

vals


# In[13]:

plt.plot(vals)


# In[14]:

plt.show()


# Notes. Not executed

# In[ ]:

tree3 = copy.deepcopy(tree2)
for series in tree3.iterfind('{http://www.wldelft.nl/fews/PI}series'):
  ID = series.find('{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}locationId').text
  for parm in series.findall('./{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}parameterId'):
    parm.text = "RQOT_B"
  for i in range(indexOfCurrentTime+1,len(events)+1):
     series[i].attrib['value'] = str(Bs[ID][i-indexOfCurrentTime-1])
  tree.getroot().append(series)


# In[90]:

currentTimestamp


# In[4]:

MFs = {}
PFs = {}
OSs = {}
LDs = {}
MFPs = {}
PFPs = {}
OSPs = {}


# In[17]:

data = pd.DataFrame()
#outputs = pd.DataFrame()


# In[5]:

for series in tree.iter('{http://www.wldelft.nl/fews/PI}series'):
  ID = series.find('{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}locationId').text
  parm = series.find('{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}parameterId').text
  vals = [] 
  indexOfCurrentTime = 0
  events = []
  index = []
  for event in series.findall('{http://www.wldelft.nl/fews/PI}event'):
    events.append(event)
    vals.append(float(event.attrib['value']))
    
    if (event.attrib['date']==currentDT.strftime("%Y-%m-%d")
    and event.attrib['time']==currentDT.strftime("%H:%M:%S") ):
      indexOfCurrentTime = len(vals)
    tmpDF = pd.DataFrame()
  
  print indexOfCurrentTime, len(vals)-indexOfCurrentTime

