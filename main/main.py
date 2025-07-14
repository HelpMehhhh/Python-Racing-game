import pygame as pg
import os.path
from button import Button
import sys
import numpy as np
from pygame import gfxdraw
import sympy as sym
from enum import IntEnum
import cProfile
import numba
from numba import jit

pg.init()

FRAME_RATE = 60


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
        self.rotation = 0
        self.zoom = 0.4
        self.Player = PlayerCar(self.screen, self, [0, 0])
        self.screen_center = self.Player.pos
        self.rescale()


    def generate_track_points(self):
        for points in self.BEZIER_POINTS:
            t = sym.Symbol('t')
            Bx = (1 - t)*((1 - t)*points[0][0] + t*points[1][0]) + t*((1 - t)*points[1][0] + t*points[2][0])
            By = (1 - t)*((1 - t)*points[0][1] + t*points[1][1]) + t*((1 - t)*points[1][1] + t*points[2][1])


            steps = (round(i * 0.05, 2) for i in range(21))
            for step in steps:
                self.RACETRACK_POINTS.append((round(Bx.subs(t, step), 3), round(By.subs(t, step), 3)))

    def convert_passer(self, gamev, ofssc = 1):
        npgamev = np.array([*gamev], dtype=np.float64)
        screen_center = np.array([*self.screen_center], dtype=np.float64)

        return self.convert(npgamev, screen_center, self.rotation_matrix, self.coord_conversion, ofssc)

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


    def redraw(self):
        self.Player.movement_calc()
        self.create_matrix()
        self.screen.fill((78, 217, 65))
        self.background()
        self.Player.redraw()
        self.rotation = self.Player.car_angle


    def create_matrix(self):
        s_x, s_y = self.screen.get_size()
        rotate = np.array([[np.cos(np.radians(self.rotation)), (np.sin(np.radians(self.rotation)))], [-np.sin(np.radians(self.rotation)), np.cos(np.radians(self.rotation))]], dtype=np.float64)
        self.rotation_matrix = rotate
        scale = np.array([[0, 0], [(s_x*(0.05208*self.zoom)), 0], [0, (s_y*(0.09259*self.zoom))]], dtype=np.float64)
        scale[0] = -np.matmul((1, *self.screen_center), scale)+(s_x/2, s_y/2)
        self.coord_conversion = scale


    def background(self):
        screen_points = []
        for point in self.RACETRACK_POINTS:
            screen_points.append(self.convert_passer(point))
        pg.gfxdraw.filled_polygon(self.screen, screen_points, (66, 66, 66))

    def rescale(self):
        self.create_matrix()
        self.background()

    def events(self, event):
        if event.type in (pg.KEYDOWN, pg.KEYUP):
            if event.key == pg.K_LEFT and self.zoom > 0.08:
                self.zoom -= 0.01
            if event.key == pg.K_RIGHT and self.zoom < 0.8:
                self.zoom += 0.01
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


            pg.display.flip()
            t = self.clock.tick(FRAME_RATE)
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
                elif event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.WINDOWRESIZED:
                    self.scene.rescale()



class Hud():
    def __init__(self):
        pass


    def speedometer(self):
        pass



class Car():
    class KeyState(IntEnum):
        left = 1
        center = 0
        right = -1
    class SpeedState(IntEnum):
        accel = 1
        const = 0
        deccel = -1

    
    
    #color id refers to how the car image files are named 1 through 6
    def __init__(self, screen, game, start_pos, color_id=1):
        self.screen = screen
        self.pos = start_pos
        self.color_id = color_id
        self.turning_angle = 0
        self.tire_direct = 0
        self.car_angle = 0
        self.prev_car_angle = 0
        self.speed = 0
        self.radius = 0
        self.game = game
        self.time_1_frame = round(1/FRAME_RATE, 4) #distance traveled in 1 tick
        self.clock = pg.time.Clock()
        self.turn_timer = 0
        self.keystate = self.KeyState.center
        self.speedstate = self.SpeedState.const
        self.a = 0

    def redraw(self):
        self.transform()
        self.car_rect = self.car.get_rect(center=self.game.convert_passer(self.pos))
        self.screen.blit(self.car, self.car_rect)

    def movement_calc(self):
        chg = 0.08*abs(self.turning_angle) + 0.01
        if self.speed > 0.116: chg *= 0.116/self.speed
        time_elapsed = self.clock.tick()
        if self.keystate == self.KeyState.center:
            if abs(self.turning_angle) > chg:
                self.turning_angle += chg if (self.turning_angle < 0) else -chg
            else:
                self.turning_angle = 0
        else:
            self.turning_angle += chg*self.keystate
            maxTurn = 0.5
            if self.speed > 0.116: maxTurn *= 0.116/self.speed
            if abs(self.turning_angle) > maxTurn:
                self.turning_angle = self.keystate * maxTurn

        if self.speedstate != self.SpeedState.const:
            if self.speedstate == self.SpeedState.deccel:
                self.speed -= time_elapsed*self.max_deccel
                if self.speed < 0: self.speed = 0
            elif self.speedstate == self.SpeedState.accel:
                self.speed += time_elapsed*self.max_accel

        
        self.car_angle += self.turning_angle*self.speed*time_elapsed

        self.pos[0] += self.speed*np.cos(np.radians(self.car_angle+90))
        self.pos[1] -= self.speed*np.sin(np.radians(self.car_angle+90))

        if self.car_angle >= 360: self.car_angle -= 360
        if self.car_angle <= -360: self.car_angle += 360

    def transform(self):
        self.car = pg.image.load(os.path.dirname(os.path.abspath(__file__))+f'/../static/car_{self.color_id}.png')
        self.car = pg.transform.scale(self.car, self.game.convert_passer([2, 4], 0))




class PlayerCar(Car):
    def __init__(self, screen, start_pos, color_id=1):
        Car.__init__(self, screen, start_pos, color_id)
        self.max_accel = 8/FRAME_RATE/1000 # 8 meters persecond persecond
        self.max_deccel = 20/FRAME_RATE/1000
        
        
        
    def control(self, event):
        if (event.type == pg.KEYUP):
            if (event.key in (pg.K_d, pg.K_a)):
                self.keystate = self.KeyState.center
            if (event.key in (pg.K_UP, pg.K_DOWN)):
                self.speedstate = self.SpeedState.const
        elif (event.type == pg.KEYDOWN):
            if (event.key == pg.K_d):
                self.keystate = self.KeyState.right
            elif (event.key == pg.K_a):
                self.keystate = self.KeyState.left
            if (event.key == pg.K_UP):
                self.speedstate = self.SpeedState.accel
            elif (event.key == pg.K_DOWN):
                self.speedstate = self.SpeedState.deccel





class AiCar(Car):
    def __init__(self, screen, start_pos, color_id, max_accel, max_deccel):
        Car.__init__(self, screen, start_pos, color_id)
        self.max_accel = max_accel/FRAME_RATE/1000 # 8 meters persecond persecond
        self.max_deccel = max_deccel/FRAME_RATE/1000


    def gasbrake(self):
        pass
    def steer(self, dir):
        pass

    
    

    




if __name__ == "__main__":
    #cProfile.run("Mainloop()", sort="cumtime")
    Mainloop()