import os.path
import pickle
import cars
from graphics import Graphics
from enum import IntEnum
from random import randrange
from pygame import time






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
        self.player = {"model": cars.PlayerCar([0,0], self.cent_line),"color_id": 1, "focus": True}
        accel_values = [14, 15, 16, 17, 18, 19, 20]
        deccel_values = [21, 22, 23, 24, 25, 26, 27]
        local_dir = os.path.join(os.path.dirname(__file__))
        with open(os.path.join(local_dir, 'winner.pickle'), 'rb') as f: g = pickle.load(f)
        with open(os.path.join(local_dir, 'genome_config.pickle'), 'rb') as f: conf = pickle.load(f)

        
        ai_cars = [cars.AiCar([0, 8], accel_values[randrange(0, 7)], deccel_values[randrange(0, 7)], g, conf, self.cent_line) for x in range(self.ai_amount)]
        self.cars_graphics = [self.player, {"model": car,"color_id": randrange(2, 7), "focus": False} for car in ai_cars]
        self.cars = [self.player["model"]]
        self.cars.extend(ai_cars)
        
        
        
    def game_loop(self):
        self.graphics = Graphics(self.scene)
        clock = time.Clock
        while True:
            t = clock.tick(FRAME_RATE)
            if self.scene == Scene.main_menu:
                s_event = self.graphics.graphics_loop()
            elif self.scene == Scene.game:
                for car in self.cars:
                    car.tick(t)
                s_event = self.graphics.graphics_loop(self.cars_graphics)

            
            if s_event:
                if s_event[0] == 1: 
                    if s_event[1] == 1: 
                        self.car_init()
                        self.graphics.scene_chg(self.cars_graphics)
                    self.scene = Scene(s_event[1])
                elif s_event[0] == 2:
                    pass
                
            
            
                 









if __name__ is "__main__":
    game = Main()
    game.game_loop()



