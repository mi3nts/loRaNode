
/* 
 * Written by Daniel Kiv
 * Version 082919
 * 
 * Acknowledgements
 * Adam, Nora, Shrey
 */

#include <Seeed_BME280.h>
#include <Wire.h>
#include <LoRaWan.h>
#include "TinyGPS++.h"
#include <avr/dtostrf.h>
#include "MutichannelGasSensor.h"
#include <SeeedOLED.h>
#include <Adafruit_INA219.h>
#include "SparkFun_SCD30_Arduino_Library.h"
#include <Adafruit_SleepyDog.h>
#include <EnergySaving.h>

// barometer initializations
double pressure;
BME280 baro;

EnergySaving nrgSave;

Adafruit_INA219 inaSol(0x41);
Adafruit_INA219 inaBat(0x40);

//initialization of the SCD30 CO2 Sensor
SCD30 airSensor;

// initializations for dust sensor (global)
int pinP1 = 8;
int pinP2 = 7;

#define USE_GPS 1
#ifdef USE_GPS
#include "TinyGPS++.h"
TinyGPSPlus gps;
#endif

char buffer[256];
char id[10];

int DONEPIN = A4;

void setup() {

  SerialUSB.println("System booting...");
  Wire.begin();
  oledInit();
  SeeedOled.putString("Booting...");
  delay(1000);
  Serial.begin(9600);  // for gps readings
  Serial1.begin(9600);
  SerialUSB.begin(115200);
  lora.init();

  delay(1000);
  SeeedOled.putString("1");
  delay(1000);
  SeeedOled.putString("2");
  delay(1000);
  SeeedOled.putString("Sleep start...");
  delay(1000);
  pinMode(DONEPIN, OUTPUT);
  digitalWrite(DONEPIN, LOW);

  delay(1000);

  // do sleep
  while (1) {
    digitalWrite(DONEPIN, HIGH);
    delay(1);
    digitalWrite(DONEPIN, LOW);
    delay(1);
  }

  SeeedOled.putString("Sleep end...");
  
//  gpsInit();

  // sensor initializations
  dustInit();
  airSensor.begin(); 
  airSensor.setMeasurementInterval(30);
  if(!baro.init()) {
    SerialUSB.println("Device error!");
  }
  gasInit();
  inaBat.begin();
  inaSol.begin();
  
//  starttime = millis();//get the current time for dust sensor

  // LoRaWAN initializations
  memset(buffer, 0, 256);
//  lora.getVersion(buffer, 256, 1);
  lora.getId(buffer, 256, 1);
  SerialUSB.print(buffer);

  readID(id, buffer);

  lora.setKey("2B7E151628AED2A6ABF7158809CF4F3C", "2B7E151628AED2A6ABF7158809CF4F3C", NULL);

  lora.setDeciveMode(LWABP);
  lora.setDataRate(DR3, US915HYBRID);

  lora.setChannel(0, 902.3);
  lora.setChannel(1, 902.5);
  lora.setChannel(2, 902.7);
//  lora.setChannel(3, 902.9, DR0, DR3);
//  lora.setChannel(4, 903.1, DR0, DR3);
//  lora.setChannel(5, 903.3, DR0, DR3);
//  lora.setChannel(6, 903.5, DR0, DR3);
//  lora.setChannel(7, 903.7, DR0, DR3);

  lora.setReceiceWindowFirst(0, 902.3);
  lora.setReceiceWindowSecond(923.3, DR3);
  lora.setAdaptiveDataRate(false);

  lora.setDutyCycle(false);
  lora.setJoinDutyCycle(false);

  lora.setPower(14);

  SerialUSB.println("System booted!");
}

void loop() {
  bool result1, result2, result3, result4, result5 = false;
  char msg1[180] = "1,";
  char msg2[180] = "2,";
  char msg3[180] = "3,";
  char msg4[180] = "4,";
  char msg5[180] = "5,";
  char cat[15];
  char com[2] = ",";

//  SerialUSB.println(millis());
  SeeedOled.clearDisplay();

  lowPower();
  
  // collect data
  readPPD42NSMintsDuo(msg2, 15);
  double temperature = baro.getTemperature();
  double pressure = baro.getPressure();
  double humidity = baro.getHumidity();
  multiChan(msg1); // this function collects AND builds message
  readElectric(msg4);
  readCO2(msg5);
  
  // build message with correct precision
  append(temperature, msg3, 2);
  append(pressure, msg3, 2);
  append(humidity, msg3, 0);
  doGPS(msg3); // collect gps and append after
  
  result1 = lora.transferPacket(msg1);
  SerialUSB.println(msg1);
  check(result1);
  result2 = lora.transferPacket(msg2);
  SerialUSB.println(msg2);
  check(result2);
  result3 = lora.transferPacket(msg3);
  SerialUSB.println(msg3);
  check(result3);
  result4 = lora.transferPacket(msg4);
  SerialUSB.println(msg4);
  check(result4);
  result5 = lora.transferPacket(msg5);
  SerialUSB.println(msg5);
  check(result5);
//  result = lora.transferPacket(data, 11);
  
//    memset(payload, '\0', 200);
}

void append(double data, char* msg, int precision) {
  char cat[15];
  char comma[2] = ",";
  
  dtostrf(data, 0, precision, cat);
  strcat(msg, cat);
  strcat(msg, comma);
}

void appendLast(double data, char* msg, int precision) {
  char cat[15];
  
  dtostrf(data, 0, precision, cat);
  strcat(msg, cat);
}

void normalPower() {
  for(unsigned char i = 7; i < 9; i ++) {
    // pinMode(i, OUTPUT);
    digitalWrite(i, HIGH);
  }
  lora.setDeviceReset();
}

void dummy(void)
{
    // do something
}


void lowPower() {
  SeeedOled.setTextXY(2,0);
  SeeedOled.putString("LWPOWER");
//  SeeedOled.setTextXY(4,0);
//  SeeedOled.putString("LWPOWER");
for(unsigned char i = 0; i < 26; i ++)      // important, set all pins to HIGH to save power
    {
        pinMode(i, OUTPUT);
        digitalWrite(i, HIGH);
    }
    digitalWrite(SDA, LOW); digitalWrite(SCL, LOW);
  for(unsigned char i = 7; i < 9; i ++) {
    pinMode(i, INPUT);
    digitalWrite(i, LOW);
  }
  lora.setDeviceLowPower();
   nrgSave.begin(WAKE_EXT_INTERRUPT, 7, dummy);    // buton on D7 to wake up the board
   nrgSave.standby();
  // begin sleep
  for(unsigned char i = 0; i < 3; i ++) {
    int sleepMS = Watchdog.sleep(5000);
    int dummy = i;
  }
}

void readID(char* id, char* buffer) {
  char comma[2] = ",";
  
  id[0] = buffer[14];
  id[1] = buffer[15];
  id[2] = buffer[17];
  id[3] = buffer[18];
  id[4] = buffer[20];
  id[5] = buffer[21];
  id[6] = buffer[23];
  id[7] = buffer[24];
  strcat(id, comma);
}

void check(bool result) {
  if(result) {
    short length;
    short rssi;
    
    memset(buffer, 0, 256);
    length = lora.receivePacket(buffer, 256, &rssi);
    SeeedOled.setTextXY(6,0);
    SeeedOled.putString("NOTICE: BRDCST!");
    if(length) {
      SerialUSB.print("Length is: ");
      SerialUSB.println(length);
      SerialUSB.print("RSSI is: ");
      SerialUSB.println(rssi);
      SerialUSB.print("Data is: ");
      for(unsigned char i = 0; i < length; i++) {
        SerialUSB.print("0x");
        SerialUSB.print(buffer[i], HEX);
        SerialUSB.print(" ");
      }
      SerialUSB.println();
    }
    delay(100);
  }
}

void doGPS(char* msg) {
  double latitude;
  double longitude;
  double dateStamp;
  double timeStamp;
  
  if (gps.location.isValid()) {
    char cat[15];
    
//    timeStamp = gps.time.value();
//    dateStamp = gps.date.value();
    latitude = gps.location.lat();
    longitude = gps.location.lng();
  
//    dtostrf(dateStamp, 0, 0, cat);
//    strcat(msg, cat);
//    append(timeStamp, msg, 0); // fix time FIRST 
    strcat(msg, "nan,");
    append(latitude, msg, 6);
    appendLast(longitude, msg, 6);
  }
  else {
    latitude = 0;
    longitude = 0;
    timeStamp = 0;
    dateStamp = 0;
    strcat(msg, "nan,nan,nan");
  }
}

void multiChan(char* msg) {
  double conc;
  
  conc = gas.measure_NH3();
  validConc(conc, msg);

  conc = gas.measure_CO();
  validConc(conc, msg);

  conc = gas.measure_NO2();
  validConc(conc, msg);

  conc = gas.measure_C3H8();
  validConc(conc, msg);

  conc = gas.measure_C4H10();
  validConc(conc, msg);

  conc = gas.measure_CH4();
  validConc(conc, msg);

  conc = gas.measure_H2();
  validConc(conc, msg);

  conc = gas.measure_C2H5OH();
  if(conc >= 0) {
      appendLast(conc, msg, 2);
    }
    else {
      strcat(msg, "nan");
    }
}

void validConc(double conc, char* msg) {
  char nan[5] = "nan,";
  
  if(conc >= 0) {
      append(conc, msg, 2);
    }
    else {
      strcat(msg, nan);
    }
}

void readCO2(char *msg){
  float co2Lvl = airSensor.getCO2();
  float co2Temp = airSensor.getTemperature();
  float co2Humd = airSensor.getHumidity();

  SerialUSB.print("CO2 Level (ppm) "); SerialUSB.println(airSensor.getCO2());
  SerialUSB.print("Temperature (C) "); SerialUSB.println(airSensor.getTemperature());
  SerialUSB.print("Humidity (%) "); SerialUSB.println(airSensor.getHumidity());

  append(co2Lvl, msg, 0);
  append(co2Temp, msg, 2);
  appendLast(co2Humd, msg, 2);
}

void readElectric(char *msg) {
  float shuntVoltageBat  = inaBat.getShuntVoltage_mV();
  float busVoltageBat    = inaBat.getBusVoltage_V();
  float currentMaBat     = inaBat.getCurrent_mA();
//  float powerMwBat      = inaBat.getPower_mW();
  float shuntVoltageSol  = inaSol.getShuntVoltage_mV();
  float busVoltageSol    = inaSol.getBusVoltage_V();
  float currentMaSol     = inaSol.getCurrent_mA();
//  float powerMwSol      = inaSol.getPower_mW();

  SerialUSB.print("Bat Bus Voltage(V) "); SerialUSB.println(inaBat.getBusVoltage_V());
  SerialUSB.print("Bat Shunt Voltage(mV) "); SerialUSB.println(inaBat.getShuntVoltage_mV());
  SerialUSB.print("Bat Current(mA) "); SerialUSB.println(inaBat.getCurrent_mA());
//  SerialUSB.print("Bat Power(mW) "); SerialUSB.println(inaBat.getPower_mW());
  SerialUSB.print("Sol Bus Voltage(V) "); SerialUSB.println(inaSol.getBusVoltage_V());
  SerialUSB.print("Sol Shunt Voltage(mV) "); SerialUSB.println(inaSol.getShuntVoltage_mV());
  SerialUSB.print("Sol Current(mA) "); SerialUSB.println(inaSol.getCurrent_mA());
//  SerialUSB.print("Sol Power(mW) "); SerialUSB.println(inaSol.getPower_mW());

  append(shuntVoltageBat, msg, 2);
  append(busVoltageBat, msg, 2);
  append(currentMaBat, msg, 2);
//  append(powerMwBat, msg, 2);
  append(shuntVoltageSol, msg, 2);
  append(busVoltageSol, msg, 2);
  appendLast(currentMaSol, msg, 2);
//  append(powerMwSol, msg, 2);
}

void readPPD42NSMintsDuo(char *msg, uint8_t sampleTimeSeconds) {
    unsigned long starttime;
    unsigned long sampletime_ms = sampleTimeSeconds*1000;

    float ratioPmMid   = 0;
    float ratioPm10  = 0;
    
    float concentrationPmMid = 0;
    float concentrationPm2_5 = 0;
    float concentrationPm10  = 0;

    boolean pmMidPinValue = HIGH;
    boolean pm10PinValue = HIGH;
    
    boolean pmMidReading  = false;
    boolean pm10Reading  = false;
    
    unsigned long LPOPmMid  =  0;
    unsigned long LPOPm10 =  0;
    
    unsigned long readingTimePmMid   =  0;
    unsigned long readingTimePm10  =  0;
    
    starttime = millis();

    while ((millis() - starttime) < sampletime_ms)
    {
       pmMidPinValue =  digitalRead(pinP1);
       pm10PinValue  =  digitalRead(pinP2);

//      For Mid Range Readings 
       if(pmMidPinValue == LOW && pmMidReading == false) {
          pmMidReading = true;
          readingTimePmMid = micros();
       }
      
       if(pmMidPinValue == HIGH && pmMidReading == true) {
          LPOPmMid = LPOPmMid + (micros() - readingTimePmMid);
          pmMidReading = false;
       }

//      For PM 10 Readings
       if(pm10PinValue == LOW && pm10Reading == false) {
          pm10Reading = true;
          readingTimePm10 = micros();
       }
      
       if(pm10PinValue == HIGH && pm10Reading == true) {
         LPOPm10 = LPOPm10 + (micros() - readingTimePm10);
         pm10Reading = false;
       }
   
    }// WHILE LOOP END 
    
    ratioPmMid  = LPOPmMid/(sampletime_ms*10.0);
    ratioPm10   = LPOPm10/(sampletime_ms*10.0);

    concentrationPmMid = 1.1*pow(ratioPmMid,3)-3.8*pow(ratioPmMid,2)+520*ratioPmMid+0.62; // using spec sheet curve
    concentrationPm10  = 1.1*pow(ratioPm10,3)-3.8*pow(ratioPm10,2)+520*ratioPm10+0.62; // using spec sheet curve
    concentrationPm2_5 = concentrationPm10 - concentrationPmMid ;

    append(LPOPmMid, msg, 0);
    append(ratioPmMid, msg, 2);
    append(concentrationPmMid, msg, 2);
    append(LPOPm10, msg, 0);
    append(ratioPm10, msg, 2);
    appendLast(concentrationPm10, msg, 2);
    
    SerialUSB.print("lpoMID; "); SerialUSB.println(LPOPmMid);
    SerialUSB.print("ratMid; "); SerialUSB.println(ratioPmMid);
    SerialUSB.print("cPmMid; "); SerialUSB.println(concentrationPmMid);
    SerialUSB.print("lpoPM10; "); SerialUSB.println(LPOPm10);
    SerialUSB.print("ratPM10; "); SerialUSB.println(ratioPm10);
    SerialUSB.print("cPm10; "); SerialUSB.println(concentrationPm10);
    SerialUSB.print("cPm25; "); SerialUSB.println(concentrationPm2_5);

}

void dustInit() {
  pinMode(pinP1,INPUT); // pin from global
  pinMode(pinP2,INPUT);
}

void oledInit() {
  SeeedOled.init();
  SeeedOled.clearDisplay();
  SeeedOled.setNormalDisplay();
  SeeedOled.setPageMode(); 
  SeeedOled.setTextXY(0,0);
}

void gasInit() {
  gas.begin(0x04);
  gas.powerOn();
}

void gpsInit() {
     char c;
#ifdef USE_GPS
   bool locked;
#endif
  
  #ifdef USE_GPS
    Serial.begin(9600);     // open the GPS
    locked = false;

    while (!gps.location.isValid()) {
      while (Serial.available() > 0) {
        if (gps.encode(c=Serial.read())) {
//          displayInfo();
          if (gps.location.isValid()) {
//            locked = true;
            break;
          }
        }
//        SerialUSB.print(c);
      }

//      if (locked)
//        break;

      if (millis() > 15000 && gps.charsProcessed() < 10)
      {
        SerialUSB.println(F("No GPS detected: check wiring."));
        SerialUSB.println(gps.charsProcessed());
        while(true);
      } 
      else if (millis() > 20000) {
        SerialUSB.println(F("Not able to get a fix in alloted time."));     
        break;
      }
    }
#endif
}
