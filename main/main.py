import os.path
import pickle
import cars
from graphics import Graphics
from enum import IntEnum
from random import randrange
import pygame as pg






FRAME_RATE = 60
class Scene(IntEnum):
        main_menu = 0
        game = 1


class Main:
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), 'center_points_08.pickle'), 'rb') as f: self.cent_line = pickle.load(f)

        self.scene = Scene.main_menu
        self.ai_amount = 6


    def car_init(self):
        self.player = {"model": cars.PlayerCar([-4, -10], self.cent_line),"color_id": 1, "focus": True}
        ai_cars = []
        accel_deccel_values = [(10, 17), (11, 18), (12, 19), (13, 20), (14, 21), (16, 23), (18, 25)]
        for i in range(self.ai_amount):
            r = randrange(0, 7)
            accel = accel_deccel_values[r][0]
            deccel = accel_deccel_values[r][1]
            with open(os.path.dirname(os.path.abspath(__file__))+f'/../models/{accel}_{deccel}_genome.pickle', 'rb') as f: g = pickle.load(f)
            with open(os.path.dirname(os.path.abspath(__file__))+f'/../models/{accel}_{deccel}_config.pickle', 'rb') as f: conf = pickle.load(f)

            ai_cars.append(cars.AiCar([0, (r*2)*randrange(1, 8)+1], accel, deccel, g, conf, self.cent_line))
        self.cars_graphics = [self.player]
        self.cars_graphics.extend([{"model": car, "color_id": randrange(2, 7), "focus": False} for car in ai_cars])
        self.cars = [self.player["model"]]
        self.cars.extend(ai_cars)



    def game_loop(self):
        graphics = Graphics(self.scene)
        clock = pg.time.Clock()
        time_left = 310
        score = 0
        while True:
            t = clock.tick(FRAME_RATE)

            if self.scene == Scene.main_menu:
                graphics.graphics_loop()

            elif self.scene == Scene.game:
                time_left -= t/1000
                score = 0
                
                for i, car in enumerate(self.cars):
                    car.tick(17)
                    if i > 0: score += self.cars[0].distance // car.distance
                
                graphics.graphics_loop(self.cars_graphics, time_left, score)

            for event in pg.event.get():
                s_event = graphics.scene_events(event)
                if s_event:
                    if s_event[0] == 1:
                        graphics.scene = Scene(s_event[1])
                        if s_event[1] == 1:
                            self.car_init()
                            graphics.scene_chg(self.cars_graphics, time_left, score)
                        self.scene = Scene(s_event[1])
                    elif s_event[0] == 2:
                        #data collection here
                        pass

                if event.type in (pg.KEYDOWN, pg.KEYUP) and self.scene == Scene.game:
                    if event.key == pg.K_LEFT and graphics.scene_obj.zoom > 0.08: graphics.scene_obj.zoom -= 0.01
                    elif event.key == pg.K_RIGHT and graphics.scene_obj.zoom < 0.8: graphics.scene_obj.zoom += 0.01
                    else: self.cars[0].control(event)

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE: exit(0)
                    if event.key == pg.K_F11:
                        if graphics.fullscreen:
                            graphics.screen = pg.display.set_mode((graphics.SCREEN_WIDTH / 2, graphics.SCREEN_HEIGHT / 2), pg.RESIZABLE)
                            graphics.fullscreen = False
                        else:
                            graphics.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
                            graphics.fullscreen = True
                elif event.type == pg.QUIT: exit(0)
                elif event.type == pg.WINDOWRESIZED: graphics.scene_rescale()














if __name__ == "__main__":
    game = Main()
    game.game_loop()



