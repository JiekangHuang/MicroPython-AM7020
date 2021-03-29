#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# am7020_mqtt.py
# @Author : Zack Huang ()
# @Link   : zack@atticedu.com
# @Date   : 2020/11/9 上午9:31:20

from utime import ticks_ms, sleep_ms
from am7020.am7020_nb import AM7020NB
from am7020.am7020_mqtt import AM7020MQTT


apn = "twm.nbiot"
band = 28
MQTT_BROKER = "test.mosquitto.org"
PORT = 1883
MQTT_USERNAME = ""
MQTT_PASSWORD = ""
TEST_TOPIC = "temp/humidity"
UPLOAD_INTERVAL_MS = 60000


nb = AM7020NB(1, 9600, 4, 5, 3, False)
mqtt = AM7020MQTT(nb)


def nbConnect():
    print("Initializing modem...")
    while((not nb.init() or (not nb.nbiotConnect(apn, band)))):
        print(".")

    print("Waiting for network...")
    while(not nb.waitForNetwork()):
        print(".")
        sleep_ms(5000)
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
        if(ticks_ms() > chk_net_timer):
            chk_net_timer = ticks_ms() + 10000
            if(not nb.chkNet()):
                nbConnect()
            reConnBroker()

        if(ticks_ms() > pub_data_timer):
            pub_data_timer = ticks_ms() + UPLOAD_INTERVAL_MS
            print("publish: ", pub_data_timer, end="")
            if(mqtt.publish(TEST_TOPIC, str(pub_data_timer))):
                print("  success")
            else:
                print("  Fail")
        mqtt.procSubs()


main()
