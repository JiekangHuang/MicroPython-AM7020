#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# am7020_http.py
# @Author : Zack Huang ()
# @Link   : zack@atticedu.com
# @Date   : 2020/11/9 上午9:31:29

from time import time, sleep
from am7020.am7020_nb import AM7020NB
from am7020.am7020_http import AM7020HTTP

apn = "twm.nbiot"
band = 28
HTTP_SERVER = "httpbin.org"
HTTP_GET_API = "//anything"
HTTP_POST_API = HTTP_GET_API
UPLOAD_INTERVAL = 60

nb = AM7020NB(0, 115200, 16, 17, 5)
http = AM7020HTTP(nb, HTTP_SERVER)


def nbConnect():
    print("Initializing modem...")
    while((not nb.init() or (not nb.nbiotConnect(apn, band)))):
        print(".")

    print("Waiting for network...")
    while(not nb.waitForNetwork()):
        print(".")
        sleep(5)
    print(" success")


def main():
    nbConnect()
    chk_net_timer = 0
    get_post_data_timer = 0
    while(True):
        if(time() > chk_net_timer):
            chk_net_timer = time() + 10
            if(not nb.chkNet()):
                nbConnect()
        if(time() > get_post_data_timer):
            get_post_data_timer = time() + UPLOAD_INTERVAL
            print("HTTP Get...")
            http.get(HTTP_GET_API)
            state_code = http.responseStatusCode()
            body = http.responseBody()
            print("GET state code = ")
            print(state_code)
            print("body = ")
            print(body)

            print("HTTP Post...")
            http.post(HTTP_POST_API, content_type="application/json",
                      body="{\"value\": \"POST\"}")
            state_code = http.responseStatusCode()
            body = http.responseBody()
            print("POST state code = ")
            print(state_code)
            print("body = ")
            print(body)


main()
