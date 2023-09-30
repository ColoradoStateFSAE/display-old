import board
import adafruit_mpu6050
import time
import multiprocessing as mp
from multiprocessing import Value
from ctypes import c_char_p
from datetime import datetime, timedelta
import setproctitle

class MotionData:
    def __init__(self, filename):
        self.filename = filename
        
        self.process = mp.Process(target=self.__read)
        self.process.daemon = True
        self.process.start()
                    
    def __read(self):
        setproctitle.setproctitle("display - Motion")
        
        i2c = board.I2C()
        mpu = adafruit_mpu6050.MPU6050(i2c)
        
        buffer = "Time (s),ax (m/s^2),ay (m/s^2),az (m/s^2),gx (rad/s),gy (rad/s),gz (rad/s),Temperature (C)\n"
        
        while True:
            try:
                ax, ay, az = mpu.acceleration[0], mpu.acceleration[1], mpu.acceleration[2]
                gx, gy, gz = mpu.gyro[0], mpu.gyro[1], mpu.gyro[2]
                
                buffer += "{},{},{},{},{},{},{}\n".format(time.time(), ax, ay, az, gx, gy, gz, mpu.temperature)
                
                if(len(buffer) >= 1024):
                    file = open(self.filename, "a+")
                    file.write(buffer)
                    buffer = ""
            except:
                pass 
                
    def shutdown(self):
        self.process.kill()