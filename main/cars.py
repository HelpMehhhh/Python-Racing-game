from enum import IntEnum
import pygame as pg
import numpy as np
import os
from neat import nn

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
    def __init__(self, screen, game, start_pos, cent_line, color_id, simulation):
        self.screen = screen
        self.pos = [cent_line[0][0]+start_pos[0], cent_line[0][1]+start_pos[1]]
        self.color_id = color_id
        self.cl_points = cent_line
        self.turning_angle = 0
        self.car_angle = np.pi/2
        self.speed = 0
        self.game = game
        self.simulation = simulation

        self.time = 0
        self.target_cl_index = 1
        self.distance_to_seg = 0
        self.distance = 0
        self.point = self.pos

    def tick(self, time_elapsed):
        self.time += time_elapsed/1000
        if not self.simulation: self.draw()

    def get_current_dist(self):
        seg_data = self.get_current_seg()
        v = np.array(seg_data[1]) - np.array(self.cl_points[self.target_cl_index-1])
        if abs(seg_data[0]) > 7: self.distance = self.distance_to_seg
        else: self.distance = self.distance_to_seg + float(np.linalg.norm(v))
        self.point = seg_data[1]
        return seg_data[0]

    def get_data_seg(self, first_point, second_point):
        result = []
        t = ((first_point[0]-self.pos[0])*(first_point[0]-second_point[0])-(first_point[1]-self.pos[1])*(second_point[1]-first_point[1]))/((second_point[1]-first_point[1])**2+(second_point[0]-first_point[0])**2)
        first_point = np.array(first_point)
        second_point = np.array(second_point)
        if t < 0: p = first_point
        elif t > 1: p = second_point
        else: p = first_point+t*(second_point - first_point)
        if abs(first_point[1]-second_point[1]) > abs(first_point[0]-second_point[0]):
            dist_sign = np.sign((p[0]-self.pos[0])/(second_point[1]-first_point[1]))

        else:
            dist_sign = np.sign((p[1]-self.pos[1])/(first_point[0]-second_point[0]))
        if dist_sign == 0: dist_sign = 1
        result.append(dist_sign*np.linalg.norm(p-np.array(self.pos)))
        result.append(p)
        return result

    def get_current_seg(self):
        next_target = (self.target_cl_index+1)%len(self.cl_points)
        cur_seg_data = self.get_data_seg(self.cl_points[self.target_cl_index-1], self.cl_points[self.target_cl_index])
        nxt_seg_data = self.get_data_seg(self.cl_points[self.target_cl_index  ], self.cl_points[next_target])
        if abs(float(cur_seg_data[0])) < abs(float(nxt_seg_data[0])): return cur_seg_data
        if abs(cur_seg_data[0]) > 7: return cur_seg_data
        self.distance_to_seg += float(np.linalg.norm(np.array(self.cl_points[self.target_cl_index]) - np.array(self.cl_points[self.target_cl_index-1])))
        self.target_cl_index = next_target
        return nxt_seg_data

    def movement_calc(self, time_elapsed):
        self.pos[0] += float(time_elapsed*self.speed*np.cos(self.car_angle))
        self.pos[1] += float(time_elapsed*self.speed*np.sin(self.car_angle))
        if self.car_angle > np.pi: self.car_angle -= 2*np.pi
        if self.car_angle < -np.pi: self.car_angle += 2*np.pi

    def draw(self):
        self.car = pg.image.load(os.path.dirname(os.path.abspath(__file__))+f'/../static/car_{self.color_id}.png')
        self.car = pg.transform.scale(self.car, self.game.convert_passer([2, 4], 0))

class PlayerCar(Car):
    def __init__(self, screen, game, start_pos, cent_line, color_id=1, simulation=0):
        Car.__init__(self, screen, game, start_pos, cent_line, color_id, simulation)
        self.max_accel = 15/1000000
        self.max_deccel = 22/1000000
        self.steerstate = self.SteerState.center
        self.speedstate = self.SpeedState.const

    def control(self, event):
        if (event.type == pg.KEYUP):
            if (event.key in (pg.K_d, pg.K_a)): self.steerstate = self.SteerState.center
            if (event.key in (pg.K_UP, pg.K_DOWN)): self.speedstate = self.SpeedState.const

        elif (event.type == pg.KEYDOWN):
            if (event.key == pg.K_d): self.steerstate = self.SteerState.right
            elif (event.key == pg.K_a): self.steerstate = self.SteerState.left
            if (event.key == pg.K_UP): self.speedstate = self.SpeedState.accel
            elif (event.key == pg.K_DOWN): self.speedstate = self.SpeedState.deccel

    def steering(self, time_elapsed):
        chg = (0.00012566*abs(self.turning_angle) + 0.000698131)*time_elapsed
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
            if self.turning_angle > np.pi/6 or self.turning_angle < -np.pi/6: self.turning_angle = float(np.pi/6*np.sign(self.turning_angle))

        if self.speedstate != self.SpeedState.const:
            if self.speedstate == self.SpeedState.deccel:
                self.speed -= time_elapsed*self.max_deccel
                if self.speed < 0: self.speed = 0

            elif self.speedstate == self.SpeedState.accel:
                self.speed += time_elapsed*self.max_accel

        if self.turning_angle != 0:
            radius = np.sqrt((((2/np.tan(abs(self.turning_angle)))+1)**2)+1)
        else:
            radius = 1000
        max_speed = np.sqrt(radius*50)/1000
        if self.speed > max_speed:
            radius = ((self.speed*1000)**2)/50

        d_angle = np.sign(self.turning_angle)*((self.speed/radius)*time_elapsed)
        self.car_angle += float(d_angle)

    def tick(self, time_elapsed):
        super().tick(time_elapsed)
        self.steering(time_elapsed)
        self.movement_calc(time_elapsed)
        self.get_current_dist()

    def draw(self):
        super().draw()
        self.car_rect = self.car.get_rect(center=self.game.convert_passer(self.pos))
        self.screen.blit(self.car, self.car_rect)
        pg.draw.line(self.screen, 'lime', self.game.convert_passer(self.pos), self.game.convert_passer(self.cl_points[self.target_cl_index]), 6)
        pg.draw.line(self.screen, 'red', self.game.convert_passer(self.pos), self.game.convert_passer(self.point), 6)

class AiCar(Car):
    DistanceTrainingLimit = 1310

    def __init__(self, screen, game, start_pos, color_id, max_accel, max_deccel, genome, config, cl_points, simulation=1):
        Car.__init__(self, screen, game, start_pos, cl_points, color_id, simulation)
        self.max_accel = max_accel/1000000
        self.max_deccel = max_deccel/1000000
        self.state = 1 #1 for alive, 0 for dead
        self.distance = 0
        self.time = 0
        self.genome = genome
        self.config = config
        self.n_net = nn.FeedForwardNetwork.create(self.genome, self.config)
        self.d = 0

    def tick(self, time_elapsed, rotation):
        self.rotation = rotation
        super().tick(time_elapsed)
        self.brain_calc(time_elapsed)
        self.movement_calc(time_elapsed)

    def get_alive(self): return self.state

    def get_reward(self):
        return self.distance - abs(self.d)

    def get_data(self, d):
        data = [self.speed/0.1, float(d/7)]
        origin_point = np.array(self.pos)
        target_point = np.array(self.cl_points[(self.target_cl_index)])
        prev_point = np.array(self.cl_points[(self.target_cl_index-1)])
        origin_target_vec = target_point - origin_point
        data.append(float(np.linalg.norm(origin_target_vec)/7))
        prev_target_vec = target_point - prev_point
        target_angle = np.arctan2(prev_target_vec[1], prev_target_vec[0])
        data.append(float((target_angle - self.car_angle)/np.pi))
        prev_angle = target_angle
        prev_point = target_point
        for i in range(1, 3):
            next_point = np.array(self.cl_points[(self.target_cl_index+i)%len(self.cl_points)])
            cur_vector = next_point - prev_point
            cur_angle = np.arctan2(cur_vector[1], cur_vector[0])
            data.append(float(np.linalg.norm(cur_vector)/7))
            data.append(float((cur_angle - prev_angle)/np.pi))
            prev_point = next_point
            prev_angle = cur_angle

        return data

    def brain_calc(self, time_elapsed):
        self.d = self.get_current_dist()
        reason = None

        if self.time > 10:
            reason = "Finished"
            self.state = 0

        if reason is not None and self.distance > 5:
            print(reason, self.distance, self.time, self.speed, self.d)


        output = self.n_net.activate(self.get_data(self.d))

        steer = min(1, max(-1, output[0]))
        accel = min(1, max(-1, output[1]))

        accel *= self.max_deccel if accel < 0 else self.max_accel
        self.speed += accel*time_elapsed
        if self.speed < 0: self.speed = 0

        radius = ((self.speed*1000)**2)/50

        if radius > 0: self.car_angle += float(steer*self.speed/radius*time_elapsed)

        #print(self.speed*3600, self.distance)

    def draw(self):
        super().draw()
        self.car = pg.transform.rotate(self.car, float(np.degrees(self.car_angle))-float(np.degrees(self.rotation)))
        self.car_rect = self.car.get_rect(center=self.game.convert_passer(self.pos))
        self.screen.blit(self.car, self.car_rect)
        pg.draw.line(self.screen, 'lime', self.game.convert_passer(self.pos), self.game.convert_passer(self.cl_points[self.target_cl_index]), 6)
        pg.draw.line(self.screen, 'red', self.game.convert_passer(self.pos), self.game.convert_passer(self.point), 6)

# vim: set sw=4 ts=4 sts=4 et sta sr ai si cin cino=>1s(0u0W1s:
