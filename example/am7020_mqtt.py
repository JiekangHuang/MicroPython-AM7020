#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# am7020_mqtt.py
# @Author : Zack Huang ()
# @Link   : zack@atticedu.com
# @Date   : 2020/11/9 上午9:31:20

from time import time, sleep, ctime
from sim7020.sim7020_nb import SIM7020NB
from sim7020.sim7020_mqtt import SIM7020MQTT


apn = "twm.nbiot"
band = 28
MQTT_BROKER = "test.mosquitto.org"
PORT = 1883
MQTT_USERNAME = ""
MQTT_PASSWORD = ""
TEST_TOPIC = "temp/humidity"
UPLOAD_INTERVAL = 60


nb = SIM7020NB("/dev/ttyS0", 115200, 18)
mqtt = SIM7020MQTT(nb)


def nbConnect():
    print("Initializing modem...")
    while((not nb.init() or (not nb.nbiotConnect(apn, band)))):
        print(".")

    print("Waiting for network...")
    while(not nb.waitForNetwork()):
        print(".")
        sleep(5)
    print(" success")


def reConnBroker():
    if(not mqtt.chkConnBroker()):
        print("Connecting to", MQTT_BROKER, end="...")
        if(mqtt.connBroker(MQTT_BROKER, PORT, mqtt_id="MY_AM7020_TEST_MQTTID")):
            print(" success")
            print("subscribe: ", TEST_TOPIC, end="")
            if(mqtt.subscribe(TEST_TOPIC, callback1)):
                print(" success")
            else:
                print(" fail")
        else:
            print(" fail")


def callback1(msg):
    print(TEST_TOPIC, ":", msg)


def main():
    nbConnect()
    reConnBroker()
    chk_net_timer = 0
    pub_data_timer = 0
    while(True):
        if(time() > chk_net_timer):
            chk_net_timer = time() + 10
            if(not nb.chkNet()):
                nbConnect()
            reConnBroker()

        if(time() > pub_data_timer):
            pub_data_timer = time() + UPLOAD_INTERVAL
            print("publish: ", ctime(), end="")
            if(mqtt.publish(TEST_TOPIC, str(ctime()))):
                print("  success")
            else:
                print("  Fail")
        mqtt.procSubs()


main()
