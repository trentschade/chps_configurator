#!/awips2/python/bin/python

import xml.etree.ElementTree as ET
import time
import re
import copy
from datetime import datetime, date, time, timedelta
import numpy as np

# Dictionary to convert from CHPS units to datetime units.
# unitConv = {'second':'seconds', 'hour':'hours', 'day':'days'}

# Need to receive data from input files

rootDir = '/awips/chps_share/sa/schade/ohrfc_sa/'
modelRootDir = rootDir+'Models/selectReleases/'
modelWorkingDir = modelRootDir+'work/'

modelOutputDir = modelRootDir+'pi-output/'
modelInputDir = modelRootDir+'pi-input/'

modelResultFile = modelOutputDir+'pi-output.xml'
CHPSInterfaceFile = modelInputDir+'pi-input.xml'
CHPSRunInfoFile = modelInputDir+'pi-run.xml'
modelLogFile = modelWorkingDir+'log.txt'

LogFH = open(modelLogFile,'w')
LogFH.write("Log from esitmateReleases.py")
LogFH.close

ET.register_namespace('',"http://www.wldelft.nl/fews/PI")

runTree = ET.parse(CHPSRunInfoFile)
currentDateElem = runTree.find("{http://www.wldelft.nl/fews/PI}time0")
currentDate = currentDateElem.get('date')
currentTime = currentDateElem.get('time')
currentDT = datetime.strptime(currentDate+" "+currentTime, "%Y-%m-%d %H:%M:%S")
currentTimestamp = currentDT.strftime("%Y-%m-%dT%H:%M:%S")

tree = ET.parse(CHPSInterfaceFile)
outtree = copy.deepcopy(tree)
for series in outtree.iter("{http://www.wldelft.nl/fews/PI}series"):
  parm = series.find("{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}parameterId").text
  if parm == 'RQOT':
    outtree.getroot().remove(series)

forecastStartDateElem = tree.find("{http://www.wldelft.nl/fews/PI}series/{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}startDate")
forecastStartDate = forecastStartDateElem.get('date')
forecastStartTime = forecastStartDateElem.get('time')

forecastIntervalElem = tree.find("{http://www.wldelft.nl/fews/PI}series/{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}timeStep")
forecastIntervalValue = int(forecastIntervalElem.get('multiplier'))
forecastIntervalUnits = forecastIntervalElem.get('unit')

if (forecastIntervalUnits == 'hour'):
  interval = timedelta(hours=forecastIntervalValue)
else:
  interval = timedelta(seconds=forecastIntervalValue)

print interval.seconds

dt = datetime.strptime(forecastStartDate+" "+forecastStartTime, "%Y-%m-%d %H:%M:%S")
timestamp = dt.strftime("%Y-%m-%dT%H:%M:%S")

print timestamp

As = {}
Bs = {}
Cs = {}
revisedSchedule={}
locations = []

for series in tree.iter('{http://www.wldelft.nl/fews/PI}series'):
  loc = series.find('{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}locationId').text
  parm = series.find('{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}parameterId').text
  ID = loc+parm
  vals = [] 
  indexOfCurrentTime = 0
  events = []
  for event in series.findall('{http://www.wldelft.nl/fews/PI}event'):
    events.append(event)
    vals.append(float(event.attrib['value']))
    if (event.attrib['date']==currentDT.strftime("%Y-%m-%d")
    and event.attrib['time']==currentDT.strftime("%H:%M:%S") ):
      indexOfCurrentTime = len(vals)
  print indexOfCurrentTime, len(vals)-indexOfCurrentTime
  vals = np.array(vals)
  vals[vals==-999]=np.nan

  last4 = np.array(vals[indexOfCurrentTime-4:indexOfCurrentTime])
  last4count = np.nan_to_num(last4)
  last4bool = ~np.isnan(last4)
  if (last4count.sum()==0):
   pat = np.zeros(len(last4))*last4
  else:
   pat = last4/last4count.sum()
  forecast = vals[indexOfCurrentTime:]
  forecast = forecast.reshape(len(forecast)/4,4)
  forecastTotals = np.nan_to_num(forecast).sum(1)
  forecastTotals = np.repeat(forecastTotals,4)
  forecastTotals = forecastTotals.reshape(len(forecastTotals)/4,4)

  if (parm=='RQOT'):

    zA = np.tile(last4,(len(vals)-indexOfCurrentTime)/4)
    zA = zA.flatten()
    zA[np.isnan(zA)]=-999.0
    As[ID] = zA

    zB = forecastTotals.flatten()
    zB[np.isnan(zB)]=-999.0
    Bs[ID] = zB

    zC = (forecastTotals*pat*4).flatten()
    zC[np.isnan(zC)]=-999.0
    Cs[ID] = zC
    print forecastTotals
    print pat
    print zC
  
    final = np.array([zA,zB,zC])
    final = final.transpose()
    #print final
    
  if (parm=='RESREL'):
    vals[np.isnan(vals)]=0
    releaseIndex = vals[indexOfCurrentTime:].astype(int)
    print releaseIndex.shape
    print releaseIndex
    revisedSchedule[ID] = final[np.arange(len(final)),releaseIndex]
    print ID
#    print revisedSchedule[ID].transpose()
    locations.append(loc)
    print loc

# now build everything back...
for series in outtree.iter('{http://www.wldelft.nl/fews/PI}series'):
  for parm in series.findall('./{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}parameterId'):
    parm.text = "RQOT_C"
    print parm.text

  for i in range(indexOfCurrentTime+1,len(events)+1):
    series[i].attrib['value'] = str(Cs[loc+'RQOT'][i-indexOfCurrentTime-1])

outtree2 = copy.deepcopy(outtree)
for series in outtree2.iterfind('{http://www.wldelft.nl/fews/PI}series'):
  ID = series.find('{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}locationId').text
  for parm in series.findall('./{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}parameterId'):
    parm.text = "RQOT_A"
  for i in range(indexOfCurrentTime+1,len(events)+1):
     series[i].attrib['value'] = str(As[loc+'RQOT'][i-indexOfCurrentTime-1]) 
  outtree.getroot().append(series)

outtree3 = copy.deepcopy(outtree2)
for series in outtree3.iterfind('{http://www.wldelft.nl/fews/PI}series'):
  ID = series.find('{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}locationId').text
  for parm in series.findall('./{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}parameterId'):
    parm.text = "RQOT_B"
  for i in range(indexOfCurrentTime+1,len(events)+1):
     series[i].attrib['value'] = str(Bs[loc+'RQOT'][i-indexOfCurrentTime-1])     
  outtree.getroot().append(series)

outtree4 = copy.deepcopy(outtree3)
for series in outtree4.iterfind('{http://www.wldelft.nl/fews/PI}series'):
  ID = series.find('{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}locationId').text
  for parm in series.findall('./{http://www.wldelft.nl/fews/PI}header/{http://www.wldelft.nl/fews/PI}parameterId'):
    parm.text = "RQOT_REVISED"
  for i in range(indexOfCurrentTime+1,len(events)+1):
     series[i].attrib['value'] = str(revisedSchedule[loc+'RESREL'][i-indexOfCurrentTime-1])     
  outtree.getroot().append(series)

outtree.write(modelResultFile)
