__author__ = 'xuepeng'

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