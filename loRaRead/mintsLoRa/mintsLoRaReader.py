
import serial
import datetime
import os
import csv
import deepdish as dd
from mintsLoRa import mintsLoRaLatest as mLL
from mintsLoRa import mintsLoRaDefinitions as mLD
from getmac import get_mac_address
import time
import serial
import pynmea2
from collections import OrderedDict
import netifaces as ni


# macAddress    = mD.macAddress
dataFolder    = mLD.dataFolder
latestOff     = mLD.latestOff


def LORAWrite(sensorData,dateTime,loRaID):
    sensorName = "LORA"
    dataLength = 19
    print(len(sensorData))
    if(len(sensorData) == (dataLength)):
        sensorDictionary =  OrderedDict([
                ("dateTime"     , str(dateTime)),
                ("timestamp"          ,sensorData[0]),
                ("latitude"           ,sensorData[1]),
                ("longitude"          ,sensorData[2]),
                ("altitude"           ,sensorData[3]),
        	    ("lowPulseOccupancy"  ,sensorData[4]),
            	("concentration"      ,sensorData[5]),
                ("ratio"              ,sensorData[6]),
                ("timeSpent"          ,sensorData[7]),
        		("temperature"        ,sensorData[8]),
            	("pressure"           ,sensorData[9]),
                ("humidity"           ,sensorData[10]),
        		("nh3"        ,sensorData[11]),
            	("co"         ,sensorData[12]),
                ("no2"        ,sensorData[13]),
            	("c3h8"       ,sensorData[14]),
        		("c4h10"      ,sensorData[15]),
            	("ch4"        ,sensorData[16]),
                ("h2"         ,sensorData[17]),
            	("c2h5oh  "   ,sensorData[18]),
                ])

        sensorFinisherLora(dateTime,loRaID,sensorDictionary)


def sensorFinisherLora(dateTime,loRaID,sensorDictionary):
    #Getting Write Path
    writePath = getWritePathLoRa(loRaID,dateTime)
    exists = directoryCheck(writePath)
    writeCSV2(writePath,sensorDictionary,exists)
    print(writePath)
    if(not(latestOff)):
       mL.writeHDF5Latest(writePath,sensorDictionary,sensorName)
    print("-----------------------------------")
    print(loRaID)
    print(sensorDictionary)


def getWritePathLoRa(loRaID,dateTime):
    #Example  : MINTS_0061_OOPCN3_2019_01_04.csv
    writePath = dataFolder+"/"+loRaID+"/"+str(dateTime.year).zfill(4)  + "/" + str(dateTime.month).zfill(2)+ "/"+str(dateTime.day).zfill(2)+"/"+ "MINTS_LoRa_"+ loRaID+ "_" + str(dateTime.year).zfill(4) + "_" +str(dateTime.month).zfill(2) + "_" +str(dateTime.day).zfill(2) +".csv"
    return writePath;


def directoryCheck(outputPath):
    exists = os.path.isfile(outputPath)
    directoryIn = os.path.dirname(outputPath)
    if not os.path.exists(directoryIn):
        os.makedirs(directoryIn)
    return exists


def writeCSV2(writePath,sensorDictionary,exists):
    keys =  list(sensorDictionary.keys())
    with open(writePath, 'a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=keys)
        # print(exists)
        if(not(exists)):
            writer.writeheader()
        writer.writerow(sensorDictionary)
