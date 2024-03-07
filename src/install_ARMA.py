#!/awips2/python/bin/python

import xml.etree.ElementTree as ET
import re


# Takes input file and creates an output file replacing strings.
def dupFile(inFile,outFile,strOut,strIn):
  fin = open(inFile,'r')
  filedata = fin.read()
  fin.close()
  
  newdata = filedata.replace(strOut,strIn)
  
  fout = open(outFile,'w')
  fout.write(newdata)
  fout.close()

# Fixes indentation for the ET string out functions.
def indent(elem, level=0):
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
            
            
# Set some global variables...
version = '6.60'
base = '/awips/chps_share/sa/schade/ohrfc_sa/Config/'
ET.register_namespace('','http://www.wldelft.nl/fews')

# Set up the module instance descriptors.
midFile = base+'RegionConfigFiles/ModuleInstanceDescriptors 5.99.xml'
midTree = ET.parse(midFile)
midRoot = midTree.getroot()

# Set up some dictionaries
fgDict = {}
wfDict = {}
aqDict = {}
opDict = {}


### Run this from base/ModuleConfigFiles to build the id list:
#  find . -name "ADJUSTQ_*_Forecast.xml" | awk -F/ '{ print $2,$3 }' | awk -F_ '{print $1,$2}' | awk '{print $1,$3}' > ~/dev/python/aq_basin_ids.txt
#  This finds all of the ADJUSTQ operations in the modules.
#  File has columns for forecast group, workflowID, Operation, and Basin
#  
# I should try/except for this file...

with open('aq_wf_map.txt','r') as text:
  for line in text:
    fg,wf,ba,op = line.split()
    primaryKey = ba+op
    fgDict[primaryKey] = fg
    wfDict[primaryKey] = wf
    aqDict[primaryKey] = op
    opDict[primaryKey] = ba
    
# Top level loop through all of the ADJUSTQ operations:
for pK in opDict:
  ba = opDict[pK]
  fg = fgDict[pK]
  wf = wfDict[pK]
  op = aqDict[pK]
  print "Line: "+ line

# For each ADJUSTQ, we will add two files to the ModuleConfigFiles directory:
#  base+ModuleConfigFiles/{basin}/ARMA_{basin}_{operation}_Forecast {version}.xml
#  base+ModuleConfigFiles/{basin}/MERGETS_ARMA_{basin}_{operation} {version}.xml
#-------------------------------------------------------------------------------
  mergeFile = base+'ModuleConfigFiles/'+wf.lower()+'/MERGETS_ARMA_'+ba+'_'+op+' '+version+'.xml'
  armaFile  = base+'ModuleConfigFiles/'+wf.lower()+'/ARMA_'+ba+'_'+op+'_Forecast '+version+'.xml'
  dupFile('MERGETS_ARMA_basin_operation version.xml','temp.xml','basin',ba)
  dupFile('temp.xml',mergeFile,'operation',op)
  dupFile('ARMA_basin_operation_Forecast version.xml','temp.xml','basin',ba)
  dupFile('temp.xml',armaFile,'operation',op)

# Now we have to fix up some of the timeseries in these files with timeseries from the ADJUSTQ module.
  aqFile  = base+'ModuleConfigFiles/'+wf.lower()+'/ADJUSTQ_'+ba+'_'+op+'_Forecast.xml'
  aqTree = ET.parse(aqFile)
  aqRoot = aqTree.getroot()

  tsSimTree = ET.ElementTree()
  tsObsTree = ET.ElementTree()
  obsFound = False

  varPattern = re.compile('.*_SQIN_.*')
  varObsPattern = re.compile('.*(_QIN_|_RQOT_).*')
  altObsPattern = re.compile('.*_SQIN_.*')

# Find the timeseries descriptor from the ADJUSTQ operation to copy into the file.
# In the existing ADJUSTQ operation, find a simulation and an observed timeseries.
  for var in aqTree.findall(".//{http://www.wldelft.nl/fews}variable"):
    for varId in var.findall(".//{http://www.wldelft.nl/fews}variableId"):
      if varPattern.match(varId.text):
         print "varPattern Match: "+varId.text
         tsSet = var.find(".//{http://www.wldelft.nl/fews}timeSeriesSet")
         print "sim tsSet: "+tsSet.tag
         tsSimTree = ET.ElementTree(tsSet)
      if varObsPattern.match(varId.text):
         print "varObsPattern Match: "+varId.text
         tsSet = var.find(".//{http://www.wldelft.nl/fews}timeSeriesSet")
         #print "obs tsSet: "+tsSet.tag
         tsObsTree = ET.ElementTree(tsSet)
         obsFound = True
      elif altObsPattern.match(varId.text) and not obsFound:
         print "altObsPattern Match: "+varId.text
         tsSet = var.find(".//{http://www.wldelft.nl/fews}timeSeriesSet")
         #print "obs tsSet: "+tsSet.tag
         tsObsTree = ET.ElementTree(tsSet)

  tsSimRoot = tsSimTree.getroot()
  tsObsRoot = tsObsTree.getroot()

# Find the simulated in the merge tree and copy in the correct timeseries descriptor.

  mergePattern = re.compile('simulation')

  mergeTree = ET.parse(mergeFile)
  mergeRoot = mergeTree.getroot()
  print "Merge Root: "+mergeRoot.tag
  for var in mergeTree.findall(".//{http://www.wldelft.nl/fews}variable"):
    for varId in var.findall(".//{http://www.wldelft.nl/fews}variableId"):
      if mergePattern.match(varId.text):
        tsSet = var.find(".//{http://www.wldelft.nl/fews}timeSeriesSet")
        print "Found a ts Set: " + tsSet[0].text
        print "Replacing with: " + tsSimRoot[0].text
        var.remove(tsSet) 
        var.append(tsSimRoot)
  mergeTree = ET.ElementTree(mergeRoot)
  #print "mergeTree: "+mergeTree.getroot().tag
  indent(mergeTree.getroot())
  mergeTree.write(mergeFile)


# Find the obaserved in the arma tree and copy in the correct timeseries descriptor.

  armaTree = ET.parse(armaFile)
  armaRoot = armaTree.getroot()
  print "ARMA Root: "+armaRoot.tag
  for var in armaTree.findall(".//{http://www.wldelft.nl/fews}inputVariable[@variableId='observation']"):
        tsSet = var.find(".//{http://www.wldelft.nl/fews}timeSeriesSet")
        print tsSet
        var.remove(tsSet) 
        var.append(tsObsRoot)
  armaTree = ET.ElementTree(armaRoot)

  indent(armaTree.getroot())
  armaTree.write(armaFile)


# base+RegionConfigFiles/ModuleInstanceDescriptors {version}.xml
#-----------------------------------------------------

#added to existing section <moduleInstanceGroup id="{basin}_Forecast">:
#        <moduleInstanceDescriptor id="ARMA_{basin}_{operation}_Forecast">
#            <moduleId>ErrorModel</moduleId>
#        </moduleInstanceDescriptor>
#         <moduleInstanceDescriptor id="MERGETS_ARMA_{basin}_{operation}">
#            <moduleId>TransformationModule</moduleId>
#        </moduleInstanceDescriptor>
  findPattern = re.compile(wf+'_Forecast')
  for set in midTree.findall(".//{http://www.wldelft.nl/fews}moduleInstanceGroup"):
     if findPattern.match(set.get('id')):
      for aq in set.findall(".//{http://www.wldelft.nl/fews}moduleInstanceDescriptor"):
        #print "AQ: "+aq.tag
        pattern = re.compile('ADJUSTQ_'+ba+'_'+op+'_Forecast')
        if pattern.match(aq.get('id')):
          [adjQ,loc,oper,fcst] = aq.get('id').split('_')  
          #try:
          #  test = aqDict[loc]
          #except:
          #  print "Problem Basin: "+loc
          #  continue 


          ARMANode = ET.Element('moduleInstanceDescriptor')
          ARMANode.set('id','ARMA_'+ba+'_'+op+'_Forecast')
          ARMANodeModId = ET.SubElement(ARMANode,'moduleId')
          ARMANodeModId.text = 'ErrorModel'
          set.append(ARMANode)

          MergeNode = ET.Element('moduleInstanceDescriptor')
          MergeNode.set('id','MERGETS_ARMA_'+ba+'_'+op)
          MergeNodeModId = ET.SubElement(MergeNode,'moduleId')
          MergeNodeModId.text = 'TransformationModule'
          set.append(MergeNode)

          midTree = ET.ElementTree(midRoot)

#base+WorkflowFiles/{fg}/{basin}_Flow_Forecast {version}.xml
#-------------------------------------------------

#after:
#  <activity>
#		<runIndependent>false</runIndependent>
#		<moduleInstanceId>ADJUSTQ_{basin}_{operation}_Forecast</moduleInstanceId>
#	</activity>	
#add: 
#  <activity>
#		<runIndependent>false</runIndependent>
#		<moduleInstanceId>MERGETS_ARMA_{basin}_{operation}</moduleInstanceId>
#	</activity> 
#	<activity>
#		<runIndependent>false</runIndependent>
#		<moduleInstanceId>ARMA_{basin}_{operation}_Forecast</moduleInstanceId>
#	</activity> 

  wfTree = ET.parse(base+'WorkflowFiles/'+fg.lower()+'/'+wf+'_Flow_Forecast 1.00.xml')
  root = wfTree.getroot()
  #print base+'WorkflowFiles/'+fg.lower()+'/'+ba+'_Flow_Forecast.xml'
  #print wfTree.getRoot().tag
  pattern = re.compile('ADJUSTQ_'+ba+'_'+op+'_Forecast')
  #print 'ADJUSTQ_'+ba+'_'+op+'_Forecast'
  index = 1
  match = False
  for activity in wfTree.findall(".//{http://www.wldelft.nl/fews}activity"):
      index = root.getchildren().index(activity)
      MergeNode = ET.Element('activity')
      ARMANode = ET.Element('activity')
      for set in activity.findall(".//{http://www.wldelft.nl/fews}moduleInstanceId"):
        #print set.text, index
        if pattern.match(set.text):
          match = True

          MergeNodeRI = ET.SubElement(MergeNode,'runIndependent')
          MergeNodeRI.text = 'false'
          MergeNodeModId = ET.SubElement(MergeNode,'moduleInstanceId')
          MergeNodeModId.text = 'MERGETS_ARMA_'+ba+'_'+op

          ARMANodeRI = ET.SubElement(ARMANode,'runIndependent')
          ARMANodeRI.text = 'false'
          ARMANodeModId = ET.SubElement(ARMANode,'moduleInstanceId')
          ARMANodeModId.text = 'ARMA_'+ba+'_'+op+'_Forecast'

        if match == True:
          match = False
          root.insert(index+1,MergeNode)
          root.insert(index+2,ARMANode)

  indent(wfTree.getroot())
  wfTree.write(base+'WorkflowFiles/'+fg.lower()+'/'+wf+'_Flow_Forecast '+version+'.xml')

indent(midTree.getroot())
midTree.write(base+'RegionConfigFiles/ModuleInstanceDescriptors '+version+'.xml')
