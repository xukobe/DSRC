__author__ = 'xuepeng'

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from multiprocessing import Process
# from USRP_Communication_Module import DSRC_USRP_Transceiver
from DSRC_Messager_Module import Test_Tube
from Controller_Module import DSRC_Unit
import time

import signal


def transceiver():
    # DSRC_USRP_Transceiver.main()
    Test_Tube.main()

def dsrc_unit(stdin_fileno):
    DSRC_Unit.main(stdin)


if __name__ == '__main__':
    p1 = Process(target=transceiver, args=())
    p2 = Process(target=dsrc_unit, args=(sys.stdin.fileno(),))
    p1.start()
    p2.start()
    while p2.is_alive():
        time.sleep(0.5)
    os.kill(p1.pid, signal.SIGUSR1)
    time.sleep(0.5)
    os.kill(p1.pid, signal.SIGTERM)