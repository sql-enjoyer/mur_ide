import pymurapi as mur
import time

auv = mur.mur_init()

def clamp(v, max_v, min_v):
    if v > max_v:
        return max_v
    if v < min_v:
        return min_v
    return v

# ПД-регулятор 
class PD(object):
    _kp = 0.0
    _kd = 0.0
    _prev_error = 0.0
    _timestamp = 0

    def __init__(self):
        pass

    def set_p_gain(self, value):
        self._kp = value

    def set_d_gain(self, value):
        self._kd = value

    def process(self, error):
        timestamp = int(round(time.time() * 1000))

        output = self._kp * error + self._kd / (timestamp - self._timestamp) * (error - self._prev_error)
        print(output)
        self._timestamp = timestamp
        self._prev_error = error
        return output


# функция сохранения курса плюс движение 
def keep_yaw(yaw_to_set, speed):
    def clamp_to180(angle):
        if angle > 180.0:
            return angle - 360
        if angle < -180.0:
            return angle + 360

        return angle

    try:
        error = auv.get_yaw() - yaw_to_set
        error = clamp_to180(error)
        output = keep_yaw.regulator.process(error)
        output = clamp(output, 100, -100)
        auv.set_motor_power(0, clamp((speed - output), 100, -100))
        auv.set_motor_power(1, clamp((speed + output), 100, -100))
    except AttributeError:
        keep_yaw.regulator = PD()
        keep_yaw.regulator.set_p_gain(0.8) # кэф проп
        keep_yaw.regulator.set_d_gain(0.6) # кэф дифф

# функция сохранения глубины 
def keep_depth(depth_to_set):
    try:
        error =  auv.get_depth() - depth_to_set
        output = keep_depth.regulator.process(error)
        output = clamp(output, 100, -100)
        
        auv.set_motor_power(2, output)
        auv.set_motor_power(3, output)
    except AttributeError:
        keep_depth.regulator = PD()
        keep_depth.regulator.set_p_gain(40) #кэф проп
        keep_depth.regulator.set_d_gain(40) #кэф дифф

isRunning = True
state = 0
while(isRunning):
    depth = auv.get_depth()
    yaw = auv.get_yaw()
    if state == 0:
        need_depth = 2.4
        keep_depth(need_depth)
        if need_depth-0.02<=depth<=need_depth+0.02:
            state = 1
            
    elif state == 1:
        need_yaw = -90
        keep_yaw(need_yaw, 5)
        if need_yaw-0.2<=yaw<=need_yaw+0.2:
            state = 2
        
    time.sleep(0.03)
        
        
        
        
        
        
        
        
        
        
        
        
