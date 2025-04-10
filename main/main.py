import pygame as pg
import os.path
from button import Button
import sys
import numpy as np
from pygame import gfxdraw
import sympy as sym
pg.init()
pg.key.set_repeat(200)


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
    TRACK_WIDTH = 6
    BEZIER_POINTS = [((-6, 0), (-7, -20), (-5, -38)), ((-5, -38), (-3, -51), (2, -61)), ((2, -61), (15, -77), (25, -60)), ((25, -60), (34, -50), (54, -52)), ((54, -52), (76, -53), (76, -26)), ((76, -26), (78, -8), (40, -16)), ((40, -16), (15, -18), (36, -9)), ((36, -9), (60, -5), (126, -6)), ((126, -6), (144, -14), (110, -30)), ((110, -30), (96, -38), (115, -61)), ((115, -61), (140, -93), (156, -60)), ((156, -60), (172, -23), (195, 17)), ((195, 17), (208, 49), (168, 47)), ((168, 47), (-8, 48), (-19, 42)), ((-19, 42), (-34, 40), (-13, 18)), ((-13, 18), (-5, 13), (-6, 0)), ((-6, 0), (0, 0), (6, 0)), ((6, 0), (9, 13), (2, 21)), ((2, 21), (-22, 36), (11, 35)), ((11, 35), (52, 35), (166, 35)), ((166, 35), (190, 32), (145, -46)), ((145, -46), (139, -72), (126, -51)), ((126, -51), (117, -42), (140, -32)), ((140, -32), (162, -15), (152, 0)), ((152, 0), (148, 18), (19, -3)), ((19, -3), (-4, -11), (23, -28)), ((23, -28), (33, -31), (50, -24)), ((50, -24), (70, -22), (62, -37)), ((62, -37), (56, -44), (36, -43)), ((36, -43), (29, -43), (25, -47)), ((25, -47), (21, -50), (18, -56)), ((18, -56), (13, -64), (9, -52)), ((9, -52), (4, -36), (6, 0)),  ]
    RACETRACK_POINTS = []
    def __init__(self, screen):
        self.screen = screen
        self.generate_track_points()
        self.screen.fill((0,0,0))
        self.zoom = 0.4
        self.Player = PlayerCar(self.screen, self, [0, 0])
        self.rescale()

    def generate_track_points(self):
        for points in self.BEZIER_POINTS:
            t = sym.Symbol('t')
            Bx = (1 - t)*((1 - t)*points[0][0] + t*points[1][0]) + t*((1 - t)*points[1][0] + t*points[2][0])
            By = (1 - t)*((1 - t)*points[0][1] + t*points[1][1]) + t*((1 - t)*points[1][1] + t*points[2][1])


            steps = (round(i * 0.1, 2) for i in range(11))
            for step in steps:
                self.RACETRACK_POINTS.append((round(Bx.subs(t, step), 3), round(By.subs(t, step), 3)))

    def convert(self, gamev, ofssc = 1):
        return np.matmul((ofssc, *gamev), self.coord_conversion)

    def redraw(self):
        self.Player.movement_calc()
        self.create_matrix(self.Player.pos, self.zoom)
        self.screen.fill((78, 217, 65))
        self.background()
        self.Player.redraw()




    def create_matrix(self, center, zoom):
        s_x, s_y = self.screen.get_size()
        scale = np.array([[0, 0], [s_x*(0.05208*zoom), 0], [0, s_y*(0.09259*zoom)]])
        scale[0] = -np.matmul((1, *center), scale)+(s_x/2, s_y/2)
        self.coord_conversion = scale

    def background(self):
        screen_points = []
        for point in self.RACETRACK_POINTS:
            screen_points.append(self.convert(point))
        pg.gfxdraw.filled_polygon(self.screen, screen_points, (66, 66, 66))


    def rescale(self):
        self.create_matrix(self.Player.pos, self.zoom)
        self.Player.rescale()
        self.background()

    def events(self, event):
        if event.type == pg.KEYDOWN:
            self.Player.control(event)





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
    def __init__(self, screen, game, start_pos, color_id=1):
        self.screen = screen
        self.pos = start_pos
        self.color_id = color_id
        self.tire_angle = 0
        self.speed = 0
        self.game = game

    def redraw(self):
        self.image_rect = self.image.get_rect(center=self.game.convert(self.pos))
        self.screen.blit(self.image, self.image_rect)

    def movement_calc(self):
        self.pos[1] -= self.speed

    def accelerate(self):
        self.speed += 0.1

    def reverse(self):
        self.speed -= 0.1

    def rescale(self):
        self.image = pg.image.load(os.path.dirname(os.path.abspath(__file__))+f'/../static/car_{self.color_id}.png')
        self.image = pg.transform.scale(self.image, self.game.convert((2, 4), 0))




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