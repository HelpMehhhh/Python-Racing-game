import pygame as pg
import os.path
from button import Button
import sys
import numpy as np
from pygame import gfxdraw
import sympy as sym
from enum import IntEnum
from numba import jit
import pickle

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
    def __init__(self, screen):
        self.screen = screen
        self.screen.fill((0,0,0))
        self.rotation = 0
        self.zoom = 0.4
        with open('center_points_1.pickle', 'rb') as f:
            self.cent_line = pickle.load(f)
        with open('parallel_points_01.pickle', 'rb') as f:
            self.para_lines = pickle.load(f)
        self.player = PlayerCar(self.screen, self, [0, 0.5])
        self.cars = [self.player]
        #, AiCar(self.screen, self, [0, -10], 2, 5, 5), AiCar(self.screen, self, [3, 0], 2, 5, 5), AiCar(self.screen, self, [-3, 0], 3, 5, 5), AiCar(self.screen, self, [3, 6], 4, 5, 5), AiCar(self.screen, self, [-3, 6], 5, 5, 5), AiCar(self.screen, self, [0, 7], 6, 5, 5)
        self.screen_center = self.player.pos
        self.rescale()


    def convert_passer(self, gamev, ofssc = 1):
        npgamev = np.array([*gamev], dtype=np.float64)
        screen_center = np.array([*self.screen_center], dtype=np.float64)

        result = self.convert(npgamev, screen_center, self.rotation_matrix, self.coord_conversion, ofssc)
        if ofssc:
            return (result[0], pg.display.Info().current_h - result[1])
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


    def redraw(self):
        for car in self.cars: car.movement_calc()
        self.create_matrix()
        self.screen.fill((78, 217, 65))
        self.background()
        for car in self.cars: car.redraw(self.rotation)
        self.rotation = -self.player.car_angle


    def create_matrix(self):
        s_x, s_y = self.screen.get_size()
        rotate = np.array([[np.cos(np.radians(self.rotation)), (np.sin(np.radians(self.rotation)))], [-np.sin(np.radians(self.rotation)), np.cos(np.radians(self.rotation))]], dtype=np.float64)
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
        pg.draw.lines(self.screen, (255,255,255), False, cent_line_screen, 5)







    def rescale(self):
        self.create_matrix()
        self.background()


    def events(self, event):
        if event.type in (pg.KEYDOWN, pg.KEYUP):
            if event.key == pg.K_LEFT and self.zoom > 0.08:
                self.zoom -= 0.01
            if event.key == pg.K_RIGHT and self.zoom < 0.8:
                self.zoom += 0.01
            self.player.control(event)






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

                if event.type == pg.KEYDOWN:
                    pass
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
                    if event.key == pg.K_9:
                        pass
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
    class SteerState(IntEnum):
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
        self.steerstate = self.SteerState.center
        self.speedstate = self.SpeedState.const
        self.a = 0
        self.tt = 0.005
        self.tspeed = 0

    def redraw(self):
        self.car_rect = self.car.get_rect(center=self.game.convert_passer(self.pos))
        self.screen.blit(self.car, self.car_rect)

    def movement_calc(self):
        chg = 0.05*abs(self.turning_angle) + 0.1
        #if self.speed > self.tt: chg *= self.tt/self.speed
        time_elapsed = self.clock.tick()
        if self.steerstate == self.SteerState.center:
            
            if abs(self.turning_angle) > chg:
                self.turning_angle += chg if (self.turning_angle < 0) else -chg
            else:
                self.turning_angle = 0
        else:
            
            self.turning_angle += chg*self.steerstate
            if self.turning_angle > 70 or self.turning_angle < -70: self.turning_angle = float(70*np.sign(self.turning_angle))
        if self.speedstate != self.SpeedState.const:
            if self.speedstate == self.SpeedState.deccel:
                self.speed -= time_elapsed*self.max_deccel
                if self.speed < 0: self.speed = 0
            elif self.speedstate == self.SpeedState.accel:
                self.speed += time_elapsed*self.max_accel
        print(self.turning_angle)
        if self.turning_angle != 0:
            radius = np.sqrt((((2/np.tan(self.turning_angle))+1)**2)+1)
            #print(radius)

        else: radius = 0
        max_speed = np.sqrt(radius*19.62)/1000
        if self.speed > max_speed:
            radius = ((self.speed*1000)**2)/19.62
            
        
        d_angle = np.sign(self.turning_angle)*((self.speed/radius)*time_elapsed) if radius != 0 else 0
        self.car_angle += float(np.degrees(d_angle))
        

        self.pos[0] += time_elapsed*self.speed*np.cos(np.radians(self.car_angle+90))
        self.pos[1] += time_elapsed*self.speed*np.sin(np.radians(self.car_angle+90))

        if self.car_angle >= 360: self.car_angle -= 360
        if self.car_angle <= -360: self.car_angle += 360

    def transform(self):
        self.car = pg.image.load(os.path.dirname(os.path.abspath(__file__))+f'/../static/car_{self.color_id}.png')
        self.car = pg.transform.scale(self.car, self.game.convert_passer([2, 4], 0))




class PlayerCar(Car):
    def __init__(self, screen, game, start_pos, color_id=1):
        Car.__init__(self, screen, game, start_pos, color_id)
        self.max_accel = 16/1000000
        self.max_deccel = 30/1000000


    def redraw(self, rotation):
        self.transform()
        super().redraw()

    def control(self, event):
        if (event.type == pg.KEYUP):
            if (event.key in (pg.K_d, pg.K_a)):
                self.steerstate = self.SteerState.center
            if (event.key in (pg.K_UP, pg.K_DOWN)):
                self.speedstate = self.SpeedState.const
        elif (event.type == pg.KEYDOWN):
            if (event.key == pg.K_d):
                self.steerstate = self.SteerState.right
            elif (event.key == pg.K_a):
                self.steerstate = self.SteerState.left
            if (event.key == pg.K_UP):
                self.speedstate = self.SpeedState.accel
            elif (event.key == pg.K_DOWN):
                self.speedstate = self.SpeedState.deccel





class AiCar(Car):
    def __init__(self, screen, game, start_pos, color_id, max_accel, max_deccel):
        Car.__init__(self, screen, game, start_pos, color_id)
        self.max_accel = max_accel/FRAME_RATE/1000 # 8 meters persecond persecond
        self.max_deccel = max_deccel/FRAME_RATE/1000


    def redraw(self, rotation):
        self.transform(rotation)
        super().redraw()
        self.tick_radar()

    def transform(self, rotation):
        super().transform()
        self.car = pg.transform.rotate(self.car, rotation - self.car_angle)



    def render_radar(self):
        pass

    def tick_radar(self):
        for i, degree in enumerate([-80, -40, 0, 40, 80]):
            length = 4
            x =  self.pos[0] + (np.sin(np.radians(degree + self.car_angle)) * length)
            y =  self.pos[1] - (np.cos(np.radians(degree + self.car_angle)) * length)


            color = ['red', 'green', 'blue', 'yellow', 'orange']



    def check_collision(self):
        pass

    def gasbrake(self, choice):
        pass

    def steer(self, choice):
        pass









if __name__ == "__main__":
    #cProfile.run("Mainloop()", sort="cumtime")
    Mainloop()