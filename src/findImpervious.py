#!/awips2/python/bin/python

import xml.etree.ElementTree as ET
import shlex,subprocess
import StringIO
import csv

import os
import fnmatch

for rootDir, dirs, files in os.walk("/awips/chps_share/sa/schade/ohrfc_sa/Config/ModuleParFiles"):
  for afile in fnmatch.filter(files, 'SACSMA_*.xml'):
    #print afile
  


    tree = ET.parse(os.path.join(rootDir,afile))
    root = tree.getroot()
    #print root.tag

    PCTIM = 'missing '
    ADIMP = 'missing '

    elem = tree.find('.//{http://www.wldelft.nl/fews/PI}parameter[@id="PCTIM"]')
    PCTIM = elem.find('.//{http://www.wldelft.nl/fews/PI}dblValue').text
    elem = tree.find('.//{http://www.wldelft.nl/fews/PI}parameter[@id="ADIMP"]')
    ADIMP = elem.find('.//{http://www.wldelft.nl/fews/PI}dblValue').text
    

#    for groups in root.findall('.//{http://www.wldelft.nl/fews/PI}group'):
#      for parm in groups.find('.//{http://www.wldelft.nl/fews/PI}parameter[@id='PCTIM']'):
        
#        if parm.attrib.get("id") == 'PCTIM':
#          PCTIM=ET.SubElement(parm,"dblValue").
#        elif parm.attrib.get("id") == 'ADIMP':
#          ADIMP=ET.SubElement(parm, "dblValue").value

    print afile, PCTIM, ADIMP
