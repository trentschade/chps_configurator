#!/awips2/python/bin/python

import xml.etree.ElementTree as ET
import re

base = '/awips/chps_share/sa/schade/ohrfc_sa/Config/'
ET.register_namespace('','http://www.wldelft.nl/fews')

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


fgDict = {}
aqDict = {}
opDict = {}
with open('aq_wf_map.txt','r') as text:
  for line in text:
    fg,ba,op = line.split()
    fgDict[ba] = fg
    aqDict[ba] = op
    opDict[op] = ba

for aqop in opDict:
  wfTree = ET.parse(base+'WorkflowFiles/'+fgDict[opDict[aqop]].lower()+'/'+opDict[aqop]+'_Flow_Forecast 1.00.xml')
  root = wfTree.getroot()
  print base+'WorkflowFiles/'+fgDict[opDict[aqop]].lower()+'/'+opDict[aqop]+'_Flow_Forecast.xml'
  #print wfTree.getRoot().tag
  pattern = re.compile('ADJUSTQ_'+opDict[aqop]+'_'+aqDict[opDict[aqop]]+'_Forecast')
  print 'ADJUSTQ_'+opDict[aqop]+'_'+aqDict[opDict[aqop]]+'_Forecast'
  index = 1
  match = False
  for activity in wfTree.findall(".//{http://www.wldelft.nl/fews}activity"):
      index = root.getchildren().index(activity)
      MergeNode = ET.Element('activity')
      ARMANode = ET.Element('activity')
      for set in activity.findall(".//{http://www.wldelft.nl/fews}moduleInstanceId"):
        print set.text, index
        if pattern.match(set.text):
          match = True

          MergeNodeRI = ET.SubElement(MergeNode,'runIndependent')
          MergeNodeRI.text = 'false'
          MergeNodeModId = ET.SubElement(MergeNode,'moduleInstanceId')
          MergeNodeModId.text = 'MERGETS_ARMA_'+opDict[aqop]+'_'+aqDict[opDict[aqop]]

          ARMANodeRI = ET.SubElement(ARMANode,'runIndependent')
          ARMANodeRI.text = 'false'
          ARMANodeModId = ET.SubElement(ARMANode,'moduleInstanceId')
          ARMANodeModId.text = 'ARMA_'+opDict[aqop]+'_'+aqDict[opDict[aqop]]+'_Forecast'

        if match == True:
          match = False
          root.insert(index+1,MergeNode)
          root.insert(index+2,ARMANode)

  indent(wfTree.getroot())
  wfTree.write(base+'WorkflowFiles/'+fgDict[opDict[aqop]].lower()+'/'+opDict[aqop]+'_Flow_Forecast 1.99.xml')
      
        
### Run this from base/WorkflowFiles to build the id list:
#  find . -name "*_Flow_Forecast*1.00.xml" -exec grep -H 'ADJUSTQ' {} \; | awk -F/ '{print $2,$3}' | awk -F_ '{print $1,$5}' > ~/dev/python/aq_wf_map.txt
