from ars import *
from hc04 import HCSR04
from time import sleep
from dcmotor import DCMotor       
from machine import Pin, PWM   
from time import sleep    
 
rssi = {}
#main_networks = ["WE_90C31E_EXT", "MicroPython-AP", "WE_90C31E"]
old_time = 0
x = []
led_status = 0
frequency = 1000
pin1 = Pin(4, Pin.OUT)
pin2 = Pin(5, Pin.OUT)     
pin3 = Pin(14, Pin.OUT)     
enable = PWM(pin3, frequency)  
dc_motor = DCMotor(pin1, pin2, enable)      

pin4 = Pin(13, Pin.OUT)    
pin5 = Pin(15, Pin.OUT)     
pin6 = Pin(12, Pin.OUT)     
enable2 = PWM(pin6, frequency)  
dc_motor2 = DCMotor(pin4, pin5, enable2)      

m1_speed = 0
m2_speed = 0
f_angle = 0
first = True
o_error = 0
u = HCSR04(2, 16)
position = [0, 0]
m = [[{"visited": 0, "up": 0, "down": 0, "right": 0, "left": 0, "dead": 0} for _ in range(12)] for _ in range(12)]

"""
-1 not visited
-2 adjustment
"""

data = []
#orders = [[180, 0], [-90, 1], [60, 0], [180, 1], [30,0], [60, 0], [80, 0]]
#orders = [[0, 1], [22, 0], [90, 1]]
orders = []
#calb_angle = False 
calb_angle = True
#calb_vals = []
calb_vals = range(360)
angle_s = 0
angle_o = 0
f_angle1 = 0
c_distance = 0
n_distance = 0

orientation = 0
def localServerMethods(self, method, m_data):
    global rssi, x, old_time, dc_motor, first, f_angle, o_error, data
    try:
        data = m_data
        Observe()
    except Exception as e:
        print(e)
    #return {"METHOD": "RESPONSE", "METHOD": "led_data", "DATA": led_status}

def Observe():
    global rssi, x, old_time, dc_motor, first, f_angle, o_error, data, orders, calb_vals, angle_s, angle_o, calb_angle, f_angle1, c_distance, orientation, position, n_distance
    if first:
        #f_angle = (1.2 * (data[1][0] - 180)) + 23.80
        f_angle = data[1][0]
        first = False
    if not calb_angle:
        print(abs(f_angle - data[1][0]))
        if (abs(f_angle - data[1][0]) >= 5 and abs(f_angle - data[1][0]) <= 355) or len(calb_vals) < 110:
            calb_vals.append(data[1][0])
            rotate(100, 0)
            return 
        else:
            dc_motor.stop()
            dc_motor2.stop()
            sleep(2)
            angle_s = (max(calb_vals) - 360) / (min(calb_vals))
            angle_o = min(calb_vals)
            #f_angle = angle_s * f_angle + angle_o
            calb_angle = True

    ds = data[0]
    print(ds)
    irs = [int(ds[0] > 25), int(ds[1] > 25), int(ds[2] > 25)]
    if len(orders) == 0:
        direction, pos_x, pos_y = preDFS(position, irs)
        print(direction, pos_x, pos_y, orders)
        if direction == 0:
            c_distance = 30
            orders = [[c_distance, 3]]
        elif direction == 1:
            c_distance = 30
            orders = [[270, 1], [c_distance, 3]]
            orientation = 1
        elif direction == 2:
            c_distance = 30
            orders = [[90, 1], [c_distance, 3]]
            orientation = 2
        elif direction == 3:
            c_distance = -30
            orders = [[c_distance, 3], [180, 1]]
            orientation = 3
        elif direction == -1:
            c_distance = -30
            orders = [[c_distance, 3], [180, 1]]
            orientation = 3
        position = [pos_x, pos_y]
                

        
    else:
        order, value = orders[0][1], orders[0][0]
        if order == 1:
            '''
            #f_angle = angle_s * value + angle_o
            a = (value + 360) % 360
            f_angle1 =  f_angle
            f_angle =  calb_vals[min(len(calb_vals)-1, max(0, int(len(calb_vals)/360*a)))]
            '''
            f_angle = value
            orders[0][1] = 2
            return
 
        #angle = (1.2 * (data[1][0] - 180)) + 23.80
        #angle = data[1][0] * angle_s + angle_o
        #angle = (angle + 360) % 360
        angle = data[1][0]
        distance = u.distance_mm()
        '''
        error_angle = angle - f_angle + (angle - f_angle1)
        error_angle = (error_angle + max(calb_vals)) % max(calb_vals)
        
        while error_angle >= 180:
            error_angle -= 360

        while error_angle <= -180:
            error_angle += 360
        
        
        c_error_angle = 180 - error_angle
        while c_error_angle >= 180:
            c_error_angle -= 360

        while c_error_angle <= -180:
            c_error_angle += 360

        error_angle = min(c_error_angle, error_angle)
        '''
        #elif m[pos[0]][pos[1]] == -2:
        print(order, value)
        if order == 2:
            #if abs(error_angle) >= 5 and abs(error_angle) <= 175:
            #if abs(error_angle) > 3 and abs(error_angle) < max(calb_vals) - 3:
            '''
            if abs(error_angle) > 10:
                if calb_vals[min(len(calb_vals)-1, max(0, int(len(calb_vals)/360*180)))] < abs(error_angle):
                    rotate(error_angle, 0)
                else:
                    rotate(error_angle, 1)
                #rotate(error_angle, 0)
            else:
                dc_motor.stop()
                dc_motor2.stop()
                del orders[0]
                #sleep(2)
            '''
            if abs(value) > 180:
                rotate(value - 180, 0)
            else:
                rotate(value, 1)
            del orders[0]

        elif order == 3:
            n_distance = distance + value
            orders[0][1] = 0
        elif order == 0:
            err_distance = (n_distance - distance)*3 - 20
            '''
            if abs(error_angle) > 10 and (error_angle) < 90:
                print(error_angle)
                rotate(error_angle, calb_vals[min(len(calb_vals)-1, max(0, int(len(calb_vals)/360*180)))] > error_angle)
            '''
            if err_distance >= 2:
                #backwards(err_distance, err_distance, error_angle)
                forward(err_distance, err_distance, ds)
            else:
                dc_motor.stop()
                dc_motor2.stop()
                m[position[0]][position[1]]["visited"] = 1
                del orders[0]
                sleep(.5)   
        '''        
        if time.time() % 5 == 0:
            f_angle += 90
            if f_angle > 360:
                f_angle -= 360
        '''
def forward(speed_1, speed_2, ds=0):
    sp1, sp2 = abs(speed_1), abs(speed_2)
    right = (ds[0] % 30) - 7.5
    left = (ds[2]  % 30) - 7.5
    error = right - left
    error = error*3.5

    if error > 0 :
        sp2 -= abs(error)
    elif error < 0:
        sp1 -= abs(error)
    if sp1 > 100:
        sp2 -= (sp1 - 100)
        sp1 = 100

    elif sp2 > 100:
        sp1 -= (sp2 - 100)
        sp2 = 100
    sp1 = max(min(100, sp1), 0)
    sp2 = max(min(100, sp2), 0)
    dc_motor.forward(sp1)
    dc_motor2.forward(sp2)

def backwards(speed_1, speed_2, ds=0):
    right = (ds[0] % 30) - 7.5
    left = (ds[2]  % 30) - 7.5
    sp1, sp2 = abs(speed_1), abs(speed_2)
    error = right - left 
    error = error * 3.5
    if right - left > 0 :
        sp2 -= abs(error)
    elif right - left < 0:
        sp1 -= abs(error)
    if sp1 > 100:
        sp2 -= (sp1 - 100)
        sp1 = 100

    elif sp2 > 100:
        sp1 -= (sp2 - 100)
        sp2 = 100
    sp1 = max(min(100, sp1), 0)
    sp2 = max(min(100, sp2), 0)
    dc_motor.backwards(sp1)
    dc_motor2.backwards(sp2)

def rotate(error, direction):
    '''
    if error < 0:
        error = min(100, abs(error)/20)
        if direction:
            dc_motor2.forward(min(100, error))
            dc_motor.backwards(min(100, error))
        else:
            dc_motor.forward(min(100, error))
            dc_motor2.backwards(min(100, error))
    elif error > 0:
        error = min(100, abs((error)/20))
        if direction:
            dc_motor2.backwards(min(100, error))
            dc_motor.forward(min(100, error))
        else:
            dc_motor.backwards(min(100, error))
            dc_motor2.forward(min(100, error))
    '''
    if direction:
        dc_motor.forward(50)
        dc_motor2.backwards(50)
    else:
        dc_motor2.forward(50)
        dc_motor.backwards(50)
    sleep(.0055*error)
    dc_motor.stop()
    dc_motor2.stop()

'''
def right(speed_1, speed_2):
    dc_motor.backwards(speed_1)
    dc_motor2.backwards(speed_2)

def left(speed_1, speed_2):
    dc_motor.backwards(speed_2)
    dc_motor2.backwards(speed_1)

Signal meaning
1 -> only forward
2 -> right, forward
3 -> left, forward
4 -> right, left
5 -> forward, right, left
'''

def mainServerMethods(self, method, data, topic, msg_id):
    '''
    global led_status
    if topic == "led_data":
        state = int(data)
        led_status = state
        led = Pin(2, Pin.OUT)
        if state == 1:
            led.off()
        else:
            led.on()
    distance = sensor.distance_mm()
    data = {
                "METHOD": "RESPONSE",
                "DATA": distance,
                "TOPIC": "ULTRASONIC_DATA",
                "MESSAGE_ID": msg_id
            }
    print("sending", data)
    print(distance)
    sleep(1)
    return data
    '''
    pass

def preDFS(pos, irs):
    print(irs, pos)
    if orientation == 0:
        if m[pos[0]][pos[1]]["up"] == 0 and irs[1] == 1:
            m[pos[0]][pos[1]]["up"] = 1
            return 0, pos[0], pos[1]+1
        elif m[pos[0]][pos[1]]["right"] == 0 and irs[2] == 1:
            m[pos[0]][pos[1]]["right"] = 1
            return 1, pos[0] + 1, pos[1]
        elif m[pos[0]][pos[1]]["left"] == 0 and irs[0] == 1:
            m[pos[0]][pos[1]]["left"] = 1
            return 2, pos[0]-1, pos[1]
        else:
            m[pos[0]][pos[1]]["dead"] = 1

    elif orientation == 1:
        if m[pos[0]][pos[1]]["up"] == 0 and irs[0] == 1:
            m[pos[0]][pos[1]]["up"] = 1
            return 0, pos[0], pos[1]+1
        elif m[pos[0]][pos[1]]["right"] == 0 and irs[1] == 1:
            m[pos[0]][pos[1]]["right"] = 1
            return 1, pos[0]+1, pos[1]
        elif m[pos[0]][pos[1]]["back"] == 0 and irs[2] == 1:
            m[pos[0]][pos[1]]["back"] = 1
            return 3, pos[0], pos[1]-1
        else:
            m[pos[0]][pos[1]]["dead"] = 1

    elif orientation == 2:
        if m[pos[0]][pos[1]]["right"] == 0 and irs[0] == 1:
            m[pos[0]][pos[1]]["right"] = 1
            return 1, pos[0]+1, pos[1]
        elif m[pos[0]][pos[1]]["down"] == 0 and irs[1] == 1:
            m[pos[0]][pos[1]]["down"] = 1
            return 3, pos[0], pos[1]-1
        elif m[pos[0]][pos[1]]["left"] == 0 and irs[2] == 1:
            m[pos[0]][pos[1]]["left"] = 1
            return 2, pos[0]-1, pos[1]
        else:
            m[pos[0]][pos[1]]["dead"] = 1

    elif orientation == 3:
        if m[pos[0]][pos[1]]["down"] == 0 and irs[0] == 1:
            m[pos[0]][pos[1]]["down"] = 1
            return 3, pos[0], pos[1]-1
        elif m[pos[0]][pos[1]]["left"] == 0 and irs[1] == 1:
            m[pos[0]][pos[1]]["left"] = 1
            return 3, pos[0]-1, pos[1]
        elif m[pos[0]][pos[1]]["up"] == 0 and irs[2] == 1:
            m[pos[0]][pos[1]]["up"] = 1
            return 0, pos[0], pos[1]+1
        else:
            m[pos[0]][pos[1]]["dead"] = 1
    return -1

Node.localServerMethods = localServerMethods
Node.mainServerMethods = mainServerMethods
node = Node()
uasyncio.run(node.main())
