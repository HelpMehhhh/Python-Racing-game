import pygame as pg
import os.path

# Simple button object
class Button():
    def __init__(self, screen, pos, size_minus=1, text="button",
                 color="#FFFFFF", hover="#000000"):
        self.pos = pos
        self.screen = screen
        self.text = text
        self.color = color
        self.hover = hover
        self.size_minus = size_minus
        self.rescale()

    #Renders the text and image of the button based on configured inputs.
    def rescale(self):
        self.image = pg.image.load(os.path.dirname(os.path.abspath(__file__))
                                   +'/../static/button.png')
        self.x, self.y = self.screen.get_size()
        self.size = int((0.10*((self.x + self.y)/3)) / self.size_minus)
        self.image = pg.transform.scale(self.image, (self.x/3, self.y/5))
        self.image_rect = self.image.get_rect(center=(self.x/self.pos[0],
        self.y/self.pos[1]))
        self.font = pg.font.SysFont('arial', self.size)
        self.text_box = self.font.render(self.text, True, self.color)
        self.button_rect = self.text_box.get_rect(center=(
             self.x/self.pos[0], self.y/self.pos[1]))

    # Returns true if button is clicked, else just updates the graphics.
    def update(self, event = None):
        self.mouse = pg.mouse.get_pos()
        if self.mouse[0] in range(self.button_rect.left,
        self.button_rect.right) and\
        self.mouse[1] in range(self.button_rect.top, self.button_rect.bottom):
            if event:
                if event.type == pg.MOUSEBUTTONDOWN:
                        return True
            self.text_box = self.font.render(self.text, True, self.hover)
        else:
            self.text_box = self.font.render(self.text, True, self.color)

        self.screen.blit(self.image, self.image_rect)
        self.screen.blit(self.text_box, self.button_rect)
