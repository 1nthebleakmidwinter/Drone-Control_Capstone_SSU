from test import testEngine
import ray
import time
import KeyPressModule as kp

sub_engine = testEngine.remote('drone')
count = 5000

def getKeyboardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50
    if kp.getKey("LEFT"):
        lr = -speed
    elif kp.getKey("RIGHT"):
        lr = speed
    if kp.getKey("UP"):
        fb = speed
    elif kp.getKey("DOWN"):
        fb = -speed
    if kp.getKey("w"):
        ud = speed
    elif kp.getKey("s"):
        ud = -speed
    if kp.getKey("a"):
        yv = -speed
    elif kp.getKey("d"):
        yv = speed
    if kp.getKey("q"):
        return 'land'
    if kp.getKey("e"):
        return 'takeoff'
    return [lr, fb, ud, yv]

def exec() :
    kp.init()
    t1 = time.time()
    result = ray.get(sub_engine.main_operation.remote(getKeyboardInput()))
    t2 = time.time() - t1
    return result, t2
while count :
    count -= 1
    print(exec())