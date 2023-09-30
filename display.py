#! /usr/bin/python3

if __name__ == '__main__':
    import pygame
    import threading
    import time
    import os
    import sys
    import signal
    import setproctitle

    from Clock import Clock
    from Dashboard import Dashboard
    
    from CANData import CANData
    from GPSData import GPSData
    from MotionData import MotionData
    from NeoPixels import NeoPixels
    
    from ErrorScreen import ErrorScreen
    
    cwd = os.path.abspath(os.path.dirname(__file__))
    
    log_path = cwd + "/log"
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    i = 0
    while (os.path.exists(cwd + f"/log/{i:04d}can.csv") or os.path.exists(cwd + f"/log/{i:04d}gps.nmea") or os.path.exists(cwd + f"/log/{i:04d}motion.csv")):
        i += 1
    
    can_filename = log_path + "/{}can.csv".format(str(i).zfill(4))
    gps_filename = log_path + "/{}gps.nmea".format(str(i).zfill(4))
    motion_filename = log_path + "/{}motion.csv".format(str(i).zfill(4))

    can_data = CANData(can_filename, test_mode=False)
    gps_data = GPSData(gps_filename)
    motion_data = MotionData(motion_filename)
    neopixels = NeoPixels()

    x = 800
    y = 480
    
    pygame.display.init()
    pygame.font.init()
    pygame.mouse.set_visible(0)
    screen = pygame.display.set_mode((x,y))

    clock = Clock(0, x, y, screen, show_fps=False)
    
    dashboard = Dashboard(x, y, screen)
    error = ErrorScreen(x, y, screen)
    
    setproctitle.setproctitle("display.py")
    
    def shutdown(signal=None, frame=None):
        can_data.shutdown()
        gps_data.shutdown()
        motion_data.shutdown()
        neopixels.shutdown()
        pygame.display.quit()
        pygame.quit()
        sys.exit()
    
    signal.signal(signal.SIGHUP, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    
    while True:
        if(time.time() - can_data.last_update.value >= 3 or not can_data.has_data.value):
            error.show()
            dashboard.intro.reset()
            neopixels.update(0)
        else:
            dashboard.update(can_data, gps_data)
            dashboard.show()
            dashboard.intro.start()
            neopixels.update(can_data.rpm.value)
        
        clock.tick()
        pygame.display.update()
        screen.fill(0)
