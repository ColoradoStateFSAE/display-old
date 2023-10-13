import can
import time
import os
import multiprocessing as mp
from multiprocessing import Value
from ctypes import c_char_p
import setproctitle

cwd = os.path.abspath(os.path.dirname(__file__))

class CANData:
    def __init__(self, filename, test_mode=False):
        self.test_mode = test_mode
        
        self.filename = filename
        
        self.has_data =     Value("d", 0)
        
        self.rpm =          Value("d", 0)
        self.batt =         Value("d", 0)
        self.manifold =     Value("d", 0)
        self.clt =          Value("d", 0)
        self.tps =          Value("d", 0)
        self.afr =          Value("d", 0)
        self.adv =          Value("d", 0)
        self.sync =         Value("d", 0)
        self.gear =         Value("d", 0)
        
        self.last_update = Value("d", 0)
        self.last_update.value = time.time()
        
        if(not test_mode):
            self.process = mp.Process(target=self.__read)
            self.process.daemon=True
            self.process.start()
        else:
            self.has_data = 1
            self.rpm.value = 8000
            self.batt.value = 12.8
            self.manifold.value = 14
            self.clt.value = 180
            self.tps.value = 28
            self.afr.value = 14.7
            self.adv.value = 15
            self.sync.value = 23

    def read_data(self, msg, offset, size):
        data = 0
        if(len(msg.data) < offset + size):
            return 0
            
        for i in range(offset, offset + size):
            data = data << 8
            data += msg.data[i]
        return data

    def construct_data(self, msg, data, offset, size):
        for i in range(0, len(msg.data)-1):
            print(i)
            msg.data[i] = data % 256
            data >>= 8
    
    def twos_complement(self, val, bits):
        if (val & (1 << (bits - 1))) != 0:
            val = val - (1 << bits)
        return val

    def __read(self):
        setproctitle.setproctitle("display - CAN")
        
        if(not self.test_mode):
            bus = can.Bus(channel='can0', interface='socketcan')
        
        for msg in bus:
            self.has_data.value = 1
            self.last_update.value = time.time()
            
            buffer = ""
            
            base_id = 1520
            
            if(msg.arbitration_id == base_id):
                # RPM
                rpm_value = self.read_data(msg, 6, 2)
                self.rpm.value = rpm_value
                
            if(msg.arbitration_id == base_id+1):
                # Advance
                adv_value = self.read_data(msg, 0, 2)
                adv_value = self.twos_complement(adv_value, 16) / 10
                self.adv.value = adv_value
                
            if(msg.arbitration_id == base_id+2):
                # MAP
                map_value = self.read_data(msg, 2,2)
                map_value = self.twos_complement(map_value, 16) / 10
                self.manifold.value = map_value
                
                # Coolant
                clt_value = self.read_data(msg, 6,2) 
                clt_value = self.twos_complement(clt_value, 16) / 10
                self.clt.value = clt_value
                
            if(msg.arbitration_id == base_id+3):
                # TPS
                tps_value = self.read_data(msg, 0, 2)
                tps_value = self.twos_complement(tps_value, 16) / 10 
                self.tps.value = tps_value
                
                # Battery
                batt_value = self.read_data(msg, 2, 2)
                batt_value = self.twos_complement(batt_value, 16) / 10
                self.batt.value = batt_value
                
            if(msg.arbitration_id == base_id+31):
                # Afr
                afr_value = self.read_data(msg, 0, 1) / 10
                self.afr.value = afr_value
                
            if(msg.arbitration_id == base_id+43):
                # Sync-loss
                sync_value = self.read_data(msg, 0, 1)
                self.sync.value = sync_value
                
            if(msg.arbitration_id == 1620):
                # Gear
                gear_value = self.read_data(msg, 0, 1)
                self.gear.value = gear_value
            
            timestamp = "{:.3f}".format(round(msg.timestamp, 3))
            buffer += timestamp + " "
            buffer += "%X" % msg.arbitration_id + " "
            for i in msg.data:
                buffer += f'{i:02X}' + " "
            buffer = buffer[:-1] + "\n"
            
            if(len(buffer) >= 0):
                file = open(self.filename, "a+")
                file.write(buffer)
                buffer = ""
                
    def shutdown(self):
        if(not self.test_mode):
            self.process.kill()