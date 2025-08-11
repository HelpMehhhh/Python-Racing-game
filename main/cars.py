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
    def __init__(self, screen, game, start_pos, color_id, simulation):
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
        self.simulation = simulation


    def tick(self, time_elapsed):
        self.time_elapsed = time_elapsed
        if not self.simulation: self.draw()


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
    def __init__(self, screen, game, start_pos, color_id=1, simulation=0):
        Car.__init__(self, screen, game, start_pos, color_id, simulation)
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
        super().tick(time_elapsed)
        self.movement_calc()


    def draw(self):
        super().draw()
        self.screen.blit(self.car, self.car_rect)






class AiCar(Car):
    def __init__(self, screen, game, start_pos, color_id, max_accel, max_deccel, n_net, cl_points, simulation=1):
        Car.__init__(self, screen, game, start_pos, color_id, simulation)
        self.max_accel = max_accel/1000000
        self.max_deccel = max_deccel/1000000
        self.n_net = n_net
        self.cl_points = cl_points
        self.state = 1 #1 for alive, 0 for dead
        self.distance = 0
        self.time = 0
        self.reward = True
        self.target_cl_index = 1
        self.p_prev = start_pos
        self.p_next = start_pos


    def tick(self, time_elapsed, rotation):
        self.rotation = rotation
        super().tick(time_elapsed)
        self.brain_calc()
        self.movement_calc()


    def used_reward(self):
        self.reward = False


    def get_reward(self):
        if self.reward:
            return (self.distance**2)/self.time
        else: return 0


    def get_alive(self):
        return self.state


    def get_distance_intersect(self, other_seg_point, closest_cl_point):
        if abs(other_seg_point[1]-closest_cl_point[1]) > abs(other_seg_point[0]-closest_cl_point[0]):
            m = ((other_seg_point[0]-closest_cl_point[0])/(other_seg_point[1]-closest_cl_point[1]))
        else:
            m = ((other_seg_point[1]-closest_cl_point[1])/(other_seg_point[0]-closest_cl_point[0]))

        x = (self.pos[0]+m*self.pos[1]+(m**2)*closest_cl_point[0]-m*closest_cl_point[1])/((m**2)+1)
        y = (m*self.pos[0]+(m**2)*self.pos[1]+(m**3)*closest_cl_point[0]-(m**2)*closest_cl_point[1])/((m**2)+1)-m*closest_cl_point[1]+closest_cl_point[1]
        lower_bound = min(other_seg_point[0], closest_cl_point[0])
        upper_bound = max(other_seg_point[0], closest_cl_point[0])
        d = np.linalg.norm(np.array(self.pos) - np.array([x, y]))
        if not lower_bound <= x <= upper_bound: return [False, d, (x, y)]
        return [True, d, (x, y)]


    def get_current_dist(self):
        c_d = -1
        index = 0
        for i, point in enumerate(self.cl_points):
            d = np.linalg.norm(np.array(self.pos) - np.array(point))
            if c_d >= d:
                c_d = d
                index = i

        closest_cl_point = self.cl_points[index]
        c_cl_index = index
        if index == (len(self.cl_points)-1): index = -1
        next_cl_point = self.cl_points[index+1]
        prev_cl_point = self.cl_points[index-1]
        d_next = self.get_distance_intersect(next_cl_point, closest_cl_point)
        d_prev = self.get_distance_intersect(prev_cl_point, closest_cl_point)
        if (d_next[0] and d_prev[0]) or (not d_next[0] and not d_prev[0]):
            self.target_cl_index = index+1
            d = np.linalg.norm(np.array(self.pos) - np.array(closest_cl_point))
            dist_trav_prev = np.linalg.norm(np.array(self.p_prev) - np.array(d_prev[2]))
            dist_trav_next = np.linalg.norm(np.array(self.p_next) - np.array(d_next[2]))
            self.p_prev = d_prev[2]
            self.p_next = d_next[2]
            self.distance += (dist_trav_next + dist_trav_prev)

        elif not d_next[0] and d_prev[0]:
            self.target_cl_index = c_cl_index
            d = d_prev[1]
            dist_trav_prev = np.linalg.norm(np.array(self.p_prev) - np.array(d_prev[2]))
            self.p_prev = d_prev[2]
            self.p_next = d_next[2]
            self.distance += dist_trav_prev

        elif d_next[0] and not d_prev[0]:
            self.target_cl_index = index+1
            d = d_next[1]
            dist_trav_next = np.linalg.norm(np.array(self.p_next) - np.array(d_next[2]))
            self.p_prev = d_prev[2]
            self.p_next = d_next[2]
            self.distance += dist_trav_next

        return d


    def get_data(self):
        data = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        point = [self.cl_points[self.target_cl_index][0] + -1*self.pos[0], self.cl_points[self.target_cl_index][1] + -1*self.pos[1]]
        if abs(self.car_angle) > np.pi:
            angle = self.car_angle + np.sign(self.car_angle)*-(2*np.pi)

        else: angle = self.car_angle

        prev_angle = np.arctan2(point[0], point[1])
        data[0] = prev_angle + angle
        d = np.linalg.norm(np.array(self.pos) - np.array(self.cl_points[self.target_cl_index]))
        data[1] = d
        index = self.target_cl_index
        for i in range(2, 9, 2):
            if index == (len(self.cl_points)-1): index = -1
            point = [self.cl_points[index+1][0] + -1*self.cl_points[index][0], self.cl_points[index+1][1] + -1*self.cl_points[index][1]]
            point_angle = np.arctan2(point[0], point[1])
            data[i] =  -1*prev_angle + point_angle
            index = index+1
            prev_angle=point_angle
            d = np.linalg.norm(np.array(self.cl_points[self.target_cl_index+((i // 2)-1)]) - np.array(self.cl_points[self.target_cl_index+((i // 2))]))
            data[i+1] = d

        return data


    def brain_calc(self):
        d = self.get_current_dist()
        if d >= 7: self.state = 0
        output = self.n_net.activate(self.get_data())
        if output[0] <= -1/3:
            self.steerstate = self.SteerState.left
        elif output[0] >= 1/3:
            self.steerstate = self.SteerState.right
        else:
            self.steerstate = self.SteerState.center

        if output[1] <= -1/3:
            self.speedstate = self.SpeedState.deccel
        elif output[1] >= 1/3:
            self.speedstate = self.SpeedState.accel
        else:
            self.speedstate = self.SpeedState.const
        self.time += self.time_elapsed


    def draw(self):
        super().draw()
        self.car = pg.transform.rotate(self.car, self.rotation - self.car_angle)
        self.screen.blit(self.car, self.car_rect)



