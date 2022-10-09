#=================Libs=============================
import socket
import json
import uasyncio
import network
import time
from machine import Pin, ADC
import hc04 as hc
from hmc5883l import HMC5883L
#=====================================pins==================
u1 = hc.HCSR04(14, 16) # left
u2 = hc.HCSR04(13, 15) # back
u3 = hc.HCSR04(0, 4) # right
#ir = [Pin(14, Pin.IN), ADC(0), Pin(13, Pin.IN)]

d1, d2, d3 = 0, 0, 0
#==================================functions=================
r1 = []
r2 = []
r3 = []
def readIR():
        return [ir[0].value(), int(ir[1].read() > 1000), ir[2].value()]
        v = []
        for i in ir:
                v.append(i.value())
        return v

import machine
import utime

async def send(data, sock):
	data = json.dumps(data).encode()
	try:
		recved = False
		sock.sendto(data, ("192.168.4.1", 50505))
		msg, addr = sock.recvfrom(1024)
		if msg:
			data = json.loads(msg.decode())
			method = data["METHOD"]
			data = data["DATA"]
			if method == "led_data":
				led(data)

	except Exception as e:
		#print('-', data, e)
                pass
	await uasyncio.sleep(0)

def led(state):
	state = int(state)
	led = Pin(2, Pin.OUT)
	if state == 1:
		led.off()
	else:
		led.on()

def connect_wifi():
	ap_if = network.WLAN(network.AP_IF)
	ap_if.active(False)
	sta_if = network.WLAN(network.STA_IF);
	sta_if.active(True)
	sta_if.connect("MicroPython-AP", "123456789")
	while not sta_if.isconnected():
                time.sleep(.1)
		pass

	ip = sta_if.ifconfig()[0]
	return ip

async def localServerMethods(method, data):
	print(method, data)

async def listenServer(server):
	try:
		data = bytearray()
		data, addr = server.recvfrom(1024)
		data = json.loads(data.decode())
		method = data["METHOD"]
		response = json.dumps(localServerMethods(method, data["DATA"]))
		if response:
			server.sendto(response.encode(), addr)
		else:
			server.sendto(b'\r\n', addr)
	except Exception as e:
		pass
	await uasyncio.sleep(0)

async def main():
        global d1, d2, d3, r1, r2, r3
	ip = connect_wifi()
	#ip = "192.168.4.3"
	server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server.bind((ip, 30303))
	server.settimeout(0.001)
	while True:
		try:
			#data = [[x[0], x[3]] for x in network.WLAN(network.STA_IF).scan()]
                        r1.append(u1.distance_mm())
                        r2.append(u2.distance_mm())
                        r3.append(u3.distance_mm())
                        #comp = HMC5883L()
			#x,y,z = comp.read()
                        #x, y, z = comp.format_result(x, y, z)
                        x, y, z = 0, 0, 0
                        d1 = sum(r1) / len(r1)
                        d2 = sum(r2) / len(r2)
                        d3 = sum(r3) / len(r3)
                        if len(r1) > 10:
                            del r1[0]
                        if len(r2) > 10:
                            del r2[0]
                        if len(r3) > 10:
                            del r3[0]
                        print(x, y, z,d3, d2, d1) 
			#send({"METHOD": 'RSSI', "DATA": {"networks": data, "point_name": 1}}, server)
			#await send({"METHOD": 'RSSI', "DATA": {"networks": data, "point_name": 1}}, server)
			await send({"METHOD": 'IRS', "DATA": [[d3, d2, d1], [x, y, z], d2]}, server)
			#await send({"METHOD": 'Ultra', "DATA": u.distance_mm()}, server)
			#await listenServer(listener)
			await uasyncio.sleep(0)
		except Exception as e:
			print(e)
			pass
		
uasyncio.run(main())
