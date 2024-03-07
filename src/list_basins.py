#!/awips2/python/bin/python

import xml.etree.ElementTree as ET

base = '/awips/chps_share/sa/schade/ohrfc_sa/Config/'

lsTree = ET.parse(base+'RegionConfigFiles/LocationSets.xml')

idDict = {}
with open('basins_ids.txt','r') as text:
  for line in text:
    v,k = line.split()
    idDict[k] = v


def dupFile(inFile,outFile,strOut,strIn):
  fin = open(inFile,'r')
  filedata = fin.read()
  fin.close()
  
  newdata = filedata.replace(strOut,strIn)
  
  fout = open(outFile,'w')
  fout.write(newdata)
  fout.close()



    
for set in lsTree.findall(".//{http://www.wldelft.nl/fews}locationSet[@id='Forecast_Gages']/{http://www.wldelft.nl/fews}locationSetId"):
  [tag, junk, basin] = set.text.split("_")
  print basin
  findText = ".//{http://www.wldelft.nl/fews}locationSet[@id='"+set.text+"']/{http://www.wldelft.nl/fews}locationId"
  for set2 in lsTree.findall(findText):
    loc = set2.text
    print basin+"->"+loc    
    try:
      dupFile(base+'ModuleConfigFiles/palp1/ARMA_PALP1_PALP1_Forecast 3.00.xml',\
          base+'ModuleConfigFiles/'+idDict[loc].lower()+'/ARMA_'+idDict[loc]+'_'+loc+'_Forecast_EXP.xml','PALP1',loc)
    except:
      continue
    try:
      dupFile(base+'ModuleConfigFiles/palp1/MERGETS_ARMA_PALP1_PALP1.xml',\
          base+'ModuleConfigFiles/'+idDict[loc].lower()+'/MERGETS_ARMA_'+idDict[loc]+'_'+loc+'_EXP.xml','PALP1',loc)
    except:
      continue

# find . -name ADJUSTQ_*_UpdateStates.xml | awk -F_ '{ print $2,$3 }' > ~/dev/python/basins_ids.txt
