import mysql.connector
import csv
import os
import datetime

def main():
#  while True:
#    a = 5
#    print("a is now 5")
#  end

  cnxMySQL() 
  print("Connected to database.")
  dataIn()

# forms connection to a MySQL database
def cnxMySQL():
  cnxdb = mysql.connector.connect(user='root', 
                                password='root',
                                host='127.0.0.1',
                                database='lora_web')

# ingest from database to line
def dataIn():


# 
def dataOut():

# convert data from hex to table values
def hex2val(hex):
  val = int(hex, 16)
  return val

def write2CSV():

def organizeInput():

def parseData():




if __name__ == "__main__":
  main()
