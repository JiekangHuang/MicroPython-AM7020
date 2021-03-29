#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# am7020_mqtt.py
# @Author : Zack Huang ()
# @Link   : zack@atticedu.com
# @Date   : 2020/11/7 下午4:12:24

from random import randint
from utime import ticks_ms, sleep_ms

CONN_BROKER_TIMEOUT_MS = 90000
NUM_OF_SUB = 30


class AM7020MQTT():
    def __init__(self, nb):
        self.sub_list = []
        self.nb = nb

    def newMQTT(self, server, port):
        # New MQTT. refer AT CMD 11.2.1
        self.nb.sendAT("+CMQNEW=\"", server, "\",", port, ",30000,1132")
        if((self.nb.waitResponse(30000, "+CMQNEW: 0") == 1) and (self.nb.waitResponse() == 1)):
            return True
        return False

    def chkMQTTChOpen(self):
        # New MQTT. refer AT CMD 11.2.1
        self.nb.sendAT("+CMQNEW?")
        if(self.nb.waitResponse(10000, "+CMQNEW: 0,") == 1):
            used_state = self.nb.streamGetIntBefore(',')
            self.nb.streamSkipUntil('\n')
            self.nb.waitResponse()
            return (used_state == 1)
        return False

    def connMQTT(self, mqtt_id, username, password, cleansession):
        # Send MQTT Connection Packet. refer AT CMD 11.2.2
        self.nb.sendAT("+CMQCON=0,4,\"", mqtt_id, "\",20000,", int(cleansession), ",0,\"",
                       username, "\",\"", password, "\"")
        return (self.nb.waitResponse(30000) == 1)

    def chkMQTTChConn(self):
        # Send MQTT Connection Packet. refer AT CMD 11.2.2
        self.nb.sendAT("+CMQCON?")
        if(self.nb.waitResponse(10000, "+CMQCON: 0,") == 1):
            conn_state = self.nb.streamGetIntBefore(',')
            self.nb.waitResponse()
            return (conn_state == 1)
        return False

    def closeMQTTCh(self):
        # Disconnect MQTT. refer AT CMD 11.2.3
        self.nb.sendAT("+CMQDISCON=0")
        return (self.nb.waitResponse(2000) == 1)

    def setSyncMode(self, value):
        # Configure MQTT Synchronization Mode. refer AT CMD 11.2.14
        self.nb.sendAT("+CMQTSYNC=", value)
        return (self.nb.waitResponse(2000) == 1)

    def connBroker(self, server, port=1883, username="", password="", mqtt_id="", cleansession=True):
        # Note: 超過keepalive_interval時間會自動斷開。
        temp_mqtt_id = ""
        if(mqtt_id == ""):
            temp_mqtt_id = "am7020_mqttid_" + str(randint(0, 65535))
        else:
            temp_mqtt_id = mqtt_id

        startTime = ticks_ms()+CONN_BROKER_TIMEOUT_MS
        while(ticks_ms() < startTime):
            if(not self.chkMQTTChOpen()):
                # Delay is used here because the AM7020 module has a bug.
                sleep_ms(1000)
                self.closeMQTTCh()
                if(self.setSyncMode(1)):
                    self.newMQTT(server, port)
                continue
            else:
                if(not self.chkMQTTChConn()):
                    self.connMQTT(temp_mqtt_id, username,
                                  password, cleansession)
                    continue
                return True
        return False

    def chkConnBroker(self):
        return self.chkMQTTChConn()

    def publish(self, topic, msg, qos=0):
        # Send MQTT Publish Packet. refer AT CMD 11.2.6
        self.nb.sendAT("+CMQPUB=0,\"", topic, "\",", qos,
                       ",0,0,", len(str(msg)), ",\"", str(msg), "\"")
        return (self.nb.waitResponse(10000) == 1)

    def subscribe(self, topic, callback, qos=0):
        if(len(self.sub_list) <= NUM_OF_SUB):
            # Send MQTT Subscribe Packet. refer AT CMD 11.2.4
            self.nb.sendAT("+CMQSUB=0,\"", topic, "\",", qos)
            self.nb.waitResponse(10000)
            temp_sub = (topic, callback)
            self.sub_list.append(temp_sub)
            # Note: 此library有開啟MQTT Synchronization Mode，只要訂閱數量未超過設定上限(NUM_OF_SUB)都將視為訂閱成功。
            return True
        else:
            print("Subscription limit exceeded !")
        return False

    def unSubscribe(self, topic):
        # Send MQTT Unsubscribe Packet. refer AT CMD 11.2.5
        self.nb.sendAT("+CMQUNSUB=0,\"", topic, "\"")
        return (self.nb.waitResponse(10000) == 1)

    def procSubs(self):
        if(self.nb.waitURCResponse(10, "+CMQPUB: ") == 1):
            self.ParseSubMsg()


    def ParseSubMsg(self):
        if(self.nb.streamSkipUntil(',')):
            topic = self.nb.streamGetStringBefore(',')[1:-1]
            if(self.nb.streamSkipUntil('\"')):
                msg = self.nb.streamGetStringBefore('\n')[:-2]
                for sub in self.sub_list:
                    if(sub[0] == topic):
                        sub[1](msg)
                        return
                print("not find topic")
