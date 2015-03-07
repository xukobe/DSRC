__author__ = 'xuepeng'

import ConfigParser
import sys
import os


class Plugin:
    def __init__(self, event_m=None, executor_m=None, receiver_m=None):
        self.event_module = event_m
        self.executor_module = executor_m
        self.receiver_module = receiver_m

plugins = {}

plugin_name = None

event_module = None
executor_module = None
receiver_module = None


def get_event_module():
    global event_module
    return event_module


def get_executor_module():
    global executor_module
    return event_module


def get_receiver_module():
    global receiver_module
    return receiver_module


def set_plugin(name):
    global event_module
    global executor_module
    global receiver_module
    global plugin_name
    global plugins
    plugin = plugins[name]
    if plugin:
        event_module = plugin.event_module
        executor_module = plugin.executor_module
        receiver_module = plugin.receiver_module
        plugin_name = name


def load_plugin():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser.SafeConfigParser()
    config_ini_path = ''.join([dir_path, "/config.ini"])
    print config_ini_path
    config.read(config_ini_path)
    try:
        plugins_config = dict(config.items('Plugins'))
        for key in plugins_config:
            value = plugins_config[key]
            load_a_plugin(key, value)
    except Exception, e:
        print e

    try:
        default_name = config.get('Default', 'default')
        set_plugin(default_name)
    except Exception, e:
        print e

    print "All plugins loaded"


def load_a_plugin(name, config_file):
    global plugins
    a_event_module = None
    a_executor_module = None
    a_receiver_module = None
    # Initialize plugins
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser.SafeConfigParser()
    config_ini_path = ''.join([dir_path, "/", config_file])
    print config_ini_path

    config.read(config_ini_path)

    plugin = Plugin()

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
            a_event_module = __import__(event_module_name)
            plugin.event_module = a_event_module
    except Exception, e:
        print e

    if a_event_module:
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
            a_executor_module = __import__(executor_module_name)
            plugin.executor_module = a_executor_module
    except Exception, e:
        print e

    if a_executor_module:
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
            a_receiver_module = __import__(receiver_module_name)
            plugin.receiver_module = a_receiver_module
    except Exception, e:
        print e

    if a_receiver_module:
        print receiver_module_name

    plugins[name] = plugin


def customized_generate_event():
    global event_module
    event = None
    if event_module:
        event = event_module.CustomizedEvent()
    return event
    #event_module.print_event()


def customized_event_handler(dsrc_unit, event):
    global receiver_module
    if receiver_module:
        receiver_module.customized_event_handler(dsrc_unit, event)


def customized_execute(dsrc_unit):
    global executor_module
    if executor_module:
        executor_module.execute(dsrc_unit)

def customized_cmd(dsrc_unit, user_input):
    global executor_module
    if executor_module:
        executor_module.customized_cmd(dsrc_unit, user_input)