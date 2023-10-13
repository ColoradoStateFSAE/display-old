import board
import adafruit_mpu6050
import time
import multiprocessing as mp
from multiprocessing import Value
from ctypes import c_char_p
from datetime import datetime, timedelta
import setproctitle
import smbus

class MotionData:
    def __init__(self, filename):
        self.filename = filename
        
        self.process = mp.Process(target=self.__read)
        self.process.daemon = True
        self.process.start()
        
    def read_raw_data(self, addr, bus):
        high = bus.read_byte_data(0x68, addr)
        low = bus.read_byte_data(0x68, addr+1)
        
        value = ((high << 8) | low)
        
        if(value > 32768):
            value = value - 65536
        return value
                    
    def __read(self):
        setproctitle.setproctitle("display - Motion")
        
        bus = smbus.SMBus(1)

        Device_Address = 0x68
        
        PWR_MGMT_1   = 0x6B
        CONFIG       = 0x1A
        ACCEL_CONFIG = 0x1C
        GYRO_CONFIG  = 0x1B
        ACCEL_XOUT_H = 0x3B
        ACCEL_YOUT_H = 0x3D
        ACCEL_ZOUT_H = 0x3F
        GYRO_XOUT_H  = 0x43
        GYRO_YOUT_H  = 0x45
        GYRO_ZOUT_H  = 0x47
        
        bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
        bus.write_byte_data(Device_Address, CONFIG, 0)
        bus.write_byte_data(Device_Address, ACCEL_CONFIG, 0x08)
        
        # Optional gyroscope
        # buffer = "Time (s),ax (m/s^2),ay (m/s^2),az (m/s^2),gx (rad/s),gy (rad/s),gz (rad/s)"
        buffer = "Time (s),ax (m/s^2),ay (m/s^2),az (m/s^2)"
        
        while True:
            try:
                precision = 4
                
                current_time = round(time.time(), precision)
                ax = round(self.read_raw_data(ACCEL_XOUT_H, bus) / 8192.0, precision)
                ay = round(self.read_raw_data(ACCEL_YOUT_H, bus) / 8192.0, precision)
                az = round(self.read_raw_data(ACCEL_ZOUT_H, bus) / 8192.0, precision)
                
                # Optional gyroscope
                # gx = round(self.read_raw_data(GYRO_XOUT_H, bus) / 131.0, precision)
                # gy = round(self.read_raw_data(GYRO_YOUT_H, bus) / 131.0, precision)
                # gz = round(self.read_raw_data(GYRO_ZOUT_H, bus) / 131.0, precision)
                
                buffer += "{},{},{},{}\n".format(current_time, ax, ay, az)
                
                if(len(buffer) >= 16384):
                    file = open(self.filename, "a+")
                    file.write(buffer)
                    buffer = ""
            except:
                pass
                
    def shutdown(self):
        self.process.kill()