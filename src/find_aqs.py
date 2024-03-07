#!/awips2/python/bin/python

import xml.etree.ElementTree as ET
import re

def dupFile(inFile,outFile,strOut,strIn):
  fin = open(inFile,'r')
  filedata = fin.read()
  fin.close()
  
  newdata = filedata.replace(strOut,strIn)
  
  fout = open(outFile,'w')
  print outFile
  fout.write(newdata)
  fout.close()

def indent(elem, level=0):
    print "Elem: "+elem.tag
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i



base = '/awips/chps_share/sa/schade/ohrfc_sa/Config/'

ET.register_namespace('','http://www.wldelft.nl/fews')
lsTree = ET.parse(base+'RegionConfigFiles/ModuleInstanceDescriptors 4.0.xml')

pattern = re.compile('ADJUSTQ_.*_Forecast')
varPattern = re.compile('.*_SQIN_.*')
mergePattern = re.compile('simulation')
varObsPattern = re.compile('.*(_QIN_|_RQOT_).*')
altObsPattern = re.compile('.*_SQIN_.*')
obsPattern = re.compile('observation')

aqDict = {}
with open('aq_basin_ids.txt','r') as text:
  for line in text:
    v,k = line.split()
    aqDict[k] = v

for mod in lsTree.findall(".//{http://www.wldelft.nl/fews}moduleInstanceDescriptor"):
  modid = mod.get('id')

  if pattern.match(mod.get('id')):

    [mod, basin, modType, fcst] = modid.split("_")
    #print mod, basin

    try:
      dupFile(base+'ModuleConfigFiles/palp1/MERGETS_ARMA_PALP1_PALP1 1.97.xml',\
      base+'ModuleConfigFiles/'+aqDict[basin]+'/MERGETS_ARMA_'+basin+'_'+basin+' 1.97.xml','PALP1',basin)
    except:
      print "Error"
      continue
    try:
      dupFile(base+'ModuleConfigFiles/palp1/ARMA_PALP1_PALP1_Forecast 3.00.xml',\
          base+'ModuleConfigFiles/'+aqDict[basin]+'/ARMA_'+basin+'_'+basin+'_Forecast 1.97.xml','PALP1',basin)
    except:
      continue

    aqTree = ET.parse(base+'ModuleConfigFiles/'+aqDict[basin]+"/"+modid+'.xml')
    aqRoot = aqTree.getroot()

    tsSimTree = ET.ElementTree()
    tsObsTree = ET.ElementTree()
    obsFound = False

    for var in aqTree.findall(".//{http://www.wldelft.nl/fews}variable"):
      for varId in var.findall(".//{http://www.wldelft.nl/fews}variableId"):
        if varPattern.match(varId.text):
           #print "varId.tag: "+varId.tag
           tsSet = var.find(".//{http://www.wldelft.nl/fews}timeSeriesSet")
           #print "tsSet: "+tsSet.tag
           tsSimTree = ET.ElementTree(tsSet)
        if varObsPattern.match(varId.text):
           print "Match 1 varId.tag: "+varId.tag
           tsSet = var.find(".//{http://www.wldelft.nl/fews}timeSeriesSet")
           #print "tsSet: "+tsSet.tag
           tsObsTree = ET.ElementTree(tsSet)
           obsFound = True
        elif altObsPattern.match(varId.text) and not obsFound:
           print "Match 2 varId.tag: "+varId.text
           tsSet = var.find(".//{http://www.wldelft.nl/fews}timeSeriesSet")
           #print "tsSet: "+tsSet.tag
           tsObsTree = ET.ElementTree(tsSet)

    tsSimRoot = tsSimTree.getroot()
    tsObsRoot = tsObsTree.getroot()

######################
    mergeTree = ET.parse(base+'ModuleConfigFiles/'+aqDict[basin]+'/MERGETS_ARMA_'+basin+'_'+basin+' 1.97.xml')
    mergeRoot = mergeTree.getroot()
    print "Merge Root: "+mergeRoot.tag
    for var in mergeTree.findall(".//{http://www.wldelft.nl/fews}variable"):
      for varId in var.findall(".//{http://www.wldelft.nl/fews}variableId"):
        if mergePattern.match(varId.text):
          tsSet = var.find(".//{http://www.wldelft.nl/fews}timeSeriesSet")
          print tsSet
          var.remove(tsSet) 
          var.append(tsSimRoot)
    mergeTree = ET.ElementTree(mergeRoot)

    indent(mergeTree.getroot())
    mergeTree.write(base+'ModuleConfigFiles/'+aqDict[basin]+'/MERGETS_ARMA_'+basin+'_'+basin+' 1.97.xml')

#######################
    armaTree = ET.parse(base+'ModuleConfigFiles/'+aqDict[basin]+'/ARMA_'+basin+'_'+basin+'_Forecast 1.97.xml')
    armaRoot = armaTree.getroot()
    print "ARMA Root: "+armaRoot.tag
    for var in armaTree.findall(".//{http://www.wldelft.nl/fews}inputVariable[@variableId='observation']"):
#      for varId in var.findall(".//{http://www.wldelft.nl/fews}variableId"):
#        if obsPattern.match(varId.text):
          tsSet = var.find(".//{http://www.wldelft.nl/fews}timeSeriesSet")
          print tsSet
          var.remove(tsSet) 
          var.append(tsObsRoot)
    armaTree = ET.ElementTree(armaRoot)

    indent(armaTree.getroot())
    armaTree.write(base+'ModuleConfigFiles/'+aqDict[basin]+'/ARMA_'+basin+'_'+basin+'_Forecast 1.97.xml')


### Run this from base/ModuleConfigFiles to build the id list:
#  find . -name "ADJUSTQ_*_Forecast.xml" | awk -F/ '{ print $2,$3 }' | awk -F_ '{print $1,$2}' | awk '{print $1,$3}' > ~/dev/python/aq_basin_ids.txt
