__author__ = 'xuepeng'

from DSRC_Messager_Module.dsrc_messager import socket_server,socket_client

class connector_Interface:
    """
    Interface for USRP connector.
    """
    def msg_received(self,msg):
        """
        Things to do when message received from USRP.
        :param msg: message received from USRP
        """
        raise NotImplementedError( "connector interface is not implemented." )

class dsrc_usrp_connector:
    """
    Connector between USRP and controller
    """
    def __init__(self, port=10123, callbackInterface=None):
        """
        :param port: Port for server socket
        :param callbackInterface: callback object
        """
        self.port = port
        self.callback = callbackInterface
        self.client = []
        self.server = socket_server(self._connected_callback,self.port)
        self.server.start()

    def _connected_callback(self,incoming_socket):
        client = socket_client(self.callback.msg_received, incoming_socket)
        client.start()
        self.client.append(client)

    def sendToUSRP(self,msg):
        for i in range(len(self.client)):
            self.client[i].send(msg)

    def stopself(self):
        for i in range(len(self.client)):
            self.client[i].stopself()
        self.server.stopself()