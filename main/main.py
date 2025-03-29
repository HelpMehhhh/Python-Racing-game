import pygame as pg
import os.path
from button import Button
import sys
import numpy as np
from math import pi
from pygame import gfxdraw
pg.init()


class Settings():
    def __init__(self, screen):
        pass

    def redraw(self):
        pass




class MainMenu():
    def __init__(self, screen):
        self.screen = screen
        self.play = Button(self.screen, pos=(2, 2.66), text="PLAY")
        self.settings = Button(self.screen, pos=(2, 1.77), size_minus=1.2, text="SETTINGS")
        self.quit = Button(self.screen, pos=(2, 1.33), text="QUIT")

    def redraw(self):
        self.screen.blit(self.menu_bg, (0,0))
        self.play.update()
        self.quit.update()
        self.settings.update()

    def rescale(self):
        self.x, self.y = self.screen.get_size()
        self.menu_bg = pg.image.load(os.path.dirname(os.path.abspath(__file__))+'/../static/crappy_bg.png')
        self.menu_bg = pg.transform.scale(self.menu_bg, self.screen.get_size())

        self.play.rescale()
        self.settings.rescale()
        self.quit.rescale()

    def events(self, event):
        if self.play.update(event): return [1, "PLAY"]
        if self.quit.update(event): sys.exit()




class Game():

    RACETRACK_POINTS = []
    def __init__(self, screen):
        self.screen = screen
        self.screen.fill((0,0,0))
        self.Player = PlayerCar(self.screen, (0, 0))
        self.rescale()

    def convert(self, gamev, ofssc = 1):
        return np.matmul((ofssc, *gamev), self.coord_conversion)

    def redraw(self):
        self.screen.fill((78, 217, 65))
        self.Player.rescale(self)
        self.background()



    def create_matrix(self, center, zoom):
        s_x, s_y = self.screen.get_size()
        scale = np.array([[0, 0], [s_x*(0.05208*zoom), 0], [0, s_y*(0.09259*zoom)]])
        scale[0] = -np.matmul((1, *center), scale)+(s_x/2, s_y/2)
        self.coord_conversion = scale

    def background(self):
        pg.gfxdraw.filled_polygon(self.screen, ((850, 540), (850, 440), (890, 400), (1100, 400), (1050, 440), (1050, 540)), (0, 0, 0))


    def rescale(self):
        self.create_matrix((0, 0), 0.2)
        self.Player.rescale(self)
        self.background()

    def events(self, event):
        #if event.type == pg.KEYDOWN:
            #self.Player.control(event)
        pass




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

    def change_scene(self, event):
        if event == "PLAY": self.scene = Game(self.screen)

    def main_loop(self):
        self.scene.rescale()
        while self.running:
            self.scene.redraw()

            #pg.display.flip()
            pg.display.update()
            self.clock.tick(60)
            for event in pg.event.get():
                r = self.scene.events(event)
                if r:
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
        self.screen = screen
        self.pos = start_pos
        self.color_id = color_id
        self.tire_angle = 0
        self.speed = 0

    def movement_calc(self):
        pass

    def accelerate(self):
        self.speed += 1

    def reverse(self):
        self.speed -= 1

    def rescale(self, game):
        self.image = pg.image.load(os.path.dirname(os.path.abspath(__file__))+f'/../static/car_{self.color_id}.png')
        self.image = pg.transform.scale(self.image, game.convert((2, 4), 0))
        self.image_rect = self.image.get_rect(center=game.convert(self.pos))
        self.screen.blit(self.image, self.image_rect)




class PlayerCar(Car):
    def __init__(self, screen, start_pos, color_id=1):
        Car.__init__(self, screen, start_pos, color_id)

    def control(self, event):
        if event.key == pg.K_w:
            self.accelerate()

        if event.key == pg.K_s:
            self.reverse()







if __name__ == "__main__":
    Mainloop()