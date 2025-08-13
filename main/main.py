import pygame as pg
import os.path
from button import Button
import sys
import numpy as np
from pygame import gfxdraw
import sympy as sym
from numba import jit
import pickle
import cars
from random import randrange

pg.init()

FRAME_RATE = 60






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
            t = self.clock.tick(FRAME_RATE)
            self.scene.tick(t)
            pg.display.flip()
            for event in pg.event.get():
                r = self.scene.events(event)
                if r:
                    if r[0] == 1: self.change_scene(r[1])

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE: sys.exit()
                    if event.key == pg.K_F11:
                        if self.fullscreen:
                            self.screen = pg.display.set_mode((self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2), pg.RESIZABLE)
                            self.fullscreen = False

                        else:
                            self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
                            self.fullscreen = True

                elif event.type == pg.QUIT: self.running = False

                elif event.type == pg.WINDOWRESIZED: self.scene.rescale()






class MainMenu():
    def __init__(self, screen):
        self.screen = screen
        self.play = Button(self.screen, pos=(2, 2.66), text="PLAY")
        self.settings = Button(self.screen, pos=(2, 1.77), size_minus=1.2, text="SETTINGS")
        self.quit = Button(self.screen, pos=(2, 1.33), text="QUIT")


    def tick(self, t):
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
    def __init__(self, screen):
        self.screen = screen
        self.screen.fill((0,0,0))
        self.zoom = 0.4
        local_dir = os.path.dirname(__file__)
        with open(os.path.join(local_dir, 'center_points_08.pickle'), 'rb') as f: self.cent_line = pickle.load(f)

        with open(os.path.join(local_dir, 'parallel_points_01.pickle'), 'rb') as f: self.para_lines = pickle.load(f)
        with open(os.path.join(local_dir, 'winner.pickle'), 'rb') as f: g = pickle.load(f)
        with open(os.path.join(local_dir, 'genome_config.pickle'), 'rb') as f: conf = pickle.load(f)
        accel_values = [7, 10, 11, 12, 13, 14, 15]
        deccel_values = [14, 17, 18, 19, 20, 21, 22]
        speed_index = randrange(0, 7)

        #cars.AiCar(self.screen, self, [0, 0], 2, accel_values[speed_index], deccel_values[speed_index], g, conf, self.cent_line, 0)
        self.player = cars.PlayerCar(self.screen, self, [0, 0.5])
        self.rotation = self.player.car_angle
        self.cars = []
        self.screen_center = self.player.pos
        self.rescale()


    def convert_passer(self, gamev, ofssc = 1):
        npgamev = np.array([*gamev], dtype=np.float64)
        screen_center = np.array([*self.screen_center], dtype=np.float64)
        result = self.convert(npgamev, screen_center, self.rotation_matrix, self.coord_conversion, ofssc)
        if ofssc: return (result[0], pg.display.Info().current_h - result[1])

        else: return result


    @staticmethod
    @jit
    def convert(npgamev, screen_center, rot_m, coordc_m, ofssc):
        if ofssc:
            origin_point = np.array([npgamev[0] - screen_center[0], npgamev[1] - screen_center[1]], dtype=np.float64)
            rotated_point = np.dot(origin_point, rot_m)
            new_point = np.array([rotated_point[0] + screen_center[0], rotated_point[1] + screen_center[1]], dtype=np.float64)
            result = np.dot(np.array([ofssc, *new_point], dtype=np.float64), coordc_m)
            return result

        else:
            result = np.dot(np.array([ofssc, *npgamev], dtype=np.float64), coordc_m)
            return result


    def tick(self, time_elapsed):
        self.create_matrix()
        self.screen.fill((78, 217, 65))
        self.background()
        self.player.tick(time_elapsed)
        for car in self.cars: car.tick(time_elapsed, self.rotation)
        self.screen_center = self.player.pos
        self.rotation = self.player.car_angle


    def create_matrix(self):
        s_x, s_y = self.screen.get_size()
        rotate = np.array([[np.sin(self.rotation), (np.cos(self.rotation))], [-np.cos(self.rotation), np.sin(self.rotation)]], dtype=np.float64)
        self.rotation_matrix = rotate
        scale = np.array([[0, 0], [(s_x*(0.05208*self.zoom)), 0], [0, (s_y*(0.09259*self.zoom))]], dtype=np.float64)
        scale[0] = -np.matmul((1, *self.screen_center), scale)+(s_x/2, s_y/2)
        self.coord_conversion = scale


    def background(self):
        cent_line_screen = []
        pp_screen=[]
        for point in self.cent_line:
            cent_line_screen.append(self.convert_passer(point))

        for point in self.para_lines:
            pp_screen.append(self.convert_passer(point))

        pg.gfxdraw.filled_polygon(self.screen, pp_screen, (105,105,105))
        pg.draw.lines(self.screen, (255,255,255), True, cent_line_screen, 5)


    def rescale(self):
        self.create_matrix()
        self.background()


    def events(self, event):
        if event.type in (pg.KEYDOWN, pg.KEYUP):
            if event.key == pg.K_LEFT and self.zoom > 0.08: self.zoom -= 0.01

            if event.key == pg.K_RIGHT and self.zoom < 0.8: self.zoom += 0.01

            self.player.control(event)





if __name__ == "__main__":
    #cProfile.run("Mainloop()", sort="cumtime")
    Mainloop()