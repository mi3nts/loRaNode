# LoRa Node 
![LoraNode](https://github.com/mi3nts/loraNode/blob/master/res/lora.png)
</br>
</br>

## A Guide to Using the Low-Cost Sensor Network
written by, Daniel Kiv (github: marchfori)

### Basics

1. Sensors Nodes (arduino)

### Sensors
2. Physical Characteristics
-Dimensions
-Weight
-Power Requirements

### Gateway Node (Raspberry Pi 3)
3.Useful Links

### Adjustments
4.Setting up the External Hard drive
5.Connecting to an external network
6.Adjustments to the PPD42NS

### Basics

The purpose of this documentation is to show how to start up and maintain the network
of low-cost sensors that will begin deployment in the North Texas area. With the increase
in particulate emissions over the years, there is a need to be aware of the implications
of toxic airbourne particles. These can have negative health outcomes on the population.
Currently, air quality sensors are spaced far and wide from each other collecting data at 
large time frames. They can also be often expensive. This project seeks to solve these 
issues and presents a low cost sensor network using a novel network communication known as
LoRaWAN, a set of arduinos, and a gateway linux based Raspbery Pi 3. Combined with the 
calibration technique using machine learning algorithms, this sensor network can effectively
provide the public with an accurate representation of air quality.

#### Sensor Nodes (arduino)
- Seeeduino w/ LoRaWAN and GPS capabilities

Uses a set of 10 arduino based nodes and 1 gateway Raspberry Pi 3.

- [Seeeduino LoRaWAN with GPS](https://www.google.com/search?q=Seeeduino+LoRaWAN+with+GPS&rlz=1CDGOYI_enUS696US696&hl=en-US&sourceid=chrome-mobile&ie=UTF-8)
- [Grove Dust Sensor](https://www.seeedstudio.com/Grove-Dust-Sensor-PPD42NS.html)
- [Grove Barometer Sensor: I2C protocol](https://www.seeedstudio.com/Grove-Barometer-Sensor-BMP28-p-2652.html)
- [Raspberry Pi 3 Model B](https://www.amazon.com/Raspberry-Pi-Model-Motherboard-Element/dp/B07CTF2GWR/ref=asc_df_B07CTF2GWR/?tag=hyprod-20&linkCode=df0&hvadid=319185484784&hvpos=1o1&hvnetw=g&hvrand=5893904611042441124&hvpone=&hvptwo=&hvqmt=&hvdev=t&hvdvcmdl=&hvlocint=&hvlocphy=9026945&hvtargid=pla-535390958326&psc=1&tag=&ref=&adgrpid=63609080556&hvpone=&hvptwo=&hvadid=319185484784&hvpos=1o1&hvnetw=g&hvrand=5893904611042441124&hvqmt=&hvdev=t&hvdvcmdl=&hvlocint=&hvlocphy=9026945&hvtargid=pla-535390958326)
- [RHFoM301 module: serves as the communication bridge for the Raspberry Pi 3](http://www.risinghf.com/#/product-details?product_id=6&lang=en%2F)
- [BME280 w/ Temperature, Pressure, & Humidity Readings](https://www.adafruit.com/product/2652?gclid=CJvFq_q63-ICFUi1wAod5RsHjw)
- [Grove Multichannel Gas Sensor](https://www.arrow.com/en/products/101020088/seeed-technology-limited?gclid=CKqP4Za73-ICFdm1wAodyJsA8g) 

## Sensors
These sensors are attached to the device

| Sensor Name | Description | Interface |
| ---- | ---- | ---- |
| Grove Dust Sensor | Measures low pulse occupancy time as a correlate to particular matter. | Digital Pin |
| Grove Barometer | Measures temperature (Celcius) and atmospheric pressure | I2C |
| Grove Multichannel Gas Sensor | Measures Carbon Monoxide, Nitrogen Dioxide, Ethanol, Hydrogen, Ammonia, Methane, Propane,and Isobutane in ppm. | I2C |

#### Physical Characteristics

**Dimensions** (L x W x H)
Seeduino device dimensions with add-ons: 65mm x 55mm x 45mm.
Gateway device dimensions (without antenna): 85mm x 55mm x 30mm.
Seeeduino device enclosure: 120mm x 120mm x 275 mm

**Weight**
Seeeduino device weight with add-ons: 0.25kg
Gateway device weight: 0.20kg
Seeeduino device with enclosure: 0.60kg

**Power Requirements**
Average power consumption on standby: 1.1W
Average power consumption during transmission 1.2W
Voltage usage: 4.91V
Current usage: 0.20A

- [3.7V Lithium Ion Battery](https://www.amazon.com/Lithium-Battery-Connector-LP803860-2000mAh/dp/B07CZFMFB3)
- [3W SEEED Solar Panel](https://cpc.farnell.com/seeed-studio/313070001/solar-panel-138x160-3w/dp/MK00376)

### Gateway Node (Raspberry Pi 3)

Used to collect signal broadcasts from surrounding nodes.

#### Useful links

[Here](https://github.com/mi3nts/loRaNode) is the link to the sensor node's software. 
If there are issues please contact me.

There is also software that synchornizes and creates the formatting for the data 
aggregation on the gateway node.

### Adjustments

#### Setting up the External hard drive

- Checking if the HD is connected 
```
sudo lshw -class disk -short 
```
Be sure the hard drive you want to use is formatted in the **_ext4_** filesystem. 

- Mounting the HD
```
sudo su
mount /dev/sda1 /mnt
```

- Transfer your root partition to the new drive:
```
sudo rsync -axv / /mnt
cp /boot/cmdline.txt /boot/cmdline.txt.bak
nano /boot/cmdline.txt

```
- Change the lines as follows:

```
dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=/dev/sda1 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait rootdelay=5
```
- Chnaging the Boot Order 
```
nano /mnt/etc/fstab
```
Then add the following line:
```
/dev/sda1       /               ext4    defaults,noatime  0       1
```
Make sure to get the spacing right 

Comment the SD Boot 
```
#/dev/mmcblk0p7  /               ext4    defaults,noatime  0       1

```

Then restart the system.

#### Connecting to an external network

```
sudo nano
/etcwpa_supplicant/wpa_supplicant.conf

   network={
    ssid="Test Wifi Network"
    psk="SecretPassWord"
    }
    
 sudo systemctl status pktfwd
 sudo systemctl enable pktfwd
 sudo systemctl restart pktfwd
 
 **mysql -u root -p**
 ```
 
#### Additional Modifications made to the PPD42NS
##### PPD42NS
<img src="https://www.shinyei.co.jp/stc/eng/images/pic_PPD42_L.jpg"
     alt="shinyei"
     style="float: left; margin-right: 10px;" />
     <br/>
     
The pins are labeled as '**thresh**', '**P1**', '**+5v**', '**P2**, and '**grnd**'  going from left to write on the figure given above. 

 - Addition of a 10K resisitor between the threshold pin and ground:
 A good read on the mechanism followed is given [here](http://takingspace.org/wp-content/uploads/ShinyeiPPD42NS_Deconstruction_TracyAllen.pdf).
[useful](https://www.shadowandy.net/2015/05/arduino-dust-sensor.htm)
 -  Capable of dual output
 
 ##### color code
 
 - p1: green - D3
 - p2: blue - D4
    
