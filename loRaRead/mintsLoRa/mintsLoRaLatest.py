

# import serial
# ser = serial.Serial('/dev/ttyACM3')
import serial
import datetime
import os
import csv
import deepdish as dd
import time


from mintsLoRa import mintsLoRaDefinitions as mLD

dataFolder = mLD.dataFolder


def writeHDF5Latest(writePath,sensorDictionary,sensorName):
    try:
        dd.io.save(dataFolder+sensorName+".h5", sensorDictionary)
    except:
        print("Data Conflict!")

def readHDF5LatestAll(sensorName):
    try:
        d = dd.io.load(dataFolder+sensorName+".h5")
        # print("-------------------------------------")
        # # print(sensorName)
        # # print(d)
        time.sleep(0.01)
        return d, True
    except:
        print("Data Conflict!")
        return "NaN", False

def readHDF5LatestData(sensorName,keyIn):
    try:
        d = dd.io.load(dataFolder+sensorName+".h5")
        # print("-------------------------------------")
        # print(sensorName)
        # print(d[keyIn])
        time.sleep(0.01)
        return str(d[keyIn]),True
    except:
        print("Data Conflict!")
        return {}, False
