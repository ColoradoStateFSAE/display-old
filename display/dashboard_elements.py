import pygame
import pygame.gfxdraw
import time
import os
import subprocess

import style

cwd = os.path.abspath(os.path.dirname(__file__))

class Gear():
    def __init__(self, x, y, screen):
        self.gear_font = pygame.font.Font(style.bold_font, 110)
            
        self.x, self.y = x, y
        self.screen = screen
        
        self.gear_text = "N"
    
    def update(self, value):
        if(value == 0):
            self.gear_text = "N"
        else:
            self.gear_text = str(round(value))
    
    def show(self):
        gear_text = self.gear_font.render(self.gear_text, True, style.white)
        gear_rect = gear_text.get_rect(midtop=(self.x,self.y))
        self.screen.blit(gear_text, gear_rect)

class RPM():
    def __init__(self, x, y, screen, timeout=100):
        self.rpm_font = pygame.font.Font(style.bold_font, 80)

        self.x, self.y = x, y
        self.screen = screen
        
        self.timeout = timeout/1000
        self.last_update = 0
        
        self.rpm_text = "0"
    
    def update(self, input_value):
        if((time.time()-self.last_update) > self.timeout):
            self.last_update = time.time()
            input_value = (round(input_value) // 100) * 100
            self.rpm_text = str(input_value)
    
    def show(self):
        rpm_text = self.rpm_font.render(self.rpm_text, True, style.white)
        rpm_rect = rpm_text.get_rect(midbottom=(self.x, self.y))
        self.screen.blit(rpm_text, rpm_rect)

class Guage():
    def __init__(self, label_text, side, x, y, screen, units="", decimals=0, timeout=100):
        self.label_font = pygame.font.Font(style.bold_font, 30)
        self.value_font = pygame.font.Font(style.bold_font, 58)
        self.units_font = pygame.font.Font(style.bold_font, 30)
        
        self.label_text = label_text
        self.value_text = "0"
        self.side = side
        
        self.x, self.y = x, y
        self.screen = screen
        
        self.units_text = units
        
        self.decimals = decimals
        self.timeout = timeout/1000
        self.last_update = 0
    
    def update(self, input_value):
        if((time.time()-self.last_update) > self.timeout):
            self.last_update = time.time()
            if(self.decimals > 0):
                self.value_text = str(round(input_value, self.decimals))
            else:
                self.value_text = str(round(input_value))
    
    def show(self):
        height_offset = 28
        units_offset = 0
        if(self.units_text != ""):
            units_offset = 9
            
        if(self.side == "right"):            
            label = self.label_font.render(self.label_text, True, style.green)
            label_rect = label.get_rect(topright=(self.x, self.y))
            self.screen.blit(label, label_rect)
            
            units = self.units_font.render(self.units_text, True, style.white)
            units_rect = units.get_rect(topright=(self.x, self.y+height_offset+9))
            self.screen.blit(units, units_rect)
            
            value = self.value_font.render(self.value_text, True, style.white)
            value_rect = value.get_rect(topright=(units_rect.left-units_offset, self.y+height_offset))
            self.screen.blit(value, value_rect)
        elif(self.side == "left"):
            label = self.label_font.render(self.label_text, True, style.green)
            label_rect = label.get_rect(topleft=(self.x, self.y))
            self.screen.blit(label, label_rect)
            
            value = self.value_font.render(self.value_text, True, style.white)
            value_rect = value.get_rect(topleft=(self.x, self.y+height_offset))
            self.screen.blit(value, value_rect)
            
            units = self.units_font.render(self.units_text, True, style.white)
            units_rect = units.get_rect(topleft=(value_rect.right+units_offset, self.y+height_offset+9))
            self.screen.blit(units, units_rect)
            
class ErrorScreen():
    def __init__(self, x, y, screen):
        self.error_icon_font = pygame.font.Font(icon_font, 160)
        self.error_font = pygame.font.Font(regular_font, 28)
        
        self.x, self.y = x, y
        self.screen = screen
        
    def show(self):
        error_icon = self.error_icon_font.render("\ue000", 1, gray)
        error_icon_rect = error_icon.get_rect(center=((self.x//2),(self.y//2)-15))
        self.screen.blit(error_icon, error_icon_rect)
        
        error_text = self.error_font.render("CAN disconnected", 1, style.white)
        error_text_rect = error_text.get_rect(center=(self.x//2,self.y//2+140))
        self.screen.blit(error_text, error_text_rect)
            
class Fade():
    def __init__(self, amount, x, y, screen):
        self.show = True
        self.alpha = 255
        self.amount = amount
        self.x, self.y = x, y
        self.screen = screen
        self.overlay = pygame.Surface((self.x,self.y), pygame.SRCALPHA)
    
    def start(self):
        if(self.show):
            if(self.alpha < 0):
                self.alpha = 0
                self.show = False
            
            self.overlay.fill((0,0,0,self.alpha))
            self.screen.blit(self.overlay, (0,0))
            self.alpha -= self.amount
    
    def reset(self):
        self.show = True
        self.alpha = 255
        
class WiFi():
    def __init__(self, x, y, screen):
        self.icon = pygame.image.load(cwd + "/image/wifi.png")
        
        self.x, self.y = x, y
        self.screen = screen
        
        self.visible = False
        
    def update(self, value):
        self.visible = value
        
    def show(self):
        if(self.visible):
            icon_rect = self.icon.get_rect(midbottom=(self.x, self.y))
            self.screen.blit(self.icon, icon_rect)

class Filename():
    def __init__(self, x, y, screen):
        self.filename_font = pygame.font.Font(style.bold_font, 24)
            
        self.x, self.y = x, y
        self.screen = screen
        
        self.filename_text = "NONE"
    
    def update(self, value):
        self.filename_text = "WRITING TO FILE " + str(value)
    
    def show(self):
        filename_text = self.filename_font.render(self.filename_text, True, (128, 128, 128))
        filename_rect = filename_text.get_rect(midbottom=(self.x,self.y))
        self.screen.blit(filename_text, filename_rect)

class Clock():
    def __init__(self,  rate, x=None, y=None, screen=None, show_fps=False):
        self.fps_font = pygame.font.Font(cwd + "/font/square.ttf", 50)
        
        self.x, self.y = x, y
        self.screen = screen
        
        self.rate = rate
        self.show_fps = show_fps
        
        self.clock = pygame.time.Clock()
        
    def tick(self):
        self.clock.tick(self.rate)
        if(self.show_fps):
            fps_text = self.fps_font.render(str(round(self.clock.get_fps())), True, (0,255,0))
            fps_rect = fps_text.get_rect(bottomright=(self.x, self.y))
            self.screen.blit(fps_text, fps_rect)