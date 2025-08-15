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
        self.pos = start_pos
        self.color_id = color_id
        self.cl_points = cent_line
        self.turning_angle = 0
        self.car_angle = np.pi/2
        self.speed = 0
        self.game = game
        self.steerstate = self.SteerState.center
        self.speedstate = self.SpeedState.const
        self.simulation = simulation

        self.prev_cl_point = self.pos
        self.target_cl_index = 1
        self.distance = 0


    def get_data_seg(self, first_point, second_point):
        result = []
        if abs(first_point[1]-second_point[1]) > abs(first_point[0]-second_point[0]):
            m = ((first_point[0]-second_point[0])/(first_point[1]-second_point[1]))
            y = (self.pos[1]+m*self.pos[0]+(m**2)*second_point[1]-m*second_point[0])/((m**2)+1)
            x = (m*self.pos[1]+(m**2)*self.pos[0]+(m**3)*second_point[1]-(m**2)*second_point[0])/((m**2)+1)-m*second_point[1]+second_point[0]
        else:
            m = ((first_point[1]-second_point[1])/(first_point[0]-second_point[0]))
            x = (self.pos[0]+m*self.pos[1]+(m**2)*second_point[0]-m*second_point[1])/((m**2)+1)
            y = (m*self.pos[0]+(m**2)*self.pos[1]+(m**3)*second_point[0]-(m**2)*second_point[1])/((m**2)+1)-m*second_point[0]+second_point[1]
        x_lower_bound = min(first_point[0], second_point[0])
        x_upper_bound = max(first_point[0], second_point[0])
        y_lower_bound = min(first_point[1], second_point[1])
        y_upper_bound = max(first_point[1], second_point[1])
        if m != 0:
            if x > x_upper_bound: point = first_point if x_upper_bound in first_point else second_point
            elif x < x_lower_bound: point = first_point if x_lower_bound in first_point else second_point
            else: point = (x,y)

        else:
            if x_lower_bound == x_upper_bound:
                if y > y_upper_bound: point = first_point if y_upper_bound in first_point else second_point
                elif y < y_lower_bound: point = first_point if y_lower_bound in first_point else second_point
                else: point = (x,y)
            elif y_lower_bound == y_upper_bound:
                if x > x_upper_bound: point = first_point if x_upper_bound in first_point else second_point
                elif x < x_lower_bound: point = first_point if x_lower_bound in first_point else second_point
                else: point = (x,y)

        result.append(np.linalg.norm(np.array(self.pos) - np.array(point)))
        result.append(point)
        return result


    def get_current_seg(self):
        c_d = float('inf')
        index = 0
        closest_seg_data = 0
        for i, point in enumerate(self.cl_points):
            seg_data = self.get_data_seg(point, self.cl_points[(i+1)%len(self.cl_points)])
            if float(seg_data[0]) < float(c_d):
                c_d = seg_data[0]
                index = (i+1)%len(self.cl_points)
                closest_seg_data = seg_data
        self.target_cl_index = index
        return closest_seg_data


    def get_current_dist(self):

        seg_data = self.get_current_seg()
        self.distance += float(np.linalg.norm(np.array(self.prev_cl_point) - np.array(seg_data[1])))
        self.prev_cl_point = seg_data[1]


        return seg_data[0]


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
            if self.turning_angle > np.pi/6 or self.turning_angle < -np.pi/6: self.turning_angle = float(np.pi/6*np.sign(self.turning_angle))

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
        #
        if self.speed > max_speed:
            radius = ((self.speed*1000)**2)/50

        if self.speed > 0:
            pass
        d_angle = np.sign(self.turning_angle)*((self.speed/radius)*self.time_elapsed) if radius != 0 else 0
        self.car_angle += float(d_angle)
        self.pos[0] += float(self.time_elapsed*self.speed*np.cos(self.car_angle))
        self.pos[1] += float(self.time_elapsed*self.speed*np.sin(self.car_angle))
        if self.car_angle > np.pi: self.car_angle -= 2*np.pi
        if self.car_angle < -np.pi: self.car_angle += 2*np.pi


    def draw(self):
        self.car = pg.image.load(os.path.dirname(os.path.abspath(__file__))+f'/../static/car_{self.color_id}.png')
        self.car = pg.transform.scale(self.car, self.game.convert_passer([2, 4], 0))
        self.car_rect = self.car.get_rect(center=self.game.convert_passer(self.pos))






class PlayerCar(Car):
    def __init__(self, screen, game, start_pos, cent_line, color_id=1, simulation=0):
        Car.__init__(self, screen, game, start_pos, cent_line, color_id, simulation)
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
        r = self.get_current_dist()

        print(round(r,2), round(self.distance,2), self.target_cl_index)
        self.movement_calc()


    def draw(self):
        super().draw()
        self.screen.blit(self.car, self.car_rect)






class AiCar(Car):
    def __init__(self, screen, game, start_pos, color_id, max_accel, max_deccel, genome, config, cl_points, simulation=1):
        Car.__init__(self, screen, game, start_pos, cl_points, color_id, simulation)
        self.max_accel = max_accel/1000000
        self.max_deccel = max_deccel/1000000
        self.state = 1 #1 for alive, 0 for dead
        self.distance = 0
        self.time = 0
        self.reward = True
        self.target_cl_index = 1
        self.p_prev = start_pos
        self.p_next = start_pos
        self.genome = genome
        self.config = config
        self.n_net = nn.FeedForwardNetwork.create(self.genome, self.config)


    def tick(self, time_elapsed, rotation):
        self.rotation = rotation
        super().tick(time_elapsed)
        self.brain_calc()
        self.movement_calc()



    def get_alive(self): return self.state

    def get_config(self): return self.config

    def get_genome(self): return self.genome

    def used_reward(self): self.reward = False


    def get_reward(self):
        if self.reward: return float((self.distance**2)/self.time)
        else: return 0




    def get_data(self, d):
        #returns should be floats, function insides should be handled with numpy
        data = [float(d)]

        origin_point = np.array(self.pos)
        origin_angle = self.car_angle
        target_point = np.array(self.cl_points[(self.target_cl_index)])
        prev_point = np.array(self.cl_points[(self.target_cl_index-1)])
        origin_target_vec = target_point - origin_point
        data.append(float(np.linalg.norm(origin_target_vec)))
        prev_target_vec = target_point - prev_point
        target_angle = np.arctan2(prev_target_vec[1], prev_target_vec[0])
        data.append(float(target_angle - origin_angle))


        prev_angle = target_angle
        prev_point = target_point
        for i in range(1, 5):
            next_point = np.array(self.cl_points[(self.target_cl_index+i)%len(self.cl_points)])
            cur_vector = next_point - prev_point
            cur_angle = np.arctan2(cur_vector[1], cur_vector[0])
            data.append(float(np.linalg.norm(cur_vector)))
            data.append(float((cur_angle - prev_angle)))
            prev_point = next_point
            prev_angle = cur_angle

        return data


    def brain_calc(self):
        d = self.get_current_dist()
        if d >= 7:
            self.state = 0
        output = self.n_net.activate(self.get_data(d))
        if output[0] <= -1/3: self.steerstate = self.SteerState.left

        elif output[0] >= 1/3: self.steerstate = self.SteerState.right

        else: self.steerstate = self.SteerState.center

        if output[1] <= -1/3: self.speedstate = self.SpeedState.deccel

        elif output[1] >= 1/3: self.speedstate = self.SpeedState.accel

        else: self.speedstate = self.SpeedState.const

        self.time += self.time_elapsed/1000
        #print(self.speed*3600, self.distance)


    def draw(self):
        super().draw()
        self.car = pg.transform.rotate(self.car, self.rotation - self.car_angle)
        self.screen.blit(self.car, self.car_rect)



