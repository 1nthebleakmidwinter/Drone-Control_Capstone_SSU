import ray
import robomaster
from robomaster import robot

@ray.remote
class testEngine(object) :
    def __init__(self, type = None) :
        self._type = type

        if type == 'drone' :
            robomaster.config.LOCAL_IP_STR = "192.168.10.2"
            self._drone = robot.Drone()
            self._drone.initialize()
            self._drone_tof = self._drone.sensor
            self._drone_flight = self._drone.flight
            self._drone_flight.mission_pad_on()
            self._old_tof = None
            self._tof = None

    def main_operation(self, cmd) :
        if self._type == 'drone' :
            self._battery = self._drone.get_status('bat')

            self._tof = self._drone_tof.get_ext_tof()
            if self._tof :
                self._old_tof = self._tof
            else :
                self._tof = self._old_tof
            
            self._height = self._drone.get_status('tof')

            if cmd == 'land' :
                self._drone_flight.land()
            elif cmd == 'takeoff' :
                self._drone_flight.takeoff()
            else :
                self._drone_flight.rc(cmd[0], cmd[1], cmd[2], cmd[3])

            self._mid = self._drone.get_status('mid')
            self._x = self._drone.get_status('x')
            self._y = self._drone.get_status('y')
            self._z = self._drone.get_status('z')
            self._vgx = self._drone.get_status('vgx')
            self._vgy = self._drone.get_status('vgy')
            self._vgz = self._drone.get_status('vgz')
            return [self._battery, self._tof, self._height, self._mid, self._x, self._y, self._z, self._vgx, self._vgy, self._vgz]