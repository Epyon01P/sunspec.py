# -*- coding: utf-8 -*-
"""
Created on Mon May 11 22:54:37 2020
Interface with any Sunspec compatible inverter, read essential registers and publish the values to the MQTT bus
Configuration with JSON file
Support for multiple inverters
Currently only TCP connected inverters are supported
To do:
    *Functionise sunspec register publish loops, using additional config file
    *Check why S/N from SolarEdge inverters isn't read
@author: Epyon
"""
import sys
import json
import time
import paho.mqtt.client as mqtt
import sunspec.core.client as sunspecclient

brokers_out={"broker1":"localhost"}

#For debugging purposes, it's possible to give one inverter ip through the command line
try: 
    ipaddr = int(sys.argv[1])
    data = list([dict({'name': 'debuginverter', 'type': 'TCP', 'ipaddr': ipaddr, 'id': 1, 'registers': ["PPVphAB", "A", "W", "WH"], 'publish': False})])
except IndexError:
    try:
        with open('sunspec.json') as f:
            data = json.load(f)
    except OSError:
        data = list([dict({'name': 'debuginverter', 'type': 'TCP', 'ipaddr': "192.168.0.99", 'id': 1, 'registers': ["PPVphAB", "A", "W", "WH"], 'publish': False})]) #a default fallback register id

#Connect to the MQTT bus
client=mqtt.Client("sunspec")
client.connect(brokers_out["broker1"])

for inverter in data:
    ip = inverter['ipaddr']
    slaveid = int(inverter['id'])
    name = inverter['name']
    conattempts = 0
    while conattempts < 10: #try each inverter ten times before moving on
        try:
            d = sunspecclient.SunSpecClientDevice(sunspecclient.TCP, slaveid, ipaddr = ip) #connect to the inverter
            time.sleep(0.5)
            readattempts = 0
            while readattempts < 10: #try each register ten times before moving on
                try:
                    d.inverter.read()
                    timestamp = int(time.time())
                    if "PPVphAB" in inverter['registers']:
                        resp = {'name': 'PPVphAB', 'value': d.inverter.PPVphAB, 'unit': 'V', 'timestamp' : timestamp}
                        resp= json.dumps(resp, ensure_ascii=False)
                        print(resp)
                        topic="sunspec/" + name + "PPVphAB"
                        client.publish(topic,resp)
                    if "A" in inverter['registers']:
                        resp = {'name': 'A', 'value': d.inverter.A, 'unit': 'A', 'timestamp' : timestamp}
                        resp= json.dumps(resp, ensure_ascii=False)
                        print(resp)
                        topic="sunspec/" + name + "A"
                        client.publish(topic,resp)
                    if "W" in inverter['registers']:
                        resp = {'name': 'W', 'value': d.inverter.W, 'unit': 'W', 'timestamp' : timestamp}
                        resp= json.dumps(resp, ensure_ascii=False)
                        print(resp)
                        topic="sunspec/" + name + "W"
                        client.publish(topic,resp)
                    if "WH" in inverter['registers']:
                        resp = {'name': 'WH', 'value': d.inverter.WH, 'unit': 'WH', 'timestamp' : timestamp}
                        resp= json.dumps(resp, ensure_ascii=False)
                        print(resp)
                        topic="sunspec/" + name + "WH"
                        client.publish(topic,resp)
                    if "Hz" in inverter['registers']:
                        resp = {'name': 'Hz', 'value': d.inverter.Hz, 'unit': 'Hz', 'timestamp' : timestamp}
                        resp= json.dumps(resp, ensure_ascii=False)
                        print(resp)
                        topic="sunspec/" + name + "Hz"
                        client.publish(topic,resp)
                    break
                except:
                    readattempts += 1
                    time.sleep(0.5)
                    if readattempts == 10: print("Read error for inverter " + ip + ", skipping")
            break
        except:
            d.close()
            conattempts += 1
            time.sleep(0.5)
            if conattempts == 10: print("Connection error for inverter " + ip + ", skipping")
    try:
        d.close()
    except:
        print("oei")
client.disconnect()
