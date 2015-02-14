__author__ = 'xuepeng'

import ConfigParser
import sys
import os


event_module = None
sender_module = None
receiver_module = None


def load_plugin():
    global event_module
    global sender_module
    global receiver_module
    # Initialize plugins
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser.SafeConfigParser()
    config_ini_path = ''.join([dir_path, "/config.ini"])
    print config_ini_path

    config.read(config_ini_path)


    try:
        path_event = config.get('CustomizedEvent', 'DirectoryPath')
        file_event = config.get('CustomizedEvent', 'FileName')
        event_module_name = config.get('CustomizedEvent', 'ModuleName')
        if path_event:
            if path_event == "./":
                if dir_path not in sys.path:
                    sys.path.append(''.join([dir_path, '/']))
            else:
                if os.path.exists(path_event + file_event):
                    if path_event not in sys.path:
                        sys.path.append(path_event)
                else:
                    raise Exception("Event Plugin path error!")
        if event_module_name:
            event_module = __import__(event_module_name)
    except Exception, e:
        print e

    if event_module:
        print event_module_name

    try:
        path_sender = config.get('CustomizedSender', 'DirectoryPath')
        file_sender = config.get('CustomizedSender', 'FileName')
        sender_module_name = config.get('CustomizedSender', 'ModuleName')
        if path_sender:
            if path_sender == "./":
                if dir_path not in sys.path:
                    sys.path.append(''.join([dir_path, '/']))
            else:
                if os.path.exists(path_sender + file_sender):
                    if path_sender not in sys.path:
                        sys.path.append(path_sender)
                else:
                    raise Exception("Sender Plugin path error!")
        if sender_module_name:
            sender_module = __import__(sender_module_name)
    except Exception, e:
        print e

    if sender_module:
        print sender_module_name

    try:
        path_receiver = config.get('CustomizedReceiver', 'DirectoryPath')
        file_receiver = config.get('CustomizedReceiver', 'FileName')
        receiver_module_name = config.get('CustomizedReceiver', 'ModuleName')
        if path_receiver:
            if path_receiver == "./":
                if dir_path not in sys.path:
                    sys.path.append(''.join([dir_path, '/']))
            else:
                if os.path.exists(path_receiver+file_receiver):
                    if path_sender not in sys.path:
                        sys.path.append(path_receiver)
                else:
                    raise Exception("Receiver Plugin path error!")
        if receiver_module_name:
            receiver_module = __import__(receiver_module_name)
    except Exception, e:
        print e

    if receiver_module:
        print receiver_module_name


def customized_generate_event():
    global event_module
    event = event_module.CustomizedEvent()
    #event_module.print_event()


def customized_event_handler(dsrc_unit, event):
    global receiver_module
    receiver_module.customized_event_handler(dsrc_unit, event)


def customized_msg_sender(dsrc_unit):
    global sender_module
    sender_module.sending_message(dsrc_unit)