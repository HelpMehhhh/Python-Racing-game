import pygame as pg
import os.path
from button import Button
pg.init()


class MainMenu():
    def __init__(self, screen):
        self.menu_bg = pg.image.load(os.path.dirname(os.path.abspath(__file__))+'/../static/crappy_bg.png')
        self.screen = screen
        self.scene = self.main_menu
        self.rescale_btns = []

    def main_menu(self):
        self.screen.blit(self.menu_bg, (0,0))
        self.test = Button(self.screen, pos=(200, 200), text="test")
        self.test.update()
        self.rescale_btns.append(self.test)

    def settings(self):
        pass

    def redraw(self):
        self.scene()

    def rescale(self):
        self.menu_bg = pg.transform.scale(self.menu_bg, self.screen.get_size())
        for i in range(len(self.rescale_btns)):
            btn = self.rescale_btns[i]
            btn.rescale()

    def btn_events(self, event):
        self.test.update(event)

    def events(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.btn_events(event)




class Mainloop():
    def __init__(self):

        self.SCREEN_WIDTH = pg.display.Info().current_w
        self.SCREEN_HEIGHT = pg.display.Info().current_h
        self.clock = pg.time.Clock()

        icon = pg.image.load(os.path.dirname(os.path.abspath(__file__))+'/../static/game_icon.png')
        pg.display.set_icon(icon)

        self.running = True
        self.menu_bg = pg.image.load(os.path.dirname(os.path.abspath(__file__))+'/../static/crappy_bg.png')
        self.fullscreen = True
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.scene = MainMenu(self.screen)
        self.main_loop()


    def main_loop(self):
        while self.running:
            self.scene.redraw()

            pg.display.update()
            self.clock.tick(60)
            for event in pg.event.get():
                self.scene.events(event)
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_F11:
                        if self.fullscreen:
                            self.screen = pg.display.set_mode((self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2), pg.RESIZABLE)
                            self.fullscreen = False

                        else:
                            self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
                            self.fullscreen = True

                elif event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.WINDOWRESIZED:
                    self.scene.rescale()



class Car():
    pass

class Camera():
    pass



if __name__ == "__main__":
    Mainloop()