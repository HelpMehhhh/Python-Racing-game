import pygame as pg
import os.path
from button import Button
import sys
pg.init()


class Settings():
    def __init__(self, screen):
        pass

    def redraw(self):
        pass




class MainMenu():
    def __init__(self, screen):
        self.screen = screen

    def redraw(self):
        self.screen.blit(self.menu_bg, (0,0))
        self.play.update()
        self.quit.update()

    def rescale(self):
        self.x, self.y = self.screen.get_size()
        self.menu_bg = pg.image.load(os.path.dirname(os.path.abspath(__file__))+'/../static/crappy_bg.png')
        self.menu_bg = pg.transform.scale(self.menu_bg, self.screen.get_size())
        self.play = Button(self.screen, pos=(self.x/2, self.y/2.66), text="PLAY")
        self.play.rescale()
        self.quit = Button(self.screen, pos=(self.x/2, self.y/1.33), text="QUIT")
        self.quit.rescale()

    def events(self, event):
        if self.play.update(event): return [1, "PLAY"]
        if self.quit.update(event): sys.exit()




class GameLoop():
    pass




class Mainloop():
    def __init__(self, scenes):

        self.SCREEN_WIDTH = pg.display.Info().current_w
        self.SCREEN_HEIGHT = pg.display.Info().current_h
        self.clock = pg.time.Clock()

        icon = pg.image.load(os.path.dirname(os.path.abspath(__file__))+'/../static/game_icon.png')
        pg.display.set_icon(icon)

        self.running = True
        self.menu_bg = pg.image.load(os.path.dirname(os.path.abspath(__file__))+'/../static/crappy_bg.png')
        self.fullscreen = True
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.scene = scenes[0]

        self.main_loop()

    def change_scene(self, event):
        if event == "PLAY": self.scene

    def main_loop(self):
        self.scene.rescale()
        while self.running:
            self.scene.redraw()

            pg.display.update()
            self.clock.tick(60)
            for event in pg.event.get():
                r = self.scene.events(event)
                if r[0] == 1: self.change_scene(r[1])
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
    #color id refers to how the car image files are named 1 through 6
    def __init__(self, screen, start_pos, color_id=1):
        pass


class PlayerCar(Car):
    def __init__(self, screen, start_pos, color_id=1):
        Car.__init__(self, screen, start_pos, color_id)




class Camera():
    pass



if __name__ == "__main__":
    scenes = [MainMenu(), Settings(), GameLoop()]
    Mainloop(scenes)