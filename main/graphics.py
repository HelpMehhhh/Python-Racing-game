#Graphics file responsible for all graphics related things.

#Packages beign used in the program.
from button import Button # Simple helper file for a simple button.
import pygame as pg # Pygame for graphics and window rendering.
import os.path # For file handeling.
from sys import exit # For program exiting.
import pickle #Packages beign used in the program.
import numpy as np # Advanced math library, makes number crunching faster and
#better.
from numba import jit # For compiling number heavy python code to machine code
#that can work at runtime, speeding up the program by alot.
from pygame import gfxdraw # For drawing the track as a filled polygon
from enum import IntEnum #For defining game states as varibles without using
#strings.

#Game states as class objects for easier assignment and use.
class Scene(IntEnum):
        main_menu = 0
        game = 1
        game_over = 2
        settings = 3

#Main graphics class
class Graphics():

    # Main Init, creates window object and configures it and the scene.
    def __init__(self, scene, cars=None):
        pg.init()
        self.SCREEN_WIDTH = pg.display.Info().current_w
        self.SCREEN_HEIGHT = pg.display.Info().current_h
        icon = pg.image.load(os.path.dirname(os.path.abspath(__file__))
                             +'/../static/game_icon.png')
        pg.display.set_icon(icon)
        self.menu_bg = pg.image.load(os.path.dirname(os.path.abspath\
                            (__file__))+'/../static/crappy_bg.png')
        self.fullscreen = True
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        if scene == Scene.main_menu:
            self.scene_obj = MainMenu(self.screen)

        # If statement used only when training ai with graphics without having
        #  to go through the main menu.
        elif scene == Scene.game:
            self.scene_obj = GameGraphics(self.screen, cars)

        self.scene = scene
        self.scene_rescale()

    #Function that handles scene changes, called from main file when on screen
    #  events happen
    def scene_chg(self, cars=None, time=None, score=None, reason=None,
                   highscore=None, ai_amount=None, hitboxes=None):
        if self.scene == Scene.main_menu:
            self.scene_obj = MainMenu(self.screen)

        elif self.scene == Scene.game:
            self.scene_obj = GameGraphics(self.screen, cars, time, score)

        elif self.scene == Scene.game_over:
            self.scene_obj = GameOver(self.screen, score, reason, highscore)

        elif self.scene == Scene.settings:
            self.scene_obj = Settings(self.screen, ai_amount, hitboxes)

        pg.display.flip()

    # Ticks the current scene object with spesific game information provided
    #  by main file.
    def scene_tick(self, cars, time, score, ai_amount, hitboxes):
        if self.scene == Scene.main_menu: self.scene_obj.tick()
        elif self.scene == Scene.game: self.scene_obj.tick(cars, time, score)
        elif self.scene == Scene.game_over: self.scene_obj.tick()
        elif self.scene == Scene.settings:
            self.scene_obj.tick(ai_amount, hitboxes)

    # Rescales the current scene, ex: when exiting fullscreen.
    def scene_rescale(self): self.scene_obj.rescale()

    # Gets on screen events from the current scene.
    def scene_events(self, event): return self.scene_obj.events(event)

    # Main caller from main file, calls a tick on the scene and updates the
    #  window.
    def graphics_loop(self, cars=None, time=None, score=None, ai_amount=None,
                       hitboxes=None):
        self.scene_tick(cars, time, score, ai_amount, hitboxes)
        pg.display.flip()

# Game over scene.
class GameOver():
    def __init__(self, screen, score, reason, highscore):
        self.score = int(score)
        self.reason = reason
        self.screen = screen
        self.screen.fill((0,0,0))
        self.x, self.y = self.screen.get_size()
        self.re_play = Button(self.screen, pos=(2, 1.77), text="PLAY AGAIN")
        self.main_menu = Button(self.screen, pos=(2, 1.33), text="MAIN MENU")
        self.highscore = highscore


    def text(self):
        l_font = pg.font.SysFont('arial', int(self.y/8))
        font = pg.font.SysFont('arial', int(self.y/15))
        game_over_text = l_font.render("GAME OVER!", True, (255,255,255))
        reason_text = font.render(f"{self.reason}, Final score: {self.score}",
        True, (255,255,255))
        game_over_text_rect = game_over_text.get_rect(center=(self.x/2, self.y/
                                                              12))
        reason_text_rect = reason_text.get_rect(center=(self.x/2, self.y/5))
        if self.highscore:
            highscore_text = font.render("NEW HIGHSCORE RECORDED!", True, (255,
                                        255,255))
            highscore_text_rect = highscore_text.get_rect(center=(self.x/2,
            self.y/3))
            self.screen.blit(highscore_text, highscore_text_rect)

        self.screen.blit(game_over_text, game_over_text_rect)
        self.screen.blit(reason_text, reason_text_rect)

    def tick(self):
        self.text()
        self.re_play.update()
        self.main_menu.update()

    def rescale(self):
        self.screen.fill((0,0,0))
        self.x, self.y = self.screen.get_size()
        self.text()
        self.re_play.rescale()
        self.main_menu.rescale()

    def events(self, event):
        if self.re_play.update(event): return [1, Scene.game]
        if self.main_menu.update(event): return [1, Scene.main_menu]


# Main menu scene.
class MainMenu():
    def __init__(self, screen):
        self.screen = screen
        self.play = Button(self.screen, pos=(2, 2.66), text="PLAY")
        self.settings = Button(self.screen, pos=(2, 1.77), size_minus=1.2,
        text="SETTINGS")
        self.quit = Button(self.screen, pos=(2, 1.33), text="QUIT")
        self.x, self.y = self.screen.get_size()
        with open(os.path.join(os.path.dirname(__file__), 'highscore.pickle'),
        'rb') as f:
            self.high_score = pickle.load(f)
        self.rescale()

    def tick(self):
        self.screen.blit(self.menu_bg, (0,0))

        font = pg.font.SysFont('arial', int(self.y/20))
        hs_text = font.render(f"Current Highscore: {int(self.high_score)}",
        True, (255,255,255))
        hs_text_rect = hs_text.get_rect(center=(self.x/2, self.y/1.1))
        self.screen.blit(hs_text, hs_text_rect)
        self.play.update()
        self.quit.update()
        self.settings.update()

    def rescale(self):
        self.x, self.y = self.screen.get_size()
        self.menu_bg = pg.image.load(os.path.dirname(os.path.abspath(__file__))
                                     +'/../static/crappy_bg.png')
        self.menu_bg = pg.transform.scale(self.menu_bg, self.screen.get_size())
        self.play.rescale()
        self.settings.rescale()
        self.quit.rescale()

    def events(self, event):
        if self.play.update(event): return [1, Scene.game]
        if self.settings.update(event): return [1, Scene.settings]
        if self.quit.update(event): exit(0)

# Settings scene
class Settings():
    def __init__(self, screen, ai_amount, hitboxes):
        self.screen = screen
        self.screen.fill((0,255,0))
        self.x, self.y = self.screen.get_size()
        self.ai_amount = ai_amount
        self.hitboxes = hitboxes
        self.main_menu = Button(self.screen, pos=(2, 1.33), text="MAIN MENU")
        self.hitboxs_btn = Button(self.screen, pos=(4, 2), text="Hitboxes")
        self.ai_amount_btn = Button(self.screen, pos=(4, 3), text="Ai Amount")
        self.reset_hs_btn = Button(self.screen, size_minus=1.5, pos=(4, 5.5),
        text="Reset Highscore")


    def text(self):
        l_font = pg.font.SysFont('arial', int(self.y/8))
        ai_count = l_font.render(f"{self.ai_amount} (16 max)", True, (255,0,0))
        ai_count_rect = ai_count.get_rect(center=(self.x/1.5, self.y/3))
        self.screen.blit(ai_count, ai_count_rect)
        hitbox_text = "Hitboxes are on" if self.hitboxes\
        else "Hitboxes are off"
        hitbox = l_font.render(f"{hitbox_text}", True, (255,0,0))
        hitbox_rect = hitbox.get_rect(center=(self.x/1.5, self.y/2))
        self.screen.blit(hitbox, hitbox_rect)


    def tick(self, ai_amount, hitboxes):
        self.screen.fill((0,255,0))
        self.ai_amount = ai_amount
        self.hitboxes = hitboxes
        self.text()
        self.main_menu.update()
        self.hitboxs_btn.update()
        self.ai_amount_btn.update()
        self.reset_hs_btn.update()

    def rescale(self):
        self.screen.fill((0,255,0))
        self.x, self.y = self.screen.get_size()
        self.main_menu.rescale()

    def events(self, event):
        if self.main_menu.update(event): return [1, Scene.main_menu]
        if self.hitboxs_btn.update(event): return [2, "hitboxes"]
        if self.ai_amount_btn.update(event): return [2, "ai_amount"]
        if self.reset_hs_btn.update(event): return [2, "reset_hs"]

# Car graphics object class
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
        self.car_image = pg.image.load(os.path.dirname(os.path.abspath
        (__file__))+f'/../static/car_{self.color_id}.png')
        self.car_image = pg.transform.scale(self.car_image,
        self.game.convert_passer([2, 4], 0))
        if not self.focus:
            self.car_image = pg.transform.rotate(self.car_image,
            float(np.degrees(self.model.car_angle))-float(np.degrees(
                self.rotation)))

        self.car_rect = self.car_image.get_rect(
            center=self.game.convert_passer(self.model.pos))
        self.screen.blit(self.car_image, self.car_rect)


#Main game graphics (track and cars and extras)
class GameGraphics():
    TRACK_WIDTH = 6
    def __init__(self, screen, cars, time, score):
        self.screen = screen
        self.screen.fill((0,0,0))
        self.zoom = 0.05
        self.score = score
        local_dir = os.path.dirname(__file__)
        with open(os.path.join(local_dir, 'center_points_08.pickle'),
        'rb') as f:
            self.cent_line = pickle.load(f)
        with open(os.path.join(local_dir, 'parallel_points_01.pickle'),
        'rb') as f:
            self.para_lines = pickle.load(f)
        self.cars = []
        self.car_graphics = []
        self.time_left = time
        focus = False
        self.warning = False
        for car in cars:
            self.cars.append(car["model"])
            self.car_graphics.append(CarGraphics(self.screen, self,
            car["color_id"], car["model"], car["focus"]))
            #If car is the focus, center the game on them.
            if car["focus"] == True:
                self.focus_car = car["model"]
                self.screen_center = car["model"].pos
                self.rotation = car["model"].car_angle
                self.speed = car["model"].speed*3600
                focus = True
        #If no focus car, put the entire tack in view zoomed out.
        if not focus:
            self.screen_center = [120, 15]
            self.rotation = np.pi/2
            self.speed = 0

        self.rescale()

    #Passer function for numba machine code compiler, as it cannot be a class
    #  function
    def convert_passer(self, gamev, ofssc = 1):
        npgamev = np.array([*gamev], dtype=np.float64)
        screen_center = np.array([*self.screen_center], dtype=np.float64)
        result = self.convert(npgamev, screen_center, self.rotation_matrix,
                               self.coord_conversion, ofssc)
        if ofssc: return (result[0], pg.display.Info().current_h - result[1])

        else: return result

    # Code that is compiled to machine code to speed up program. Possible
    # becuase the code is just a set of maxtrix multiplications using numpy.
    @staticmethod
    @jit
    def convert(npgamev, screen_center, rot_m, coordc_m, ofssc):
        if ofssc:
            origin_point = np.array([npgamev[0] - screen_center[0],
            npgamev[1] - screen_center[1]], dtype=np.float64)
            rotated_point = np.dot(origin_point, rot_m)
            new_point = np.array([rotated_point[0] + screen_center[0],
            rotated_point[1] + screen_center[1]], dtype=np.float64)
            result = np.dot(np.array([ofssc, *new_point], dtype=np.float64),
            coordc_m)
            return result

        else:
            result = np.dot(np.array([ofssc, *npgamev], dtype=np.float64),
            coordc_m)
            return result

    # Where all the graphics objects belonging to the game get ticked.
    def tick(self, cars, time, score):
        s_x, s_y = self.screen.get_size()
        self.time_left = time
        self.score = score
        for car in cars:
            if car["focus"] == True:
                self.focus_car = car["model"]
                self.screen_center = car["model"].pos
                self.rotation = car["model"].car_angle
                self.speed = car["model"].speed*3600

        self.create_matrix()
        self.screen.fill((78, 217, 65))
        self.background()
        for i, graphic in enumerate(self.car_graphics):
            graphic.tick(self.cars[i], self.rotation)

        self.warning = False
        #Draw warning line if off track
        if self.focus_car.prev_distance == self.focus_car.distance and\
        self.focus_car.speed != 0:
            pg.draw.line(self.screen, 'red', self.convert_passer(
                self.focus_car.pos),
            self.convert_passer(
                    self.focus_car.cl_points[self.focus_car.target_cl_index]),
                    s_x//400)
            self.warning = True

        #Draw hitboxes
        for car in cars:
            pg.draw.lines(self.screen,(225,0,0), True,
            (self.convert_passer(car["model"].car_corners[0]),
            self.convert_passer(car["model"].car_corners[1]),
            self.convert_passer(car["model"].car_corners[3]),
            self.convert_passer(car["model"].car_corners[2])), 2)
        self.hud()

    # Creates the rotation and scaling matrix used to convert between game
    # coordinates (1metre = 1gameunit) and on-screen coordinates.
    def create_matrix(self):
        s_x, s_y = self.screen.get_size()
        rotate = np.array([[np.sin(self.rotation), (np.cos(self.rotation))],
        [-np.cos(self.rotation), np.sin(self.rotation)]], dtype=np.float64)
        self.rotation_matrix = rotate
        scale = np.array([[0, 0], [(s_x*(0.05208*self.zoom)), 0],
        [0, (s_y*(0.09259*self.zoom))]], dtype=np.float64)
        scale[0] = -np.matmul((1, *self.screen_center), scale)+(s_x/2, s_y/2)
        self.coord_conversion = scale

    # Renders hud objects, eg: speedometer.
    def hud(self):
        w, h = self.screen.get_size()
        color = (255, 255, 255)
        info_bg = pg.image.load(os.path.dirname(os.path.abspath(__file__))
                                +'/../static/button.png')
        speed_bg = pg.transform.scale(info_bg, (w/6, h/10))
        score_bg = pg.transform.scale(info_bg, (w/7, h/10))
        time_bg = pg.transform.scale(info_bg, (w/5, h/10))
        speed_bg_rect = speed_bg.get_rect(center=(w/10, h/1.1))
        score_bg_rect = score_bg.get_rect(center=(w/3.5, h/14))
        time_bg_rect = time_bg.get_rect(center=(w/9, h/14))
        t_font = pg.font.SysFont('arial', int(h/20))
        speed_text = t_font.render(f"{int(round(self.speed, 0))} KM/H", True,
                                   color)
        score_text = t_font.render(f"Score) {int(round(self.score, 0))}",
        True, color)
        time_text = t_font.render(
        f"Time left) {int(self.time_left // 60)}:\
        {int(round(self.time_left % 60, 0)):02d}", True, color)
        speed_text_rect = speed_text.get_rect(center=(w/10, h/1.1))
        score_text_rect = score_text.get_rect(center=(w/3.6, h/14))
        time_text_rect = time_text.get_rect(center=(w/9.3, h/14))
        if self.warning:
            warn_text = t_font.render(f"YOU HAVE SKIPPED THE TRACK!", True,
            (255,0,0))
            warn_text_rect = warn_text.get_rect(center=(w/2, h/1.6))
            self.screen.blit(warn_text, warn_text_rect)
            warn_text = t_font.render(f"FOLLOW THE RED LINE BACK TO REGAIN\
                                      SCORE!", True, (255,0,0))
            warn_text_rect = warn_text.get_rect(center=(w/2, h/1.4))
            self.screen.blit(warn_text, warn_text_rect)

        self.screen.blit(speed_bg, speed_bg_rect)
        self.screen.blit(speed_text, speed_text_rect)
        self.screen.blit(score_bg, score_bg_rect)
        self.screen.blit(score_text, score_text_rect)
        self.screen.blit(time_bg, time_bg_rect)
        self.screen.blit(time_text, time_text_rect)


    # Renders the track, pp = parallel points.
    def background(self):
        cent_line_screen = []
        pp_screen=[]
        for point in self.cent_line:
            cent_line_screen.append(self.convert_passer(point))

        for point in self.para_lines:
            pp_screen.append(self.convert_passer(point))

        pg.gfxdraw.filled_polygon(self.screen, pp_screen, (105,105,105))
        pg.draw.lines(self.screen, (255,255,255), True, cent_line_screen, 5)

    # Re-creates matrix and backround on screen resize.
    def rescale(self):
        self.create_matrix()
        self.background()

    def events(self, event): return None