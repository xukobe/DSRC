__author__ = 'xuepeng'

from DSRC_Messager_Module.dsrc_messager import socket_server,socket_client
from DSRC_USRP_Connector import connector_Interface

class event:
    def __init__(self):
        self.cmd = ''
        self.option = ''

    def set_cmd(self, cmd):
        self.cmd = cmd

    def set_option(self,option):
        self.option = option

class eventGenerator:
    def __init__(self):
        self.listener = None

    def setListener(self, listener):
        self.listener = listener

class eventListener:
    def usrpEventReceived(self,event):
        raise NotImplementedError( "USRP event listener is not implemented." )

    def irobotEventReceived(self,event):
        raise NotImplementedError("iRobot event listener is not implemented")

class USRPEventDetector(eventGenerator, connector_Interface):
    def __init__(self):
        pass

    def msg_received(self,msg):
        print msg