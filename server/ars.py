import socket
import struct
import time
import uasyncio
from machine import Pin
import network
import machine
machine.freq(160000000)

import esp
esp.osdebug(None)

import gc
gc.collect()

import json

class Node():
    def __init__(self):
        self.host = "192.168.1.37"
        self.port = 30303
        self.sub_host = "192.168.4.1"
        self.sub_port = 50505
        self.server_host = "192.168.1.28"
        self.server_port = 30303
        self.timeout = 0.001
        self.wifi_ssid = "TE-Data"
        self.wifi_pwd = "pwd3141592654"
    
    def startWifi(self, ssid='MicroPython-AP', password='123456789'):
        sta_if = network.WLAN(network.STA_IF);
        sta_if.active(False)
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid=ssid, password=password)
        while ap.active() == False:
            time.sleep(.1)
        print("Started")

    def connectWifi(self):
        sta_if = network.WLAN(network.STA_IF);
        sta_if.active(True)
        sta_if.connect(self.wifi_ssid, self.wifi_pwd)
        while not sta_if.isconnected():
            time.sleep(.1)
        self.host = sta_if.ifconfig()[0]

    def startNetwork(self):
        self.startWifi()
        #self.connectWifi()
        print('\nConnection successful')

    async def twistedRecv(self, sock):
        print("recv")
        data = bytearray()
        while not data:
            print("waiting for data from twisted")
            try:
                data, addr = sock.recvfrom(1024)
            except Exception as e:
                try:
                    print('1')
                    await uasyncio.sleep(0)
                    #print("reconn", self.reconnect(sock))
                    try:
                        print('2')
                        host_addr = (self.server_host, self.server_port)
                        sock.settimeout(.5)
                        sock.connect(host_addr)
                        sock.sendto(b'\r\n', host_addr)
                        await uasyncio.sleep(0)
                    except:
                        try:
                            print('3')
                            sock.settimeout(1)
                            sock.connect((self.server_host, self.server_port))
                            node_name, port_server, port_client = "nodemcu1", self.port, "50505"
                            info = {
                                    "DEVICE": "nodemcu",
                                    "METHOD": "INFO",
                                    "NAME": node_name,
                                    "TOPICS": ["led_data"],
                                    "SERVER": port_server,
                                    "CLIENT": port_client
                                    }
                            msg = str(json.dumps(info) + "\r\n").encode()
                            sock.sendto(msg, (self.server_host, self.server_port))
                            sock.settimeout(self.timeout)
                            print("out")
                        except:
                            print('4')
                            await uasyncio.sleep(0)
                except Exception as e:
                    print("error", e)
        try:
            data = json.loads(data.decode())
            if 'METHOD' in data:
                method = data["METHOD"]
                if method == "UPDATE_METHODS":
                    new_methods = data["METHODS"]
                    try:
                        exec(new_methods)
                        print("Methods updated successfully")
                    except Exception as e:
                        print("failed to update methods", e)
                elif method == "PUB_NODEMCU":
                    response = self.mainServerMethods(method, data["DATA"], data["TOPIC"], data["MESSAGE_ID"])
                    if response:
                        msg = str(json.dumps(response) + "\r\n").encode()
                        sock.sendto(msg, addr)

                elif method == "GET_INFO":
                    node_name, port_server, port_client = "nodemcu1", "30303", "50505"
                    data = {
                            "DEVICE": "nodemcu",
                            "METHOD": "INFO",
                            "NAME": node_name,
                            "TOPICS": ["led_data"],
                            "SERVER": port_server,
                            "CLIENT": port_client
                            }
                    msg = str(json.dumps(data) + "\r\n").encode()
                    sock.sendto(msg, addr)

            print(data)
            sock.sendto(b'\r\n', addr)
        except Exception as e:
            #print(e, "eee")
            pass
        #print("end-", time.ticks_ms())

    def led(self, state):
        state = int(state)
        led = Pin(2, Pin.OUT)
        if state == 1:
            led.off()
        else:
            led.on()


    async def shareInfo(self, s):
        try:
            s.connect((self.server_host, self.server_port))
            node_name, port_server, port_client = "nodemcu1", self.port, "50505"
            info = {
                    "DEVICE": "nodemcu",
                    "METHOD": "INFO",
                    "NAME": node_name,
                    "TOPICS": ["led_data"],
                    "SERVER": port_server,
                    "CLIENT": port_client
                    }
            msg = str(json.dumps(info) + "\r\n").encode()
            s.sendto(msg, (self.server_host, self.server_port))
        except Exception as e:
            await uasyncio.sleep(0)

    async def listenServer(self, server):
        try:
            data = bytearray()
            data, addr = server.recvfrom(1024)
            data = json.loads(data.decode())
            method = data["METHOD"]
            response = json.dumps(self.localServerMethods(method, data["DATA"]))
            await uasyncio.sleep(0)
            if response:
                server.sendto(response.encode(), addr)
            else:
                server.sendto(b'\r\n', addr)
                pass
        except Exception as e:
            await uasyncio.sleep(0)



    async def main(self):
        self.startNetwork()
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind((self.sub_host, self.sub_port))
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.settimeout(self.timeout)
        while True:
            try:
                await self.listenServer(server)
                await uasyncio.sleep(0)
            except:
                pass
