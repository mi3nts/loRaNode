after first boot of the rasberi pi 
us: rxhf
pw: risinghf

# Expand SD
sudo raspi-config

# install Dependancies
```
sudo apt-get install screen
sudo apt-get install python3-pip
sudo pip3 install getmac
sudo pip3 install pyserial
sudo pip3 install netifaces
sudo pip3 install pynmea2
```
# Install crontab with Nano 
export VISUAL=nano; crontab -e
