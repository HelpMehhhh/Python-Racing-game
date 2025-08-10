from enum import IntEnum
import pygame as pg
import numpy as np
import os

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
        self.turn_timer = 0
        self.steerstate = self.SteerState.center
        self.speedstate = self.SpeedState.const
        self.a = 0
        self.tt = 0.005
        self.tspeed = 0


    def tick(self, time_elapsed, rotation):
        self.rotation = rotation
        self.time_elapsed = time_elapsed
        self.draw()
        self.movement_calc()



    def movement_calc(self):
        chg = (0.00012566*abs(self.turning_angle) + 0.000698131)*self.time_elapsed
        #if self.speed > self.tt: chg *= self.tt/self.speed
        if self.steerstate == self.SteerState.center:
            chg *=3
            if abs(self.turning_angle) > chg:
                self.turning_angle += chg if (self.turning_angle < 0) else -chg

            else:
                self.turning_angle = 0

        else:
            if np.sign(self.turning_angle) != np.sign(self.steerstate): chg *= 3
            self.turning_angle += chg*self.steerstate
            if self.turning_angle > 0.5236 or self.turning_angle < -0.5236: self.turning_angle = float(0.5236*np.sign(self.turning_angle))

        if self.speedstate != self.SpeedState.const:
            if self.speedstate == self.SpeedState.deccel:
                self.speed -= self.time_elapsed*self.max_deccel
                if self.speed < 0: self.speed = 0

            elif self.speedstate == self.SpeedState.accel:
                self.speed += self.time_elapsed*self.max_accel

        if self.turning_angle != 0:
            radius = np.sqrt((((2/np.tan(abs(self.turning_angle)))+1)**2)+1)
            #print(radius)

        else: radius = 0
        max_speed = np.sqrt(radius*50)/1000
        #print(self.speed*3600)
        if self.speed > max_speed:
            radius = ((self.speed*1000)**2)/50

        d_angle = np.sign(self.turning_angle)*((self.speed/radius)*self.time_elapsed) if radius != 0 else 0
        self.car_angle += float(d_angle)
        self.pos[0] += self.time_elapsed*self.speed*np.cos(self.car_angle+1.570796327)
        self.pos[1] += self.time_elapsed*self.speed*np.sin(self.car_angle+1.570796327)
        if self.car_angle >= 6.283185307: self.car_angle -= 6.283185307
        if self.car_angle <= -6.283185307: self.car_angle += 6.283185307


    def draw(self):
        self.car = pg.image.load(os.path.dirname(os.path.abspath(__file__))+f'/../static/car_{self.color_id}.png')
        self.car = pg.transform.scale(self.car, self.game.convert_passer([2, 4], 0))
        self.car_rect = self.car.get_rect(center=self.game.convert_passer(self.pos))






class PlayerCar(Car):
    def __init__(self, screen, game, start_pos, color_id=1):
        Car.__init__(self, screen, game, start_pos, color_id)
        self.max_accel = 15/1000000
        self.max_deccel = 22/1000000


    def control(self, event):
        if (event.type == pg.KEYUP):
            if (event.key in (pg.K_d, pg.K_a)): self.steerstate = self.SteerState.center

            if (event.key in (pg.K_UP, pg.K_DOWN)): self.speedstate = self.SpeedState.const

        elif (event.type == pg.KEYDOWN):
            if (event.key == pg.K_d): self.steerstate = self.SteerState.right

            elif (event.key == pg.K_a): self.steerstate = self.SteerState.left

            if (event.key == pg.K_UP): self.speedstate = self.SpeedState.accel

            elif (event.key == pg.K_DOWN): self.speedstate = self.SpeedState.deccel


    def draw(self):
        super().draw()
        self.screen.blit(self.car, self.car_rect)






class AiCar(Car):
    def __init__(self, screen, game, start_pos, color_id, max_accel, max_deccel):
        Car.__init__(self, screen, game, start_pos, color_id)
        self.max_accel = max_accel/1000000
        self.max_deccel = max_deccel/1000000


    def draw(self):
        super().draw()
        self.car = pg.transform.rotate(self.car, self.rotation - self.car_angle)
        self.screen.blit(self.car, self.car_rect)



