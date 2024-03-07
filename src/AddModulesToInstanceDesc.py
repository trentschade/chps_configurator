#!/awips2/python/bin/python

import xml.etree.ElementTree as ET
import re

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



base = '/awips/chps_share/sa/schade/ohrfc_sa/Config/'

ET.register_namespace('','http://www.wldelft.nl/fews')
lsTree = ET.parse(base+'RegionConfigFiles/ModuleInstanceDescriptors 5.99.xml')
pattern = re.compile('ADJUSTQ.*_Forecast')

fgDict = {}
aqDict = {}
opDict = {}
with open('aq_wf_map.txt','r') as text:
  for line in text:
    fg,ba,op = line.split()
    fgDict[ba] = fg
    aqDict[ba] = op
    opDict[op] = ba

for set in lsTree.findall(".//{http://www.wldelft.nl/fews}moduleInstanceGroup"):
  for aq in set.findall(".//{http://www.wldelft.nl/fews}moduleInstanceDescriptor"):
    if pattern.match(aq.get('id')):
      [adjQ,loc,oper,fcst] = aq.get('id').split('_')  
      try:
        test = aqDict[loc]
      except:
        print "Problem Basin: "+loc
        continue 


      ARMANode = ET.Element('moduleInstanceDescriptor')
      ARMANode.set('id','ARMA_'+loc+'_'+oper+'_Forecast')
      ARMANodeModId = ET.SubElement(ARMANode,'moduleId')
      ARMANodeModId.text = 'ErrorModel'
      set.append(ARMANode)

      MergeNode = ET.Element('moduleInstanceDescriptor')
      MergeNode.set('id','MERGETS_ARMA_'+loc+'_'+oper)
      MergeNodeModId = ET.SubElement(MergeNode,'moduleId')
      MergeNodeModId.text = 'TransformationModule'
      set.append(MergeNode)

indent(lsTree.getroot())
lsTree.write('test.xml')    
