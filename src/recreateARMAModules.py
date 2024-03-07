#!/awips2/python/bin/python

import xml.etree.ElementTree as ET

base = '/awips/chps_share/sa/schade/ohrfc_sa/Config/'

fgDict = {}
aqDict = {}
with open('aq_wf_map.txt','r') as text:
  for line in text:
    fg,ba,op = line.split()
    fgDict[ba] = fg
    aqDict[ba] = op

def dupFile(inFile,outFile,strOut,strIn):
  fin = open(inFile,'r')
  filedata = fin.read()
  fin.close()
  
  newdata = filedata.replace(strOut,strIn)
  
  fout = open(outFile,'w')
  print outFile
  fout.write(newdata)
  fout.close()



for basin in aqDict:
    try:
      dupFile(base+'ModuleConfigFiles/palp1/ARMA_PALP1_PALP1_Forecast 3.00.xml',\
          base+'ModuleConfigFiles/'+basin.lower()+'/ARMA_'+basin+'_'+aqDict[basin]+'_Forecast 1.98.xml','PALP1',basin)
    except:
      continue
    try:
      dupFile(base+'ModuleConfigFiles/palp1/MERGETS_ARMA_PALP1_PALP1 1.00.xml',\
          base+'ModuleConfigFiles/'+basin.lower()+'/MERGETS_ARMA_'+basin+'_'+aqDict[basin]+' 1.98.xml','PALP1',basin)
    except:
      continue

# find . -name ADJUSTQ_*_UpdateStates.xml | awk -F_ '{ print $2,$3 }' > ~/dev/python/basins_ids.txt
