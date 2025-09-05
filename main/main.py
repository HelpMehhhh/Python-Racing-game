#Main file, responsible for handaling the game states and running as a whole.

#Packages beign used in the program.
import os.path # For file handeling.
import pickle # Also For file handeling.
import cars # Car file where the code for the cars is stored.
from graphics import Graphics # Graphics class where the graphics is stored.
from enum import IntEnum # For defining game states as varibles without using
#strings.
from random import randrange # Random number generation
import pygame as pg # Pygame non graphics, used for event handaling and clock
#ticking.
import numpy as np # Advanced math library, makes number crunching faster and
#better.

#Game states as class objects for easier assignment and use.
class Scene(IntEnum):
        main_menu = 0
        game = 1
        game_over = 2
        settings = 3

#Main class where the game is ran.
class Main:
    #Constants for car hitbox dimensions as rectangle.
    CORNER_TO_CENTER_LEN = np.sqrt(0.8**2 + 1.8**2)
    CORNER_TO_CENTER_ANGLE = np.arctan(0.8/1.8)
    #Constant framerate.
    FRAME_RATE = 60

    #Main initializer, creates varibles with info about the game.
    def __init__(self):
        #File with points that make up the track center line, generated using
        #  trackMaker.py file with a 0.8 distance threshold.
        with open(os.path.join(os.path.dirname(__file__),
        'center_points_08.pickle'), 'rb') as f:
            self.cent_line = pickle.load(f)
        self.hitboxes = False
        self.scene = Scene.main_menu
        self.ai_amount = 6

    #Creates the player and ai car/cars list and their graphics information
    # when game is started.
    def car_init(self):
        # Model refers to the car class object, focus refers to wether the car
        # is centered on the screen (the one the player is viewing).
        self.player = {"model": cars.PlayerCar([-4, -10], self.cent_line),
        "color_id": 1, "focus": True}
        ai_cars = []
        accel_deccel_values = [(10, 17), (11, 18), (12, 19), (13, 20),
                               (14,21), (16, 23), (18, 25)]
        #Places the ai cars at random distances with random neural networks
        # infront of the player on the first straight.
        # Ai cars are nueral networks, trained using the Neat-python library/
        # method.
        for i in range(self.ai_amount):
            r = randrange(0, 7)
            accel = accel_deccel_values[r][0]
            deccel = accel_deccel_values[r][1]
            with open(os.path.dirname(os.path.abspath(__file__))+
            f'/../models/{accel}_{deccel}_genome.pickle', 'rb') as f:
                g = pickle.load(f)
            with open(os.path.dirname(os.path.abspath(__file__))+
            f'/../models/{accel}_{deccel}_config.pickle', 'rb') as f:
                conf = pickle.load(f)
            ai_cars.append(cars.AiCar([0, (r*2)*randrange(1, 8)+1], accel,
                                       deccel, g, conf, self.cent_line))

        self.cars_graphics = [self.player]
        self.cars_graphics.extend([{"model": car, "color_id": randrange(2, 7),
                                     "focus": False} for car in ai_cars])
        self.cars = [self.player["model"]]
        self.player_model = self.cars[0]
        self.cars.extend(ai_cars)

    #Resets certain game varibles when a new game is played.
    def reset(self):
        self.time_left = 310 #seconds
        self.score = 0
        self.highscore = False

    #Helper function that detects a collision between two cars (norm_car, car)
    #  by testing for overlap with hitbox vertacies.
    # Works by normalizing one of the cars position to (0,0) and angle to pi
    #  radians so that the width and height perfectly match up with the x,y
    #  axis, making it so that the collision calculation becomes a simple if
    #  statement.
    def _collision_test(self, norm_car, car):
        norm_angle = norm_car.car_angle - (car.car_angle - np.pi/2)
        if norm_angle > np.pi: norm_angle -= 2*np.pi
        if norm_angle < -np.pi: norm_angle += 2*np.pi
        norm_pos_vec = np.array(norm_car.pos) - np.array(car.pos)

        #top left, top right, bottom left, bottom right from car view.
        car_corners = [[norm_pos_vec[0]+np.cos(norm_angle+
        self.CORNER_TO_CENTER_ANGLE)*self.CORNER_TO_CENTER_LEN,
        norm_pos_vec[1]+np.sin(norm_angle+self.CORNER_TO_CENTER_ANGLE)*
        self.CORNER_TO_CENTER_LEN],
        [norm_pos_vec[0]+np.cos(norm_angle-self.CORNER_TO_CENTER_ANGLE)*
        self.CORNER_TO_CENTER_LEN,
        norm_pos_vec[1]+np.sin(norm_angle-self.CORNER_TO_CENTER_ANGLE)*
        self.CORNER_TO_CENTER_LEN],
        [norm_pos_vec[0]+np.cos((norm_angle-np.pi)-
        self.CORNER_TO_CENTER_ANGLE)*self.CORNER_TO_CENTER_LEN,
        norm_pos_vec[1]+np.sin((norm_angle-np.pi)-
        self.CORNER_TO_CENTER_ANGLE)*self.CORNER_TO_CENTER_LEN],
        [norm_pos_vec[0]+np.cos((norm_angle-np.pi)+
        self.CORNER_TO_CENTER_ANGLE)*self.CORNER_TO_CENTER_LEN,
        norm_pos_vec[1]+np.sin((norm_angle-np.pi)+
        self.CORNER_TO_CENTER_ANGLE)*self.CORNER_TO_CENTER_LEN]]
        for corner in car_corners:
            if (corner[0] > -0.8 and corner[0] < 0.8) and (corner[1] > -1.8
            and corner[1] < 1.8):
                return True

        return False

    #Main game loop, everything relating directly to the game is handeled
    #  within here.
    def game_loop(self):
        #Initializes the Game graphics object and game clock.
        graphics = Graphics(self.scene)
        clock = pg.time.Clock()
        self.reset()
        with open(os.path.join(os.path.dirname(__file__), 'highscore.pickle'),
        'rb') as f:
            high_score = pickle.load(f)

        #Main loop.
        while True:
            #Time since last tick in miliseconds.
            time_elapsed = clock.tick(self.FRAME_RATE)
            #Each scene has different things happening, so each is split into
            #  its own code block based on scene varible.
            # Main menu scene code.
            if self.scene == Scene.main_menu:
                graphics.graphics_loop()

            # Game scene code.
            elif self.scene == Scene.game:
                self.time_left -= time_elapsed/1000
                self.score = 0
                #Ticks every car, and updates their positions and data. Also
                #  checks for collisions, and changes the scene to game_over
                #  state if it is detected.
                for i, car in enumerate(self.cars):
                    car.tick(17)
                    #Updates each cars corner class varibles for hitbox
                    #  display.
                    if self.hitboxes: car.car_corners = [[car.pos[0]+
                    np.cos(car.car_angle+self.CORNER_TO_CENTER_ANGLE)*
                    self.CORNER_TO_CENTER_LEN,
                    car.pos[1]+np.sin(car.car_angle+
                    self.CORNER_TO_CENTER_ANGLE)*self.CORNER_TO_CENTER_LEN],
                    [car.pos[0]+np.cos(car.car_angle-
                    self.CORNER_TO_CENTER_ANGLE)*self.CORNER_TO_CENTER_LEN,
                    car.pos[1]+np.sin(car.car_angle-
                    self.CORNER_TO_CENTER_ANGLE)*self.CORNER_TO_CENTER_LEN],
                    [car.pos[0]+np.cos((car.car_angle-np.pi)-
                    self.CORNER_TO_CENTER_ANGLE)*self.CORNER_TO_CENTER_LEN,
                    car.pos[1]+np.sin((car.car_angle-np.pi)-
                    self.CORNER_TO_CENTER_ANGLE)*self.CORNER_TO_CENTER_LEN],
                    [car.pos[0]+np.cos((car.car_angle-np.pi)+
                    self.CORNER_TO_CENTER_ANGLE)*self.CORNER_TO_CENTER_LEN,
                    car.pos[1]+np.sin((car.car_angle-np.pi)+
                    self.CORNER_TO_CENTER_ANGLE)*self.CORNER_TO_CENTER_LEN]]
                    else: car.car_corners = [(0,0),(0,0),(0,0),(0,0)]

                    if i > 0:
                        self.score += self.cars[0].distance // car.distance
                        if self._collision_test(car,
                        self.player_model) or self._collision_test(
                        self.player_model, car):
                            graphics.scene = Scene.game_over
                            if self.score > high_score: self.highscore = True
                            graphics.scene_chg(score=self.score,
                            reason="You Hit a AI!", highscore=self.highscore)
                            self.scene = Scene.game_over
                            #Update highscore file if there is a new highscore.
                            if self.highscore:
                                with open(os.path.join(
                                os.path.dirname(__file__),
                                'highscore.pickle'), 'wb') as f:
                                    pickle.dump(self.score, f)

                #Game over if time reaches 0.
                if self.time_left < 0:
                    graphics.scene = Scene.game_over
                    if self.score > high_score: self.highscore = True
                    graphics.scene_chg(score=self.score,
                    reason="Time limit reached!", highscore=self.highscore)
                    self.scene = Scene.game_over
                    if self.highscore:
                        with open(os.path.join(os.path.dirname(__file__),
                        'highscore.pickle'), 'wb') as f:
                            pickle.dump(self.score, f)

                #Ticks the graphics.
                graphics.graphics_loop(cars=self.cars_graphics,
                time=self.time_left, score=self.score)

            #Game over scene.
            elif self.scene == Scene.game_over:
                graphics.graphics_loop()

            #Settings scene.
            elif self.scene == Scene.settings:
                graphics.graphics_loop(ai_amount=self.ai_amount,
                                       hitboxes=self.hitboxes)

            #Event handler, detects player key and mouse inputs and gets
            #  results from the different handlers.
            for event in pg.event.get():
                #s_event gets screen events, Ex: a on screen button click.
                s_event = graphics.scene_events(event)
                if s_event:
                    #If the returned event is a "scene change" event.
                    if s_event[0] == 1:
                        #Changes the scene on graphics file side.
                        graphics.scene = Scene(s_event[1])
                        #Runs if game scene.
                        if s_event[1] == Scene.game:
                            self.car_init()
                            self.reset()
                            graphics.scene_chg(cars=self.cars_graphics,
                            time=self.time_left, score=self.score)

                        #Runs if game over scene.
                        elif s_event[1] == Scene.game_over:
                            self.reset()
                            graphics.scene_chg()

                        #Runs if settings scene.
                        elif s_event[1] == Scene.settings:
                            graphics.scene_chg(ai_amount=self.ai_amount,
                            hitboxes=self.hitboxes)

                        #Changes scene on main file side.
                        self.scene = Scene(s_event[1])

                    #Else if the returned event is a data change, Ex: button
                    #  turning on hitboxes in settings.
                    elif s_event[0] == 2:
                        #Change in ai amount.
                        if s_event[1] == "ai_amount":
                            self.ai_amount += 1
                            if self.ai_amount > 16: self.ai_amount = 1

                        #Hitboxes on or off.
                        elif s_event[1] == "hitboxes":
                            self.hitboxes = True if not self.hitboxes \
                            else False

                        #Reset in highscore
                        elif s_event[1] == "reset_hs":
                            with open(os.path.join(os.path.dirname(__file__),
                            'highscore.pickle'), 'wb') as f:
                                pickle.dump(0, f)

                #If key is pressed, do certain actions.
                if event.type in (pg.KEYDOWN, pg.KEYUP) and\
                self.scene == Scene.game:
                    #Game control keys for zoom and player control
                    if event.key == pg.K_LEFT and\
                    graphics.scene_obj.zoom > 0.08:
                        graphics.scene_obj.zoom -= 0.01
                    elif event.key == pg.K_RIGHT and\
                    graphics.scene_obj.zoom < 0.8:
                        graphics.scene_obj.zoom += 0.01
                    else: self.cars[0].control(event)

                #Game control keys for window sizeing and exiting.
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE: exit(0)
                    if event.key == pg.K_F11:
                        if graphics.fullscreen:
                            graphics.screen = pg.display.set_mode((
                                graphics.SCREEN_WIDTH / 2,
                                graphics.SCREEN_HEIGHT / 2), pg.RESIZABLE)
                            graphics.fullscreen = False

                        else:
                            graphics.screen = pg.display.set_mode((0, 0),
                            pg.FULLSCREEN)
                            graphics.fullscreen = True

                elif event.type == pg.QUIT: exit(0)
                elif event.type == pg.WINDOWRESIZED: graphics.scene_rescale()


#Runs on file run, very top on callstack.
if __name__ == "__main__":
    #Creates the game object and enters the main loop.
    game = Main()
    game.game_loop()