__author__ = 'xuepeng'

from DSRC_USRP_Connector import dsrc_usrp_connector
from DSRC_Event import USRPEventDetector

def main():
    detector = USRPEventDetector()
    connector = dsrc_usrp_connector(port=10123,callbackInterface=detector)

if __name__ == '__main__':
    main()