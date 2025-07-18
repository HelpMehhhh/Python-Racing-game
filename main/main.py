import pygame as pg
import os.path
from button import Button
import sys
import numpy as np
from pygame import gfxdraw
import sympy as sym
from enum import IntEnum
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
    def __init__(self, screen):
        self.screen = screen
        self.screen.fill((0,0,0))
        self.rotation = 0
        self.zoom = 0.4
        self.player = PlayerCar(self.screen, self, [0, 0.5])
        self.cars = [self.player, AiCar(self.screen, self, [0, -10], 2, 5, 5), AiCar(self.screen, self, [3, 0], 2, 5, 5), AiCar(self.screen, self, [-3, 0], 3, 5, 5), AiCar(self.screen, self, [3, 6], 4, 5, 5), AiCar(self.screen, self, [-3, 6], 5, 5, 5), AiCar(self.screen, self, [0, 7], 6, 5, 5)]
        self.screen_center = self.player.pos
        self.rescale()


    def convert_passer(self, gamev, ofssc = 1):
        npgamev = np.array([*gamev], dtype=np.float64)
        screen_center = np.array([*self.screen_center], dtype=np.float64)

        result = self.convert(npgamev, screen_center, self.rotation_matrix, self.coord_conversion, ofssc)
        if ofssc:
            return (result[0],pg.display.Info().current_h - result[1])
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
        screen_points = []
        points = [(0, 0), (0, 100), (0.312500000000000, 103.515625000000), (1.25000000000000, 106.562500000000), (2.81250000000000, 109.140625000000), (5.00000000000000, 111.250000000000), (7.81250000000000, 112.890625000000), (11.2500000000000, 114.062500000000), (15.3125000000000, 114.765625000000), (20, 115), (22.4218750000000, 114.902343750000), (24.6875000000000, 114.609375000000), (26.7968750000000, 114.121093750000), (28.7500000000000, 113.437500000000), (30.5468750000000, 112.558593750000), (32.1875000000000, 111.484375000000), (33.6718750000000, 110.214843750000), (35.0000000000000, 108.750000000000), (36.1718750000000, 107.089843750000), (37.1875000000000, 105.234375000000), (38.0468750000000, 103.183593750000), (38.7500000000000, 100.937500000000), (39.6875000000000, 95.8593750000000), (40, 90), (39.6875000000000, 83.1250000000000), (39.2968750000000, 80.1562500000000), (38.7500000000000, 77.5000000000000), (38.0468750000000, 75.1562500000000), (37.1875000000000, 73.1250000000000), (36.1718750000000, 71.4062500000000), (35, 70), (31.7968750000000, 67.5000000000000), (30.6054687500000, 66.2500000000000), (29.6875000000000, 65.0000000000000), (29.0429687500000, 63.7500000000000), (28.6718750000000, 62.5000000000000), (28.5742187500000, 61.2500000000000), (28.7500000000000, 60.0000000000000), (29.1992187500000, 58.7500000000000), (29.9218750000000, 57.5000000000000), (30.9179687500000, 56.2500000000000), (32.1875000000000, 55.0000000000000), (35.5468750000000, 52.5000000000000), (40, 50), (43.8281250000000, 48.2421875000000), (47.8125000000000, 46.7187500000000), (51.9531250000000, 45.4296875000000), (56.2500000000000, 44.3750000000000), (60.7031250000000, 43.5546875000000), (65.3125000000000, 42.9687500000000), (70.0781250000000, 42.6171875000000), (75.0000000000000, 42.5000000000000), (80.0781250000000, 42.6171875000000), (85.3125000000000, 42.9687500000000), (90.7031250000000, 43.5546875000000), (96.2500000000000, 44.3750000000000), (107.812500000000, 46.7187500000000), (120, 50), (129.062500000000, 53.7500000000000), (132.890625000000, 55.6250000000000), (136.250000000000, 57.5000000000000), (139.140625000000, 59.3750000000000), (141.562500000000, 61.2500000000000), (143.515625000000, 63.1250000000000), (145.000000000000, 65.0000000000000), (146.015625000000, 66.8750000000000), (146.562500000000, 68.7500000000000), (146.640625000000, 70.6250000000000), (146.250000000000, 72.5000000000000), (145.390625000000, 74.3750000000000), (144.062500000000, 76.2500000000000), (142.265625000000, 78.1250000000000), (140, 80), (136.093750000000, 83.4375000000000), (131.875000000000, 86.2500000000000), (127.343750000000, 88.4375000000000), (122.500000000000, 90.0000000000000), (117.343750000000, 90.9375000000000), (111.875000000000, 91.2500000000000), (106.093750000000, 90.9375000000000), (100, 90), (90.7812500000000, 89.1406250000000), (83.1250000000000, 89.0625000000000), (79.8828125000000, 89.3164062500000), (77.0312500000000, 89.7656250000000), (74.5703125000000, 90.4101562500000), (72.5000000000000, 91.2500000000000), (70.8203125000000, 92.2851562500000), (69.5312500000000, 93.5156250000000), (68.6328125000000, 94.9414062500000), (68.1250000000000, 96.5625000000000), (68.0078125000000, 98.3789062500000), (68.2812500000000, 100.390625000000), (68.9453125000000, 102.597656250000), (70, 105), (71.3437500000000, 106.609375000000), (73.3750000000000, 107.937500000000), (76.0937500000000, 108.984375000000), (79.5000000000000, 109.750000000000), (83.5937500000000, 110.234375000000), (88.3750000000000, 110.437500000000), (93.8437500000000, 110.359375000000), (100, 110), (112.343750000000, 108.515625000000), (124.375000000000, 106.562500000000), (136.093750000000, 104.140625000000), (147.500000000000, 101.250000000000), (158.593750000000, 97.8906250000000), (169.375000000000, 94.0625000000000), (179.843750000000, 89.7656250000000), (190, 85), (195.468750000000, 82.5781250000000), (199.375000000000, 80.3125000000000), (200.742187500000, 79.2382812500000), (201.718750000000, 78.2031250000000), (202.304687500000, 77.2070312500000), (202.500000000000, 76.2500000000000), (202.304687500000, 75.3320312500000), (201.718750000000, 74.4531250000000), (200.742187500000, 73.6132812500000), (199.375000000000, 72.8125000000000), (195.468750000000, 71.3281250000000), (190, 70), (185.625000000000, 68.6718750000000), (182.500000000000, 67.1875000000000), (181.406250000000, 66.3867187500000), (180.625000000000, 65.5468750000000), (180.156250000000, 64.6679687500000), (180.000000000000, 63.7500000000000), (180.156250000000, 62.7929687500000), (180.625000000000, 61.7968750000000), (181.406250000000, 60.7617187500000), (182.500000000000, 59.6875000000000), (185.625000000000, 57.4218750000000), (190, 55), (192.500000000000, 53.9843750000000), (195.000000000000, 53.4375000000000), (197.500000000000, 53.3593750000000), (200.000000000000, 53.7500000000000), (202.500000000000, 54.6093750000000), (205.000000000000, 55.9375000000000), (207.500000000000, 57.7343750000000), (210, 60), (211.328125000000, 61.1718750000000), (212.812500000000, 62.1875000000000), (214.453125000000, 63.0468750000000), (216.250000000000, 63.7500000000000), (220.312500000000, 64.6875000000000), (225.000000000000, 65.0000000000000), (230.312500000000, 64.6875000000000), (236.250000000000, 63.7500000000000), (242.812500000000, 62.1875000000000), (250, 60), (252.187500000000, 59.1093750000000), (253.750000000000, 57.9375000000000), (254.687500000000, 56.4843750000000), (255.000000000000, 54.7500000000000), (254.687500000000, 52.7343750000000), (253.750000000000, 50.4375000000000), (252.187500000000, 47.8593750000000), (250, 45), (247.109375000000, 42.6562500000000), (243.437500000000, 40.6250000000000), (238.984375000000, 38.9062500000000), (233.750000000000, 37.5000000000000), (227.734375000000, 36.4062500000000), (220.937500000000, 35.6250000000000), (213.359375000000, 35.1562500000000), (205, 35), (201.992187500000, 34.9023437500000), (199.218750000000, 34.6093750000000), (196.679687500000, 34.1210937500000), (194.375000000000, 33.4375000000000), (192.304687500000, 32.5585937500000), (190.468750000000, 31.4843750000000), (188.867187500000, 30.2148437500000), (187.500000000000, 28.7500000000000), (186.367187500000, 27.0898437500000), (185.468750000000, 25.2343750000000), (184.804687500000, 23.1835937500000), (184.375000000000, 20.9375000000000), (184.179687500000, 18.4960937500000), (184.218750000000, 15.8593750000000), (184.492187500000, 13.0273437500000), (185, 10), (185.507812500000, 8.16406250000000), (185.781250000000, 6.40625000000000), (185.820312500000, 4.72656250000000), (185.625000000000, 3.12500000000000), (185.195312500000, 1.60156250000000), (184.531250000000, 0.156250000000000), (183.632812500000, -1.21093750000000), (182.500000000000, -2.50000000000000), (181.132812500000, -3.71093750000000), (179.531250000000, -4.84375000000000), (175.625000000000, -6.87500000000000), (170.781250000000, -8.59375000000000), (165, -10), (162.031250000000, -10.4492187500000), (159.375000000000, -10.5468750000000), (157.031250000000, -10.2929687500000), (155.000000000000, -9.68750000000000), (153.281250000000, -8.73046875000000), (151.875000000000, -7.42187500000000), (150.781250000000, -5.76171875000000), (150.000000000000, -3.75000000000000), (149.531250000000, -1.38671875000000), (149.375000000000, 1.32812500000000), (149.531250000000, 4.39453125000000), (150.000000000000, 7.81250000000000), (150.781250000000, 11.5820312500000), (151.875000000000, 15.7031250000000), (155, 25), (156.660156250000, 29.1406250000000), (157.890625000000, 32.8125000000000), (158.691406250000, 36.0156250000000), (159.062500000000, 38.7500000000000), (159.003906250000, 41.0156250000000), (158.515625000000, 42.8125000000000), (157.597656250000, 44.1406250000000), (156.250000000000, 45.0000000000000), (154.472656250000, 45.3906250000000), (152.265625000000, 45.3125000000000), (149.628906250000, 44.7656250000000), (146.562500000000, 43.7500000000000), (143.066406250000, 42.2656250000000), (139.140625000000, 40.3125000000000), (130, 35), (127.218750000000, 32.7031250000000), (124.875000000000, 29.8125000000000), (122.968750000000, 26.3281250000000), (121.500000000000, 22.2500000000000), (120.468750000000, 17.5781250000000), (119.875000000000, 12.3125000000000), (119.718750000000, 6.45312500000000), (120, 0), (119.843750000000, -7.10937500000000), (119.375000000000, -13.4375000000000), (118.593750000000, -18.9843750000000), (117.500000000000, -23.7500000000000), (116.093750000000, -27.7343750000000), (114.375000000000, -30.9375000000000), (112.343750000000, -33.3593750000000), (111.210937500000, -34.2773437500000), (110.000000000000, -35.0000000000000), (108.710937500000, -35.5273437500000), (107.343750000000, -35.8593750000000), (104.375000000000, -35.9375000000000), (101.093750000000, -35.2343750000000), (97.5000000000000, -33.7500000000000), (93.5937500000000, -31.4843750000000), (89.3750000000000, -28.4375000000000), (84.8437500000000, -24.6093750000000), (80, -20), (76.9140625000000, -17.7734375000000), (73.9062500000000, -16.0937500000000), (70.9765625000000, -14.9609375000000), (68.1250000000000, -14.3750000000000), (65.3515625000000, -14.3359375000000), (62.6562500000000, -14.8437500000000), (60.0390625000000, -15.8984375000000), (57.5000000000000, -17.5000000000000), (55.0390625000000, -19.6484375000000), (52.6562500000000, -22.3437500000000), (50.3515625000000, -25.5859375000000), (48.1250000000000, -29.3750000000000), (45.9765625000000, -33.7109375000000), (43.9062500000000, -38.5937500000000), (41.9140625000000, -44.0234375000000), (40, -50), (37.4218750000000, -57.1093750000000), (34.6875000000000, -63.4375000000000), (31.7968750000000, -68.9843750000000), (28.7500000000000, -73.7500000000000), (25.5468750000000, -77.7343750000000), (22.1875000000000, -80.9375000000000), (18.6718750000000, -83.3593750000000), (15.0000000000000, -85.0000000000000), (11.1718750000000, -85.8593750000000), (7.18750000000000, -85.9375000000000), (3.04687500000000, -85.2343750000000), (-1.25000000000000, -83.7500000000000), (-5.70312500000000, -81.4843750000000), (-10.3125000000000, -78.4375000000000), (-15.0781250000000, -74.6093750000000), (-20, -70), (-24.5312500000000, -65.1562500000000), (-28.1250000000000, -60.6250000000000), (-30.7812500000000, -56.4062500000000), (-32.5000000000000, -52.5000000000000), (-33.0078125000000, -50.6640625000000), (-33.2812500000000, -48.9062500000000), (-33.3203125000000, -47.2265625000000), (-33.1250000000000, -45.6250000000000), (-32.6953125000000, -44.1015625000000), (-32.0312500000000, -42.6562500000000), (-31.1328125000000, -41.2890625000000), (-30, -40), (-19.8125000000000, -30.9375000000000), (-12.2500000000000, -23.7500000000000), (-7.31250000000000, -18.4375000000000), (-5.82812500000000, -16.4843750000000), (-5, -15), (-2.81250000000000, -10.3125000000000), (-1.25000000000000, -6.25000000000000), (-0.312500000000000, -2.81250000000000), (0,0)]
        for point in points:
            screen_points.append(self.convert_passer(point))
        c=0
        print(len(screen_points))
        for i, point in enumerate(screen_points):
            if i == 306: break
            if i % 2 != 0: continue
            else:
                c +=1

                pg.draw.line(self.screen, (255,255,255), point, screen_points[i+1], 3)



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
        self.pos[1] += self.speed*np.sin(np.radians(self.car_angle+90))

        if self.car_angle >= 360: self.car_angle -= 360
        if self.car_angle <= -360: self.car_angle += 360

    def transform(self):
        self.car = pg.image.load(os.path.dirname(os.path.abspath(__file__))+f'/../static/car_{self.color_id}.png')
        self.car = pg.transform.scale(self.car, self.game.convert_passer([2, 4], 0))




class PlayerCar(Car):
    def __init__(self, screen, game, start_pos, color_id=1):
        Car.__init__(self, screen, game, start_pos, color_id)
        self.max_accel = 8/FRAME_RATE/1000 # 8 meters persecond persecond
        self.max_deccel = 20/FRAME_RATE/1000


    def redraw(self, rotation):
        self.transform()
        super().redraw()

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
            pg.draw.line(self.screen, color[i], self.game.convert_passer(self.pos), self.game.convert_passer((x, y)), 2)


    def check_collision(self):
        pass

    def gasbrake(self, choice):
        pass

    def steer(self, choice):
        pass









if __name__ == "__main__":
    #cProfile.run("Mainloop()", sort="cumtime")
    Mainloop()