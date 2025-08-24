from button import Button
import pygame as pg
import os.path
from sys import exit
import pickle
import numpy as np
from numba import jit
from pygame import gfxdraw
from enum import IntEnum
class Scene(IntEnum):
        main_menu = 0
        game = 1
class Graphics():

    def __init__(self, scene, cars=None):
        pg.init()
        self.SCREEN_WIDTH = pg.display.Info().current_w
        self.SCREEN_HEIGHT = pg.display.Info().current_h
        icon = pg.image.load(os.path.dirname(os.path.abspath(__file__))+'/../static/game_icon.png')
        pg.display.set_icon(icon)
        self.menu_bg = pg.image.load(os.path.dirname(os.path.abspath(__file__))+'/../static/crappy_bg.png')
        self.fullscreen = True
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        if scene == Scene.main_menu: self.scene_obj = MainMenu(self.screen)
        elif scene == Scene.game: self.scene_obj = GameGraphics(self.screen, cars)
        self.scene = scene
        self.scene_rescale()

    def scene_chg(self, cars=None, time=None):
        if self.scene == Scene.main_menu: self.scene_obj = MainMenu(self.screen)
        elif self.scene == Scene.game: self.scene_obj = GameGraphics(self.screen, cars, time)
        pg.display.flip()

    def scene_tick(self, cars, time):
        if self.scene == Scene.main_menu: self.scene_obj.tick()
        elif self.scene == Scene.game: self.scene_obj.tick(cars, time)

    def scene_rescale(self): self.scene_obj.rescale()

    def scene_events(self, event): return self.scene_obj.events(event)

    def graphics_loop(self, cars=None, time=None):
        self.scene_tick(cars, time)
        pg.display.flip()

class MainMenu():
    def __init__(self, screen):
        self.screen = screen
        self.play = Button(self.screen, pos=(2, 2.66), text="PLAY")
        self.settings = Button(self.screen, pos=(2, 1.77), size_minus=1.2, text="SETTINGS")
        self.quit = Button(self.screen, pos=(2, 1.33), text="QUIT")

    def tick(self):
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
        if self.play.update(event): return [1, Scene.game]
        if self.quit.update(event): exit(0)

class Settings():
    pass

class CarGraphics():
    def __init__(self, screen, game, color_id, model, focus=True):
        self.model = model
        self.screen = screen
        self.game = game
        self.color_id = color_id
        self.focus = focus
        self.rotation = 0

    def tick(self, model, rotation):
        self.model = model
        self.rotation = rotation
        self.draw()

    def draw(self):
        self.car_image = pg.image.load(os.path.dirname(os.path.abspath(__file__))+f'/../static/car_{self.color_id}.png')
        self.car_image = pg.transform.scale(self.car_image, self.game.convert_passer([2, 4], 0))
        if not self.focus:
            self.car_image = pg.transform.rotate(self.car_image, float(np.degrees(self.model.car_angle))-float(np.degrees(self.rotation)))
        self.car_rect = self.car_image.get_rect(center=self.game.convert_passer(self.model.pos))
        self.screen.blit(self.car_image, self.car_rect)
        #pg.draw.line(self.screen, 'lime', self.game.convert_passer(self.model.pos), self.game.convert_passer(self.model.cl_points[self.model.target_cl_index]), 2)
        #pg.draw.line(self.screen, 'red', self.game.convert_passer(self.model.pos), self.game.convert_passer(self.model.point), 2)


class GameGraphics():
    TRACK_WIDTH = 6
    def __init__(self, screen, cars, time):
        self.screen = screen
        self.screen.fill((0,0,0))
        self.zoom = 0.05
        local_dir = os.path.dirname(__file__)
        with open(os.path.join(local_dir, 'center_points_08.pickle'), 'rb') as f: self.cent_line = pickle.load(f)
        with open(os.path.join(local_dir, 'parallel_points_01.pickle'), 'rb') as f: self.para_lines = pickle.load(f)
        self.cars = []
        self.car_graphics = []
        self.time_left = time
        focus = False
        for car in cars:
            self.cars.append(car["model"])
            self.car_graphics.append(CarGraphics(self.screen, self, car["color_id"], car["model"], car["focus"]))
            if car["focus"] == True:
                self.screen_center = car["model"].pos
                self.rotation = car["model"].car_angle
                self.speed = car["model"].speed*3600
                focus = True
        if not focus:
            self.screen_center = [120, 15]
            self.rotation = np.pi/2
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

    def tick(self, cars, time):
        self.time_left = time
        for car in cars:
            if car["focus"] == True:
                self.screen_center = car["model"].pos
                self.rotation = car["model"].car_angle
                self.speed = car["model"].speed*3600

        self.create_matrix()
        self.screen.fill((78, 217, 65))
        self.background()
        for i, graphic in enumerate(self.car_graphics):
            graphic.tick(self.cars[i], self.rotation)
        self.hud()

    def create_matrix(self):
        s_x, s_y = self.screen.get_size()
        rotate = np.array([[np.sin(self.rotation), (np.cos(self.rotation))], [-np.cos(self.rotation), np.sin(self.rotation)]], dtype=np.float64)
        self.rotation_matrix = rotate
        scale = np.array([[0, 0], [(s_x*(0.05208*self.zoom)), 0], [0, (s_y*(0.09259*self.zoom))]], dtype=np.float64)
        scale[0] = -np.matmul((1, *self.screen_center), scale)+(s_x/2, s_y/2)
        self.coord_conversion = scale

    def hud(self):
        w, h = self.screen.get_size()
        color = (255, 255, 255)
        info_bg = pg.image.load(os.path.dirname(os.path.abspath(__file__))+'/../static/button.png')
        speed_bg = pg.transform.scale(info_bg, (w/6, h/10))
        score_bg = pg.transform.scale(info_bg, (w/7, h/10))
        time_bg = pg.transform.scale(info_bg, (w/5, h/10))
        speed_bg_rect = speed_bg.get_rect(center=(w/10, h/1.1))
        score_bg_rect = score_bg.get_rect(center=(w/3.5, h/14))
        time_bg_rect = time_bg.get_rect(center=(w/9, h/14))
        t_font = pg.font.SysFont('arial', int(h/20))
        speed_text = t_font.render(f"{int(round(self.speed, 0))} KM/H", True, color)
        score_text = t_font.render("Score)", True, color)
        time_text = t_font.render(f"Time left) {int(self.time_left // 60)}:{int(round(self.time_left % 60, 0)):02d}", True, color)
        speed_text_rect = speed_text.get_rect(center=(w/10, h/1.1))
        score_text_rect = score_text.get_rect(center=(w/3.8, h/14))
        time_text_rect = time_text.get_rect(center=(w/9.3, h/14))
        self.screen.blit(speed_bg, speed_bg_rect)
        self.screen.blit(speed_text, speed_text_rect)
        self.screen.blit(score_bg, score_bg_rect)
        self.screen.blit(score_text, score_text_rect)
        self.screen.blit(time_bg, time_bg_rect)
        self.screen.blit(time_text, time_text_rect)



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

    def events(self, event): return None






