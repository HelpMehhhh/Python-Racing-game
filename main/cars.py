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
    def __init__(self, start_pos, cent_line):
        self.start_pos = start_pos
        self.cl_points = cent_line
        self.reset()


    def reset(self):
        self.pos = self.start_pos.copy()
        self.car_angle = np.pi/2
        self.target_cl_index = 1
        self.distance_to_seg = 0
        self.speed = 0
        self.turning_angle = 0
        self.steerstate = self.SteerState.center
        self.speedstate = self.SpeedState.accel
        self.radius = 1000
        self.distance = 0
        self.time = 0
        self.d_track = self.get_current_dist()
        self.score = 0

    def get_current_dist(self):
        seg_data = self.get_current_seg()
        v = np.array(seg_data[1]) - np.array(self.cl_points[self.target_cl_index-1])
        self.distance = self.distance_to_seg + float(np.linalg.norm(v))
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
        self.distance_to_seg += float(np.linalg.norm(np.array(self.cl_points[self.target_cl_index]) - np.array(self.cl_points[self.target_cl_index-1])))
        self.target_cl_index = next_target
        return nxt_seg_data

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
            if self.turning_angle > np.pi/6 or self.turning_angle < -np.pi/6: self.turning_angle = float(np.pi/6*np.sign(self.turning_angle))

        if self.speedstate != self.SpeedState.const:
            if self.speedstate == self.SpeedState.deccel:
                self.speed -= self.time_elapsed*self.max_deccel
                if self.speed < 0: self.speed = 0

            elif self.speedstate == self.SpeedState.accel:
                self.speed += self.time_elapsed*self.max_accel

        if self.turning_angle != 0:
            self.radius = np.sqrt((((2/np.tan(abs(self.turning_angle)))+1)**2)+1)
        else:
            self.radius = 1000
        max_speed = np.sqrt(self.radius*50)/1000
        if self.speed > max_speed:
            self.radius = ((self.speed*1000)**2)/50

        d_angle = np.sign(self.turning_angle)*((self.speed/self.radius)*self.time_elapsed)
        self.car_angle += float(d_angle)
        self.pos[0] += float(self.time_elapsed*self.speed*np.cos(self.car_angle))
        self.pos[1] += float(self.time_elapsed*self.speed*np.sin(self.car_angle))
        if self.car_angle > np.pi: self.car_angle -= 2*np.pi
        if self.car_angle < -np.pi: self.car_angle += 2*np.pi


class PlayerCar(Car):
    def __init__(self, start_pos, cent_line):
        Car.__init__(self, start_pos, cent_line)
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

    def tick(self, time_elapsed):
        self.movement_calc()
        self.time += time_elapsed/1000
        self.get_current_dist()


class AiCar(Car):

    def __init__(self, start_pos, max_accel, max_deccel, cl_points):
        Car.__init__(self, start_pos, cl_points)
        self.max_accel = max_accel/1000000
        self.max_deccel = max_deccel/1000000
        self.last_distance = 0

    def tick(self, time_elapsed, action):
        self.time_elapsed = time_elapsed
        return self.brain_calc(action)

    def get_start(self): return self.start_pos

    def get_data(self):
        #returns should be floats, function insides should be handled with numpy

        data = [self.turning_angle, self.speed, self.radius, self.d_track]
        origin_point = np.array(self.pos)
        target_point = np.array(self.cl_points[(self.target_cl_index)])
        prev_point = np.array(self.cl_points[(self.target_cl_index-1)])
        origin_target_vec = target_point - origin_point
        data.append(np.linalg.norm(origin_target_vec))
        prev_target_vec = target_point - prev_point
        target_angle = np.arctan2(prev_target_vec[1], prev_target_vec[0])
        data.append(target_angle - self.car_angle)
        prev_angle = target_angle
        prev_point = target_point
        for i in range(1, 4):
            next_point = np.array(self.cl_points[(self.target_cl_index+i)%len(self.cl_points)])
            cur_vector = next_point - prev_point
            cur_angle = np.arctan2(cur_vector[1], cur_vector[0])
            data.append(np.linalg.norm(cur_vector))
            data.append(cur_angle - prev_angle)
            prev_point = next_point
            prev_angle = cur_angle

        return np.array(data, dtype=np.float64)

    def brain_calc(self, action):
        self.time += self.time_elapsed/1000

        steer_choice = action[:3].index(max(action[:3]))
        speed_choice = action[3:].index(max(action[3:]))
        self.steerstate = [self.SteerState.left, self.SteerState.center, self.SteerState.right][steer_choice]
        self.speedstate = [self.SpeedState.accel, self.SpeedState.const, self.SpeedState.deccel][speed_choice]
        self.movement_calc()


        reward = 0
        game_over = False
        too_slow = False
        self.last_distance = self.distance
        self.d_track = self.get_current_dist()
        if self.time > 10 and self.distance/self.time < 2: too_slow = True
        if abs(self.d_track) > 7 or too_slow:
            game_over = True
            reward = -100
            return reward, game_over, self.score
        else:
            reward = abs(self.distance)-abs(self.last_distance)
            self.score = abs(self.distance)
        return reward, game_over, self.score



