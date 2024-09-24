# ProjectP
Repo for code for a moving base/rover, RTK position and heading sensor.
On a RPi4, there are 5 usable serial ports, most HATs use GPIO 14,15 which is AMA0.
In this project, this is reserved, it will be connected to a ZIHATEC RS485 HAT.
This project was tested using Ardusimple ZED-9P based boards.
The configuration of these boards is stored under the directory UBXZED9P.

### Testing the code
The code here is a combination of functions from several different projects. 
Unit testing is done in the original repos where this code was extracted from.
For the moment, I have no plans to add unit tests here.
As an integration test, the data from the three sources was read by a PC using OpenCPN 5.6.

### Wiring
![img.png](img.png)


 
## NMEA
The NMEA code in this project is based on IOTECH/NMEA.
There are two executables, one for the 
- Base on multicast port 239.1.1.1:5001
- Heading sensor on multicast port 239.1.1.1:5002

They output on different multicast ports, so they can both work simultaneously.

## UBX
The UBlox code in this project is based on IOTECH/UBX.
Its output is to another multicast port 239.1.1.1:5003

## RTKLIB
This project also uses a compiled version of str2str from RTKLIB.
This provides RTCM from a CORS station.

Conserving WAN bandwidth to the boat, str2str also provides a TCPIP NTRIP server to other local devices.

See str2str.sh for connection details.


