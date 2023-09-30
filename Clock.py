import pygame
import os

cwd = os.path.abspath(os.path.dirname(__file__))

regular_font = cwd + "/font/heebo_regular.ttf"
bold_font = cwd + "/font/heebo_bold.ttf"
icon_font = cwd + "/font/icon.ttf"

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