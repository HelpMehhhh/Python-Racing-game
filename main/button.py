import pygame as pg
class Button():
    def __init__(self, screen, pos, text="button", font=pg.font.SysFont('arial', 12), color="#FFFFFF", hover="#000000"):
        self.pos = pos
        self.text = text
        self.font = font
        self.color = color
        self.hover = hover
        self.text_box = self.font.render(self.text, True, self.color)
        self.button_rect = self.text_box.get_rect(center=self.pos)

    def update(self):
        self.mouse = pg.mouse.get_pos()
        if self.mouse[0] in range(self.button_rect.left, self.button_rect.right) and self.mouse[1] in range(self.button_rect.top, self.button_rect.bottom):
			self.text_box = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)
