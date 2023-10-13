import pygame
import threading
import subprocess
import time

import dashboard_elements

class Dashboard:
    def __init__(self, x, y, screen):
        self.gear = dashboard_elements.Gear(x//2, 0, screen)
        self.rpm = dashboard_elements.RPM(x//2, 280, screen)

        left = 30
        right = x-left

        row_1 = 20
        row_2 = row_1 + 115
        row_3 = row_2 + 115
        row_4 = row_3 + 115

        self.battery = dashboard_elements.Guage("BATTERY", "left", left, row_1, screen, units="V", decimals=1)
        self.clt = dashboard_elements.Guage("ENGINE", "right", right, row_1, screen, units="°F")
        self.afr = dashboard_elements.Guage("AFR", "left", left, row_2, screen, decimals=1)
        self.tps = dashboard_elements.Guage("TPS", "right", right, row_2, screen, units="%")
        self.sync = dashboard_elements.Guage("SYNC-LOSS", "left", left, row_3, screen)
        self.adv = dashboard_elements.Guage("ADVANCE", "right", right, row_3, screen, units="°")
        self.manifold = dashboard_elements.Guage("MAP", "left", left, row_4, screen, units="kPa")
        self.gps = dashboard_elements.Guage("GPS", "right", right, row_4, screen)
        
        self.wifi = dashboard_elements.WiFi(x//2, y-70, screen)
        self.filename = dashboard_elements.Filename(x//2, y-16, screen)

        self.intro = dashboard_elements.Fade(14, x, y, screen)
        
        self.wifi_active = False
        threading.Thread(target=self.__check_wifi, daemon=True).start()
        
    def update(self, can_data, gps_data, filename):
        self.gear.update(can_data.gear.value)
        self.rpm.update(can_data.rpm.value)
        
        self.battery.update(can_data.batt.value)
        self.manifold.update(can_data.manifold.value)
        self.clt.update(can_data.clt.value)
        self.tps.update(can_data.tps.value)
        self.afr.update(can_data.afr.value)
        self.adv.update(can_data.adv.value)
        self.sync.update(can_data.sync.value)
        self.gps.update(gps_data.sats.value)
        
        self.wifi.update(self.wifi_active)
        self.filename.update(filename)
        
    def show(self):
        self.gear.show()
        self.rpm.show()
        self.battery.show()
        self.manifold.show()
        self.clt.show()
        self.tps.show()
        self.afr.show()
        self.adv.show()
        self.sync.show()
        self.gps.show()
        
        self.wifi.show()
        self.filename.show()
        
    def __check_wifi(self):
        while True:
            iw_output = subprocess.run('iw wlan0 info | grep "\tssid "', stdout=subprocess.PIPE, shell=True)
            ssid = iw_output.stdout.decode()[5:-1]
            
            if(iw_output.returncode == 0):
                self.wifi_active = True
            else:
                self.wifi_active = False
            
            time.sleep(1)