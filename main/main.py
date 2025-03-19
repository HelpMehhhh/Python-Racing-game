import pygame as pg
import os.path
from button import Button
import sys
import numpy as np
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




class GameLoop():
    def __init__(self, screen):
        self.screen = screen
        self.screen.fill((0,0,0))
        self.rescale()
        #self.Player = PlayerCar(self.screen, (50.5, 4))

    def redraw(self):
        self.screen.fill((0,0,0))
        pg.draw.rect(self.screen, (255, 0, 0), ((960, 540), (1, 2).dot(self.coord_conversion)))





        #self.Player.draw()

    def create_matrix(self):
        self.s_x, self.s_y = self.screen.get_size()
        


    def rescale(self):
        self.create_matrix()



        #self.Player.rescale()

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
        if event == "PLAY": self.scene = GameLoop(self.screen)


    def main_loop(self):
        self.scene.rescale()
        while self.running:
            self.scene.redraw()

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

        self.rescale()

    def movement_calc(self):
        pass

    def draw(self):
        self.screen.blit(self.image, self.image_rect)

    def accelerate(self):
        self.speed += 1

    def reverse(self):
        self.speed -= 1

    def unit_to_pixel(self, units):
        self.s_x, self.s_y = self.screen.get_size()
        pixels = int(((self.s_x + self.s_y) // 78)* units)
        return pixels

    def rescale(self):
        print(self.unit_to_pixel(1))
        self.image = pg.image.load(os.path.dirname(os.path.abspath(__file__))+f'/../static/car_{self.color_id}.png')
        self.image = pg.transform.scale(self.image, (self.unit_to_pixel(3), self.unit_to_pixel(4)))
        self.image_rect = self.image.get_rect(center=(self.unit_to_pixel(self.pos[0]), self.unit_to_pixel(self.pos[1])))




class PlayerCar(Car):
    def __init__(self, screen, start_pos, color_id=1):
        Car.__init__(self, screen, start_pos, color_id)


    def control(self, event):
        if event.key == pg.K_w:
            self.accelerate()

        if event.key == pg.K_s:
            self.reverse()




class Camera():
    def __init__(self):
        pass




if __name__ == "__main__":
    Mainloop()