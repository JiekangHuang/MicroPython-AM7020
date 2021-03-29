#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# am7020_http.py
# @Author : Zack Huang ()
# @Link   : zack@atticedu.com
# @Date   : 2020/11/7 下午7:22:38

from utime import ticks_ms, sleep_ms

CONN_BROKER_TIMEOUT_MS = 90


class AM7020HTTP():
    def __init__(self, nb, host, username="", password=""):
        self.nb = nb
        self.host = host
        self.username = username
        self.password = password
        self.statusCode = 0
        self.body = ""

    def newHTTP(self):
        # Create a HTTP Client Instance. refer AT CMD 8.2.1
        self.nb.sendAT("+CHTTPCREATE=\"http://", self.host, "\",\"",
                       self.username, "\",\"", self.password, "\"")
        return (self.nb.waitResponse(30000, "+CHTTPCREATE: 0") == 1 and self.nb.waitResponse() == 1)

    def chkHTTPChOpen(self):
        # Create a HTTP Client Instance. refer AT CMD 8.2.1
        self.nb.sendAT("+CHTTPCREATE?")
        if(self.nb.waitResponse(10000, "+CHTTPCREATE: 0,") == 1):
            used_state = self.nb.streamGetIntBefore(',')
            self.nb.waitResponse()
            return (used_state == 1)

    def connHTTP(self):
        # Establish the HTTP(S) Connection. refer AT CMD 8.2.3
        self.nb.sendAT("+CHTTPCON=0")
        return (self.nb.waitResponse(30000) == 1)

    def chkHTTPChConn(self):
        # Establish the HTTP(S) Connection. refer AT CMD 8.2.3
        self.nb.sendAT("+CHTTPCON?")
        if(self.nb.waitResponse(10000, "+CHTTPCON: 0,") == 1):
            conn_state = self.nb.streamGetIntBefore(',')
            self.nb.waitResponse()
            return (conn_state == 1)

    def closeHTTPCh(self):
        # Destroy the HTTP(S) Client Instance. refer AT CMD 8.2.5
        self.nb.sendAT("+CHTTPDESTROY=0")
        return (self.nb.waitResponse(2000) == 1)

    def disconHTTPCh(self):
        # Close the HTTP(S) Connection. refer AT CMD 8.2.4
        self.nb.sendAT("+CHTTPDISCON=0")
        return (self.nb.waitResponse(2000) == 1)

    def sendHTTPData(self, method, path, header, content_type, content_string):
        # Send HTTP(S) Package. refer AT CMD 8.2.6
        self.nb.sendAT("+CHTTPSEND=0,", method, ",\"", path, "\",\"",
                       header, "\",\"", content_type, "\",\"", content_string, "\"")
        return (self.nb.waitResponse(10000) == 1)

    def startRequest(self, path, method, headers="", content_type="", body=""):
        if(self.connServer()):
            temp_header = self.makeHeader("Host", self.host)
            if(headers != ""):
                for header in headers:
                    temp_header += self.makeHeader(header, headers[header])
            self.sendHTTPData(method, path, self.stringToHex(
                temp_header), content_type, self.stringToHex(body))
            # Header of the Response from Host. refer AT CMD 8.2.13
            if(self.nb.waitResponse(30000, "+CHTTPNMIH: 0,") == 1):
                self.ParseResponseMsg()
                self.endRequest()
                return True
        return False

    def endRequest(self):
        self.disconHTTPCh()

    def stringToHex(self, data):
        if(data):
            return (''.join([hex(ord(x))[2:].zfill(2) for x in data]))
        return ""

    def makeHeader(self, key, value):
        return (str(key) + ":" + str(value) + "\n")

    def connServer(self):
        endTime = ticks_ms() + CONN_BROKER_TIMEOUT_MS
        while(ticks_ms() < endTime):
            if(not self.chkHTTPChOpen()):
                # Delay is used here because the AM7020 module has a bug.
                sleep_ms(1000)
                self.closeHTTPCh()
                self.newHTTP()
                continue
            else:
                if(not self.chkHTTPChConn()):
                    self.disconHTTPCh()
                    self.connHTTP()
                    continue
                return True
        return False

    def get(self, path, headers=""):
        self.startRequest(path, 0, headers)
        return self.statusCode

    def post(self, path, headers="", content_type="", body=""):
        self.startRequest(path, 1, headers, content_type, body)
        return self.statusCode

    def ParseResponseMsg(self):
        self.statusCode = self.nb.streamGetIntBefore(',')
        data_len = self.nb.streamGetIntBefore(',')
        data = ""
        while(len(data) < data_len):
            data += self.nb.atRead()

        # Content of The Response from Host. refer AT CMD 8.2.14
        if(self.nb.waitResponse(5000, "+CHTTPNMIC: 0,") == 1):
            self.nb.streamSkipUntil(',')
            self.nb.streamSkipUntil(',')
            self.body = ""
            data_len = (self.nb.streamGetIntBefore(',') * 2)
            # read Content of the Response from Host
            # hex string to string
            data = ""
            while(len(data) < data_len):
                data += self.nb.atRead()
            self.body = self.HexToString(data)

    def HexToString(self, data):
        if(data):
            return (''.join(chr(int(data[i:i+2], 16)) for i in range(0, len(data), 2)))
        return ""

    def responseStatusCode(self):
        temp = self.statusCode
        self.statusCode = 0
        return temp

    def responseBody(self):
        temp = self.body
        self.body = ""
        return temp
