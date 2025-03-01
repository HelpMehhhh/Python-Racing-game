import pygame as pg
import os.path
pg.init()
class Button():
    def __init__(self, screen, pos, text="button", font=pg.font.SysFont('arial', 75), color="#FFFFFF", hover="#000000"):
        self.pos = pos
        self.screen = screen
        self.text = text
        self.font = font
        self.color = color
        self.hover = hover
        self.image = pg.image.load(os.path.dirname(os.path.abspath(__file__))+'/../static/button.png')
        self.image_rect = self.image.get_rect(center=self.pos)
        self.text_box = self.font.render(self.text, True, self.color)
        self.button_rect = self.text_box.get_rect(center=self.pos)

    def rescale(self):
        self.image = pg.transform.scale(self.image, self.screen.get_size())
        self.image_rect = self.image.get_rect(center=self.pos)

    def update(self, event = None):
        self.mouse = pg.mouse.get_pos()
        if self.mouse[0] in range(self.button_rect.left, self.button_rect.right) and self.mouse[1] in range(self.button_rect.top, self.button_rect.bottom):
            if event:
                if event.type == pg.MOUSEBUTTONDOWN:
                        return True
            self.text_box = self.font.render(self.text, True, self.hover)
        else:
            self.text_box = self.font.render(self.text, True, self.color)

        self.screen.blit(self.image, self.image_rect)
        self.screen.blit(self.text_box, self.button_rect)
