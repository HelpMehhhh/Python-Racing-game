import pygame as pg
pg.init()
class Button():
    def __init__(self, screen, pos, text="button", font=pg.font.SysFont('arial', 75), color="#FFFFFF", hover="#000000"):
        self.pos = pos
        self.screen = screen
        self.text = text
        self.font = font
        self.color = color
        self.hover = hover
        self.text_box = self.font.render(self.text, True, self.color)
        self.button_rect = self.text_box.get_rect(center=self.pos)

    def update(self, event = None):
        self.mouse = pg.mouse.get_pos()
        if self.mouse[0] in range(self.button_rect.left, self.button_rect.right) and self.mouse[1] in range(self.button_rect.top, self.button_rect.bottom):
            if event:
                if event.type == pg.MOUSEBUTTONDOWN:
                        return True
            self.text_box = self.font.render(self.text, True, self.hover)
        else:
            self.text_box = self.font.render(self.text, True, self.color)

        self.screen.blit(self.text_box, self.button_rect)