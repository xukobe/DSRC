__author__ = 'xuepeng'

import json

class message_coder:
    def __init__(self):
        pass

    @staticmethod
    def decode(msg_str):
        json_obj = json.loads(msg_str)
        return json_obj

    @staticmethod
    def encode( msg_obj):
        msg = json.dumps(msg_obj)
        return msg


def main():
    obj = {}
    obj['a'] = 'b'
    a = {'a': 'b'}
    obj['obj'] = a
    msg_str = message_coder.encode(obj)
    print msg_str

    str = "{\"a\": \"b\", \"obj\": {\"a\": \"b\"}}"
    msg_obj = message_coder.decode(str)
    print msg_obj['a']
    print msg_obj['obj']
    print msg_obj

if __name__ == '__main__':
    main()
