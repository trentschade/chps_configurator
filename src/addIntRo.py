#!/awips2/python/bin/python

import xml.etree.ElementTree as ET
import shlex,subprocess
import StringIO
import csv

import os
import fnmatch

#aFile = '/awips/chps_share/sa/schade/ohrfc_sa/Config/ModuleConfigFiles/abbi3/SACSMA_ABBI3_ABBI3_UpdateStates.xml'
for rootDir, dirs, files in os.walk("/awips/chps_share/sa/schade/ohrfc_sa/Config/ModuleConfigFiles"):
  for aFile in fnmatch.filter(files, 'SACSMA_*.xml'):

   tree = ET.parse(os.path.join(rootDir,aFile))
   root = tree.getroot()

   importTSAList = root.find(".//{http://www.wldelft.nl/fews}importTimeSeriesActivity")

   ET.register_namespace("",'http://www.wldelft.nl/fews')

   for ts in importTSAList.findall('.//{http://www.wldelft.nl/fews}timeSeriesSets'):
    for e in ts.findall('.//{http://www.wldelft.nl/fews}timeSeriesSet'):
     for p in e.findall('.//{http://www.wldelft.nl/fews}parameterId'):
      if p.text == 'IMP_RO':
       importTimeSeriesSets = ts
       tssIntRoStr = ET.tostring(e)
       tssIntRoStr = tssIntRoStr.replace("IMP_RO","INT_RO")
       tssIntRo = ET.XML(tssIntRoStr)

       importTimeSeriesSets.append(tssIntRo)

   tree.write(os.path.join(rootDir,aFile+".new"))
   print "Wrote: "+os.path.join(rootDir,aFile+".new")

