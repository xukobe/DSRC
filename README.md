# DSRC Documentation
VSmart testbed is designed for DSRC experiments in both indoor and outdoor scenarios. It utilizes Software Defined Radios (SDR), laptops and iRobot Create to emulate the real-world traffic. The VSmart utilizes the modified code of the following project:
pycreate: https://github.com/mgobryan/pycreate
gr-ieee802-11: https://github.com/bastibl/gr-ieee802-11

## Installation
The VSmart testbed is developed under Linux (Ubuntu 14.04). The deployment of VSmart has the following dependencies:

### GNU Radio and UHD:
The easiest way to install the GNU Radio and UHD is use the following script:
http://www.sbrac.org/files/build-gnuradio

### gr-ieee802-11 
VSmart utilize open source project IEEE 802.11 a/g/p transceiver by bastibl
The installation instruction is on the page: https://github.com/bastibl/gr-ieee802-11

#### Installation of VSmart
The VSmart can be installed by the following instructions:
git clone https://github.com/xukobe/VSmart.git
cd VSmart
sudo ./install

To run the VSmart:
sudo VSmart

