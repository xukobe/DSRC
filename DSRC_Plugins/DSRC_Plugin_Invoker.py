__author__ = 'xuepeng'

import ConfigParser
import sys
import os


event_module = None
executor_module = None
receiver_module = None


def get_event_module():
    global event_module
    if not event_module:
        load_plugin()
    return event_module


def get_executor_module():
    global executor_module
    if not executor_module:
        load_plugin()
    return event_module


def get_receiver_module():
    global receiver_module
    if not receiver_module:
        load_plugin()
    return receiver_module



def load_plugin():
    global event_module
    global executor_module
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
        path_executor = config.get('CustomizedExecutor', 'DirectoryPath')
        file_executor = config.get('CustomizedExecutor', 'FileName')
        executor_module_name = config.get('CustomizedExecutor', 'ModuleName')
        if path_executor:
            if path_executor == "./":
                if dir_path not in sys.path:
                    sys.path.append(''.join([dir_path, '/']))
            else:
                if os.path.exists(path_executor + file_executor):
                    if path_executor not in sys.path:
                        sys.path.append(path_executor)
                else:
                    raise Exception("Executor Plugin path error!")
        if executor_module_name:
            executor_module = __import__(executor_module_name)
    except Exception, e:
        print e

    if executor_module:
        print executor_module_name

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
                    if path_receiver not in sys.path:
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
    return event
    #event_module.print_event()


def customized_event_handler(dsrc_unit, event):
    global receiver_module
    receiver_module.customized_event_handler(dsrc_unit, event)


def customized_execute(dsrc_unit):
    global executor_module
    executor_module.execute(dsrc_unit)

def customized_cmd(dsrc_unit, user_input):
    global executor_module
    executor_module.customized_cmd(dsrc_unit, user_input)