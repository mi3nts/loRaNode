import mysql.connector
# import pandas as pd
import csv
import os
import time as t
import datetime

# Written by Daniel Kiv
# Version 0.2
# This script provides a data pipeline from a gateway database

# performs primary functions
def main():
    global df1, df2, df3, dfComb
    cnxMySQL()
    firstid = 986115
    lastid = 400

    # create headers for csv
    # with open('test.csv', 'wb') as fileOpen:
    #     file = csv.writer(fileOpen)
        # file.writerow(["DateTime", "NH3", "CO", "NO2", "C3H8", "C4H10", "CH4", "H2",
        # "C2H5OH", "LowPulseOccupancy", "lpoRatio", "dustconc", "Temperature",
        # "Pressure", "Humidity"])
    # fileOpen.close()
    dataIn(firstid, lastid)
    print("Connected to database.")

# forms connection to a MySQL database
def cnxMySQL():
    global cnxdb
    cnxdb = mysql.connector.connect(user='root',
                                password='root',
                                host='127.0.0.1',
                                database='lora_web')

# ingest from database to line
def dataIn(firstid, lastid):
    global cleanResultComb

    while True:
        crs = cnxdb.cursor(buffered = True)
        query = ("SELECT time, data FROM mergedframes WHERE id BETWEEN {:d} AND {:d}")
        queryLast = ("SELECT id FROM mergedframes ORDER BY id DESC LIMIT 1")

        # find most recent record at time of access based on id
        crs.execute(queryLast)
        for (id) in crs:
            queryLastResult = "{}".format(id)
        lastid = query2num(queryLastResult)

        crs.execute(query.format(firstid, lastid))
        for (time, data) in crs:
            queryResult = hex2char(data).split(',')
            print(time)
            # print(queryResult)
            cleanResult = [float(entry) for entry in queryResult[2:]]


            # cleanResult = queryResult

            # cleanResult1 = cleanResult
            # if cleanResult[0] == 1:
            #     cleanResult1 = cleanResult[1:]
            #     cleanResultComb = time
            #     cleanResultComb.append(cleanResult1)
            #     break
            # if cleanResult[0] == 2:
            #     cleanResult2 = cleanResult[1:]
            #     cleanResultComb = cleanResult1.append(cleanResult2)

            # converts the strings to floats and preserves precision
        #     try:
        #         # float(element)
        #         # cleanResult = parseData(queryResult)
        #
        #         print(cleanResult)
        #         # write2csv('test.csv', cleanResult, time)
        #
        #         # queryResult = "{},{}".format(time, hex2char(data).split(','))
        #         # print("{},{}".format(time, hex2char(data).split(',')))
        #     except ValueError:
        #         print("Not possible to convert to float")
        #
        # # print("Checking for update --------------------------")
        #
        # # wait for update
        # print(lastid)
        # while newRecord(lastid) == False:
        #     lk = 0
        #     # print("Rechecking for update ----------------")
        #     # t.sleep(1)
        #
        # # print("Performing update ----------------------")
        # firstid = lastid + 1
    crs.close()

def newRecord(lastid):
    query = ("SELECT id FROM mergedframes WHERE id={:d}")
    recentcrs = cnxdb.cursor(buffered = True)

    # check 1 record after the most recently evaluated row
    check = recentcrs.execute(query.format(lastid + 1))
    # print(recentcrs.rowcount)

def makeRow(dateTime, data):
    dataOut    = sensorData.split(':')
    sensorName = "MGS001"
    dataLength = 8
    if(len(dataOut) == (dataLength +1)):
        sensorDictionary =  OrderedDict([
                ("dateTime"   , str(dateTime)),
                ("nh3"        ,dataOut[0]),
                ("co"         ,dataOut[1]),
                ("no2"        ,dataOut[2]),
                ("c3h8"       ,dataOut[3]),
                ("c4h10"      ,dataOut[4]),
                ("ch4"        ,dataOut[5]),
                ("h2"         ,dataOut[6]),
                ("c2h5oh  "   ,dataOut[7]),
                ])
        sensorFinisher(dateTime,sensorName,sensorDictionary)

        # "DateTime", "NH3", "CO", "NO2", "C3H8", "C4H10", "CH4", "H2",
        # "C2H5OH", "LowPulseOccupancy", "lpoRatio", "dustconc", "Temperature",
        # "Pressure", "Humidity"

# convert data from hex to table values
def hex2char(hex):
    char = hex.decode('hex')
    return char

# converts a numerical database query to integer value
def query2num(queryResult):
    num = int(filter(str.isdigit, queryResult))
    return num

def write2csv(filename, row, time):
    # if row[0] == 1:
    #     df1 = pd.DataFrame(time, columns = ["DateTime"])
    #     df2 = pd.DataFrame(row[1:], columns = ["NH3", "CO", "NO2", "C3H8", "C4H10", "CH4", "H2",
    #     "C2H5OH"])
    #     dfComb = pd.concat([df1, df2])
    # if row[0] == 2:
    #     df3 = pd.DataFrame(row[1:], columns = ["LowPulseOccupancy", "lpoRatio", "dustconc", "Temperature",
    #     "Pressure", "Humidity"])
    #     dfComb = pd.concat([dfComb, df3])
    #     dfComb.to_csv(filename, index = False)

    with open(filename, 'ab') as fileOpen:
        file = csv.writer(fileOpen)
        file.writerow(row)
    fileOpen.close()

def organizeInput():
    print("organize")

# maintain numerical precision
def parseData(data):

    # print("yes")
    # print(data[1])
    for entry in data:
        if entry == 'null':
            print("wwo")
        else:
            print(entry)

if __name__ == "__main__":
    main()
