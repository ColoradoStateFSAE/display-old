import pygame
import os

import style

class ErrorScreen():
    def __init__(self, x, y, screen):
        self.error_icon_font = pygame.font.Font(style.icon_font, 160)
        self.error_font = pygame.font.Font(style.regular_font, 28)
        
        self.x, self.y = x, y
        self.screen = screen
        
    def show(self):
        error_icon = self.error_icon_font.render("\ue000", 1, style.gray)
        error_icon_rect = error_icon.get_rect(center=((self.x//2),(self.y//2)-15))
        self.screen.blit(error_icon, error_icon_rect)
        
        error_text = self.error_font.render("CAN disconnected", 1, style.white)
        error_text_rect = error_text.get_rect(center=(self.x//2,self.y//2+140))
        self.screen.blit(error_text, error_text_rect)