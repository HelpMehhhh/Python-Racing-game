import os.path
import pickle
import cars
from graphics import Graphics
from enum import IntEnum






FRAME_RATE = 60 
class Scene(IntEnum):
        main_menu = 0
        game = 1


class Main:
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), 'center_points_08.pickle'), 'rb') as f: self.cent_line = pickle.load(f)
        #self.player = {"model": cars.PlayerCar([0,0], self.cent_line), "color_id": 1, "focus": True}
        #self.ai_cars = [cars.AiCar()]
        #self.cars_graphics = [self.player, ]
        self.scene = Scene.main_menu
        self.game_loop()

    def car_init(self):
        
         
	
        
        
         
        
        
        

    def game_loop(self):
        self.graphics = Graphics(self.scene)
        while True:
            if self.scene == Scene.main_menu:
                s_event = self.graphics.graphics_loop()
            elif self.scene == Scene.game:
                s_event = self.graphics.graphics_loop(self.cars)
            if s_event:
                if s_event == Scene.game: self.car_init()
                self.scene = Scene(s_event)
            
            
                 









if __name__ is "__main__":
    game = Main()



