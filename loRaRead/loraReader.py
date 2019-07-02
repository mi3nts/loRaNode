
# ***************************************************************************
#  loRaReader
#   ---------------------------------
#   Written by: Daniel Kiv
#   - for -
#   Mints: Multi-scale Integrated Sensing and Simulation
#   ---------------------------------
#   Date: 1 July 2019
#   ---------------------------------
#   This module is written for a Mints sensor Node with LoRa Technology -
#   This script provides a data pipeline from a gateway database
#   --------------------------------------------------------------------------
#   https://github.com/mi3nts
#   http://utdmints.info/
#  ***************************************************************************


import mysql.connector
import csv
import os
import errno
import time as t
import datetime
import sys
from collections import OrderedDict

def main():
    global gatewayAddr
    global sensorDataBuffer

    # in case of crash, creates record of last entry
    recordSave = 'record.txt'
    sensorDataBuffer = OrderedDict()
    # enter gateway ID here, which is the MAC address
    gatewayAddr = 'e80688cf9052'.lower()

    # connects to the MySQL server
    cnxMySQL()
    print("Connected to database.")

    # performs the record save feature
    if os.path.isfile(recordSave):
        fileOpen = open(recordSave, "r")
        if fileOpen.mode == 'r':
            try:
                firstid = int(fileOpen.read())
            except ValueError:
                firstid = 0
            lastid = firstid + 1
    else:
        firstid = 0
        lastid = 1

    # begin data aggregation to csv
    print("Beginning data collection.")
    dataIn(firstid, lastid)

# forms connection to a MySQL database
def cnxMySQL():
    # for data frames
    global cnxdb
    cnxdb = mysql.connector.connect(user='XXXX',
                                password='XXXX',
                                host='127.0.0.1',
                                database='lora_web')

# ingest from database to line
def dataIn(firstid, lastid):
    while True:
        crs       = cnxdb.cursor(buffered = True)
        query     = ("SELECT mote,time,data FROM mergedframes WHERE id BETWEEN {:d} AND {:d}")
        queryLast = ("SELECT id FROM mergedframes ORDER BY id DESC LIMIT 1")

        # find most recent record at time of access based on id
        crs.execute(queryLast)
        for (id) in crs:
            queryLastResult = "{}".format(id)
        lastid = query2num(queryLastResult)

        # parses the entries and conglomerates packets into full data frame
        crs.execute(query.format(firstid, lastid))
        for (mote, time, data) in crs:
            queryResult = data.decode('hex').split(',')
            hexid = hex(mote).lstrip("0x").rstrip("L")
            sensorParse(hexid, time, queryResult)
        # print("Checking for update --------------------------")
        # wait for update
        # print(lastid)
        while newRecord(lastid) == False:
            lk = 0
            # print("Rechecking for update ----------------")
            # t.sleep(1)
        # print("Performing update ----------------------")
        firstid = lastid + 1
        with open('record.txt', 'w') as fileOpen:
            fileOpen.write(str(lastid))

def newRecord(lastid):
    query = ("SELECT id FROM mergedframes WHERE id={:d}")
    recentcrs = cnxdb.cursor(buffered = True)

    # check 1 record after the most recently evaluated row
    check = recentcrs.execute(query.format(lastid + 1))

def makeData(sensData, id, dateTime):
    sensDict                = OrderedDict()
    # part 1 metadata and gas
    sensDict['dateTime']    = str(dateTime)
    sensDict['id']          = id
    sensDict['NH3']         = sensData[0]
    sensDict['CO']          = sensData[1]
    sensDict['NO2']         = sensData[2]
    sensDict['C3H8']        = sensData[3]
    sensDict['C4H10']       = sensData[4]
    sensDict['CH4']         = sensData[5]
    sensDict['H2']          = sensData[6]
    sensDict['C2H5OH']      = sensData[7]
    # part 2 particulate information
    sensDict['P1_lpo']      = sensData[8]
    sensDict['P1_ratio']    = sensData[9]
    sensDict['P1_conc']     = sensData[10]
    sensDict['P2_lpo']      = sensData[11]
    sensDict['P2_ratio']    = sensData[12]
    sensDict['P2_conc']     = sensData[13]
    # part 3 conditions and gps
    sensDict['Temperature'] = sensData[14]
    sensDict['Pressure']    = sensData[15]
    sensDict['Humidity']    = sensData[16]
    sensDict['gpsTime']     = sensData[17]
    sensDict['Latitude']    = sensData[18]
    sensDict['Longitude']   = sensData[19]

    if not id == '475b41f200350016':
        # part 4 battery information
        sensDict['shuntVoltageBat'] = sensData[20]
        sensDict['busVoltageBat']   = sensData[21]
        sensDict['currentBat']      = sensData[22]
        sensDict['shuntVoltageSol'] = sensData[23]
        sensDict['busVoltageSol']   = sensData[24]
        sensDict['currentSol']      = sensData[25]

    return sensDict

def sensorParse(id, dateTime, sensData):
    try:
        sensorDataBuffer['{}_flag'.format(id)]
    except KeyError as e:
        sensorDataBuffer['{}_flag'.format(id)] = 0
        return
    if sensData[0] == '1':
        sensorDataBuffer['{}_dateTime'.format(id)] = str(dateTime)
        sensorDataBuffer['{}_id'.format(id)] = id
        sensorDataBuffer['{}_1'.format(id)] = sensData[1:]
        sensorDataBuffer['{}_flag'.format(id)] = 1

    if sensData[0] == '2':
        if sensorDataBuffer['{}_flag'.format(id)] != 1:
            return
        sensorDataBuffer['{}_2'.format(id)] = sensorDataBuffer['{}_1'.format(id)] + sensData[1:]
        sensorDataBuffer['{}_flag'.format(id)] = 2

    if sensData[0] == '3':
        if sensorDataBuffer['{}_flag'.format(id)] != 2:
            return
        sensorDataBuffer['{}_3'.format(id)] = sensorDataBuffer['{}_2'.format(id)] + sensData[1:]
        sensorDataBuffer['{}_flag'.format(id)] = 3
        # catch the non-battery sensor
        if id == '475b41f200350016':
            # Merge dataframe and print
            sensorDataFrame = sensorDataBuffer['{}_3'.format(id)]
            print(sensorDataFrame)
            sensorDataFrame = makeData(sensorDataFrame, id, sensorDataBuffer['{}_dateTime'.format(id)])
            print('Node {} packet received at {}.'.format(id, sensorDataBuffer['{}_dateTime'.format(id)]))
            try:
                write2csv(sensorDataFrame)
                sensorDataFrame = None
                sensorDataBuffer['{}_flag'.format(id)] = 0
            except ValueError:
                print("Not possible to convert!")
            return sensorDataFrame

    elif sensData[0] == '4':
        if sensorDataBuffer['{}_flag'.format(id)] != 3:
            return
        sensorDataBuffer['{}_4'.format(id)] = sensorDataBuffer['{}_3'.format(id)] + sensData[1:]
        sensorDataBuffer['{}_flag'.format(id)] = 4

        # Merge dataframe and print
        sensorDataFrame = sensorDataBuffer['{}_4'.format(id)]
        print(sensorDataFrame)
        sensorDataFrame = makeData(sensorDataFrame, id, sensorDataBuffer['{}_dateTime'.format(id)])
        print('Node {} packet received at {}.'.format(id, sensorDataBuffer['{}_dateTime'.format(id)]))
        try:
            write2csv(sensorDataFrame)
            sensorDataFrame = None
            sensorDataBuffer['{}_flag'.format(id)] = 0
        except ValueError:
            print("Not possible to convert!")
        return sensorDataFrame

# converts a numerical database query to integer value
def query2num(queryResult):
    num = int(filter(str.isdigit, queryResult))
    return num

def write2csv(row):
    fileDirectory = 'loraNet/{}/{}/'.format(gatewayAddr, row['id'])
    filename = '{}{}_{}.csv'.format(fileDirectory, row['id'], row['dateTime'][:10])

    if not os.path.exists(fileDirectory):
        try:
            os.makedirs(fileDirectory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    with open(filename, 'ab') as fileOpen:
        if os.stat(filename).st_size == 0:
            csv_columns = ['dateTime', 'id', 'NH3', 'CO', 'NO2', 'C3H8', 'C4H10', 'CH4', 'H2',
                'C2H5OH', 'P1_lpo', 'P1_ratio', 'P1_conc', 'P2_lpo', 'P2_ratio', 'P2_conc',
                'Temperature', 'Pressure', 'Humidity','gpsTime', 'Latitude','Longitude',
                'shuntVoltageBat', 'busVoltageBat', 'currentBat',
                'shuntVoltageSol', 'busVoltageSol', 'currentSol']
            writer = csv.DictWriter(fileOpen, fieldnames = csv_columns)
            writer.writeheader()
        writer = csv.DictWriter(fileOpen, row.keys())
        writer.writerow(row)
    fileOpen.close()

if __name__ == "__main__":
    main()
