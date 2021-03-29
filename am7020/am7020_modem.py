#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# am7020_modem.py
# @Author : Zack Huang ()
# @Link   : zack@atticedu.com
# @Date   : 2020/11/5 下午1:40:47

from machine import UART, Pin
from utime import ticks_ms, sleep_ms

GSM_OK = "OK\r\n"
GSM_ERROR = "ERROR\r\n"


class AM7020Modem:
    def __init__(self, uart_num, baudrate, tx_pin, rx_pin, reset_pin, dump_at_cmd=False):
        self._at = UART(uart_num, baudrate=baudrate, tx=Pin(
            tx_pin), rx=Pin(rx_pin), timeout=50)
        Pin(rx_pin, mode=Pin.ALT, pull=None, alt=2)
        self._reset_pin = Pin(reset_pin, Pin.OUT)
        self.dump_at_cmd = dump_at_cmd

    def atWrite(self, cmd):
        if(self.dump_at_cmd):
            print(cmd, end="")
        cmd = bytes(cmd, 'utf-8')
        self._at.write(cmd)

    def atRead(self, numChars=1):
        try:
            cmd = self._at.read(numChars)
            if(len(cmd) > 0):
                cmd = cmd.decode("utf-8")
                if(self.dump_at_cmd):
                    print(cmd, end="")
                return cmd
            return ""
        except TypeError:
            return ""
        except Exception as e:
            print(e)
            return ""

    def restart(self):
        self._reset_pin.off()
        sleep_ms(500)
        self._reset_pin.on()
        sleep_ms(500)

    def testAT(self, timeout_ms=10000):
        startTime = ticks_ms()
        while(ticks_ms() - startTime < timeout_ms):
            self.sendAT()
            if(self.waitResponse(200) == 1):
                return True
            sleep_ms(100)
        return False

    def streamWrite(self, *args):
        cmd = ""
        for arg in args:
            cmd += str(arg)
        self.atWrite(cmd)

    def sendAT(self, *args):
        cmd = "AT"
        for arg in args:
            cmd += str(arg)
        cmd += "\r\n"
        self.atWrite(cmd)

    def streamRead(self):
        self.atRead()

    def streamGetLength(self, numChars, timeout_ms=1000):
        startTime = ticks_ms()
        data = ""
        while(ticks_ms() - startTime < timeout_ms):
            data += self.atRead(numChars)
            if(data != "" and len(data) == numChars):
                return data

    def streamGetIntBefore(self, lastChar, timeout_ms=1000):
        startTime = ticks_ms()
        data = ""
        while(ticks_ms() - startTime < timeout_ms):
            data += self.atRead()
            if(data != "" and data.endswith(lastChar)):
                return int(data[:-1])
        return -9999

    def streamGetStringBefore(self, lastChar, timeout_ms=1000):
        startTime = ticks_ms()
        data = ""
        while(ticks_ms() - startTime < timeout_ms):
            data += self.atRead()
            if(data != "" and data.endswith(lastChar)):
                return data[:-1]
        return ""

    def streamSkipUntil(self, c, timeout_ms=1000):
        startTime = ticks_ms()
        while(ticks_ms() - startTime < timeout_ms):
            ch = self.atRead()
            if(ch == c):
                return True
        return False

    def waitResponse(self, timeout_ms=1000, r1=GSM_OK, r2=GSM_ERROR, r3=None, r4=None, r5=None):
        index = 0
        startTime = ticks_ms()
        data = ""
        while(True):
            data += self.atRead()
            if(r1 and data.endswith(r1)):
                index = 1
                break
            elif(r2 and data.endswith(r2)):
                index = 2
                break
            elif(r3 and data.endswith(r3)):
                index = 3
                break
            elif(r4 and data.endswith(r4)):
                index = 4
                break
            elif(r5 and data.endswith(r5)):
                index = 5
                break
            if(ticks_ms()-startTime > timeout_ms):
                break
        return index
    
    def waitURCResponse(self, timeout_ms=1000, r1=GSM_OK, r2=GSM_ERROR, r3=None, r4=None, r5=None):
        index = 0
        startTime = ticks_ms()
        data = ""
        pre_data = ""
        while(True):
            data += self.atRead()
            if(data == ""):
                break
            elif(data != pre_data):
                pre_data = data
                startTime = ticks_ms()

            if(r1 and data.endswith(r1)):
                index = 1
                break
            elif(r2 and data.endswith(r2)):
                index = 2
                break
            elif(r3 and data.endswith(r3)):
                index = 3
                break
            elif(r4 and data.endswith(r4)):
                index = 4
                break
            elif(r5 and data.endswith(r5)):
                index = 5
                break
            if(ticks_ms()-startTime > timeout_ms):
                break
        return index
