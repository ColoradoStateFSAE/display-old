import serial
import pynmea2
import time
import os
import multiprocessing as mp
from multiprocessing import Value
from ctypes import c_char_p
from datetime import datetime, timedelta
import setproctitle

class GPSData:
    def __init__(self, filename):
        self.filename = filename
        
        self.mph =  Value("d", 0)
        self.sats = Value("d", 0)

        self.process = mp.Process(target=self.__read)
        self.process.daemon = True
        self.process.start()
        
    def checksum(self, s):
        result = 0
        s = s[1:]
        for c in s:
            result ^= ord(c)
        return "${}*{:X}\r\n".format(s,result).encode()
                    
    def __read(self):
        setproctitle.setproctitle("display - GPS")
        
        set_baud_rate = serial.Serial("/dev/ttyS0", 9600)
        set_baud_rate.write(self.checksum("$PMTK251,115200"))
        set_baud_rate.close()
        
        ser = serial.Serial("/dev/ttyS0", 115200)
        ser.write(self.checksum("$PMTK220,100"))
        
        buffer = ""
        
        while True:
            try:
                data = ser.readline().decode()
                msg = pynmea2.parse(data)
                
                if(data.startswith("$GPGGA")):
                    self.sats.value = int(msg.num_sats)
                    
                if(data.startswith("$GPRMC")):
                    self.mph.value = float(msg.spd_over_grnd) * 1.150779
                    buffer += data
                    
                if(len(buffer) >= 1024):
                    file = open(self.filename, "a+")
                    file.write(buffer)
                    buffer = ""
            except:
                continue
                
    def shutdown(self):
        self.process.kill()