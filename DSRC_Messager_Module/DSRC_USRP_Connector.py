__author__ = 'xuepeng'

from DSRC_Messager_Module.DSRC_Messenger import SocketServer, SocketClient

class ConnectorInterface:
    """
    Interface for USRP connector.
    """
    def msg_received(self, msg):
        """
        Things to do when message received from USRP.
        :param msg: message received from USRP
        """
        raise NotImplementedError( "connector interface is not implemented." )

class DsrcUSRPConnector:
    """
    Connector between USRP and controller
    """
    def __init__(self, ip="127.0.0.1", port=10123, callbackInterface=None):
        """
        :param ip: IP to connect
        :param port: Port for server socket
        :param callbackInterface: callback object
        :type port: int
        :type callbackInterface: ConnectorInterface
        """
        self.IP = ip
        self.port = port
        self.callback = callbackInterface
        self.client = SocketClient(self._recv_callback)
        print "Connecting to " + self.IP + ":" + str(self.port) + "..."
        self.client.connect("127.0.0.1", self.port)
        print "Connected!"
        self.client.start()

    # def _connected_callback(self, incoming_socket):
    #     client = SocketClient(self._recv_callback, incoming_socket)
    #     client.start()
    #     print "A USRP module is connecting..."
    #     self.client.append(client)

    def _recv_callback(self, msg):
        if self.callback:
            self.callback.msg_received(msg)

    def register_listener(self, callback_interface):
        """
        :param callback_interface: The listener to monitoring the received message
        :type callback_interface: connector_Interface
        """
        self.callback = callback_interface

    def send_to_USRP(self, msg):
        """
        :type msg: str
        """
        try:
            self.client.send(msg)
        except Exception, e:
            print self.IP + ":" + self.port + " connection refused!"

    def stop_self(self):
        self.client.stop_self()