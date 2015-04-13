__author__ = 'xuepeng'

from threading import Thread
import time

SENSOR_NAME_BUMPS_AND_WHEEL_DROPS = "BUMPS_AND_WHEEL_DROPS"

# EVENT_BUMP_RIGHT = 0
# EVENT_BUMP_LEFT = 1
# EVENT_WHEEL_DROP_RIGHT = 2
# EVENT_WHEEL_DROP_LEFT = 3
# EVENT_WHEEL_DROP_CASTER = 4

EVENT_BUMP = 0
EVENT_WHEEL_DROP = 1


class SensorCallback:
    def __init__(self):
        pass

    def sensor_event_handler(self, events):
        print "Not Implemented"


class CreateSensorDetector(Thread):
    def __init__(self, create=None, callback=None, interval=0.01):
        Thread.__init__(self)
        self.create = create
        self.callback = callback
        self.interval = interval
        self.bump = False
        self.drop = False
        self.running = True

    def run(self):
        while self.running:
            if self.create:
                events = []
                bump_wheel_drop_data = self.create.getSensor(SENSOR_NAME_BUMPS_AND_WHEEL_DROPS)
                if bump_wheel_drop_data:
                    if bump_wheel_drop_data[0] or bump_wheel_drop_data[1] or bump_wheel_drop_data[2]:
                        self.drop = True
                        events.append(EVENT_WHEEL_DROP)
                    else:
                        self.drop = False
                    if bump_wheel_drop_data[3] or bump_wheel_drop_data[4]:
                        self.bump = True
                        events.append(EVENT_BUMP)
                    else:
                        self.bump = False
                    if len(events) > 0:
                        if self.callback:
                            self.callback.sensor_event_handler(events)
            time.sleep(self.interval)

    def stop_self(self):
        self.running = False