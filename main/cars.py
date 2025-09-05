# Car file responsible for holding car logic code.

#Packages beign used in the program.
from enum import IntEnum #For defining car states as varibles without using
#strings.
import pygame as pg # For event handeling.
import numpy as np # Advanced math library, makes number crunching faster and
#better.
from neat import nn # For creating the neural network based off a model and
# config in models folder.

# Parent car class, where common data between ai and player car objects are
#  stored.
class Car():
    class SteerState(IntEnum):
        left = 1
        center = 0
        right = -1
    class SpeedState(IntEnum):
        accel = 1
        const = 0
        deccel = -1

    #Main init, creates all the data varibles of the cars.
    #Color id refers to how the car image files are named 1 through 6.
    def __init__(self, start_pos, cent_line):
        # Starting pos made with refrence to the center line for ai training
        #  purposes.
        self.pos = [cent_line[0][0]+start_pos[0], cent_line[0][1]+start_pos[1]]
        #cl = center line.
        self.cl_points = cent_line
        self.car_corners = [(0,0),(0,0),(0,0),(0,0)]
        self.turning_angle = 0
        self.car_angle = np.pi/2
        self.speed = 0
        self.time = 0
        self.target_cl_index = 1
        #seg = segment
        self.distance_to_seg = 0
        self.distance = 0
        self.prev_distance = self.distance
        self.point = self.pos

    #Parent tick function
    def tick(self, time_elapsed):
        self.time += time_elapsed/1000


    # Returns the current distance to closest centerline segment, and updates
    # the total distance travled along the center line for the car.
    def get_current_dist(self):
        self.prev_distance = self.distance
        seg_data = self.get_current_seg()
        v = np.array(seg_data[1]) - np.array(
            self.cl_points[self.target_cl_index-1])
        if abs(seg_data[0]) > 7: self.distance = self.distance_to_seg
        else: self.distance = self.distance_to_seg + float(np.linalg.norm(v))
        self.point = seg_data[1]
        return seg_data[0]

    #Returns the point on the given line (first_point, second_point) closest
    #  to the car and the distance to it, where p is the calculated point based
    #  on formula calculated using the parametric arrangement of general line
    #  formule for t.
    def get_data_seg(self, first_point, second_point):
        result = []
        t = ((first_point[0]-self.pos[0])*
             (first_point[0]-second_point[0])-
             (first_point[1]-self.pos[1])*
             (second_point[1]-first_point[1]))/(
             (second_point[1]-first_point[1])**2
            +(second_point[0]-first_point[0])**2)

        first_point = np.array(first_point)
        second_point = np.array(second_point)
        if t < 0:
            p = first_point
        elif t > 1:
            p = second_point
        else:
            p = first_point+t*(second_point - first_point)

        if abs(first_point[1]-second_point[1]) >\
        abs(first_point[0]-second_point[0]):
            dist_sign = np.sign((p[0]-self.pos[0])/(
                second_point[1]-first_point[1]))

        else:
            dist_sign = np.sign((p[1]-self.pos[1])/(
                first_point[0]-second_point[0]))

        if dist_sign == 0: dist_sign = 1
        result.append(dist_sign*np.linalg.norm(p-np.array(self.pos)))
        result.append(p)
        return result

    # Returns either the data for the current segment the car is on, or the
    # next depending on if they have gone off the track or not.
    def get_current_seg(self):
        next_target = (self.target_cl_index+1)%len(self.cl_points)
        cur_seg_data = self.get_data_seg(self.cl_points[
            self.target_cl_index-1], self.cl_points[self.target_cl_index])
        nxt_seg_data = self.get_data_seg(self.cl_points[
            self.target_cl_index  ], self.cl_points[next_target])
        if abs(float(cur_seg_data[0])) < abs(float(nxt_seg_data[0])):
            return cur_seg_data

        if abs(cur_seg_data[0]) > 7:
            return cur_seg_data

        self.distance_to_seg += float(np.linalg.norm(
            np.array(self.cl_points[self.target_cl_index]) -
            np.array(self.cl_points[self.target_cl_index-1])))
        self.target_cl_index = next_target
        return nxt_seg_data

    # Calculates cars new position after tick.
    def movement_calc(self, time_elapsed):
        self.pos[0] += float(time_elapsed*self.speed*np.cos(self.car_angle))
        self.pos[1] += float(time_elapsed*self.speed*np.sin(self.car_angle))
        if self.car_angle > np.pi: self.car_angle -= 2*np.pi
        if self.car_angle < -np.pi: self.car_angle += 2*np.pi

# Player car child class, inherits from the parent.
class PlayerCar(Car):
    # Initilizes player spesific values.
    def __init__(self, start_pos, cent_line):
        Car.__init__(self, start_pos, cent_line)
        self.max_accel = 17/1000000
        self.max_deccel = 32/1000000
        self.steerstate = self.SteerState.center
        self.speedstate = self.SpeedState.const
        self.d = 0

    # Control fucntion spesific to the player.
    def control(self, event):
        if (event.type == pg.KEYUP):
            if (event.key in (pg.K_d, pg.K_a)):
                self.steerstate = self.SteerState.center
            if (event.key in (pg.K_UP, pg.K_DOWN)):
                self.speedstate = self.SpeedState.const

        elif (event.type == pg.KEYDOWN):
            if (event.key == pg.K_d): self.steerstate = self.SteerState.right
            elif (event.key == pg.K_a): self.steerstate = self.SteerState.left
            if (event.key == pg.K_UP): self.speedstate = self.SpeedState.accel
            elif (event.key == pg.K_DOWN):
                self.speedstate = self.SpeedState.deccel

    #Steering calculation for the player, based off real physics formula.
    def steering(self, time_elapsed):
        chg = (0.00012566*abs(self.turning_angle) + 0.000698131)*time_elapsed
        # Adjust the tire deflection angle based of off of chg = change
        #  equation.
        if self.steerstate == self.SteerState.center:
            chg *=3
            if abs(self.turning_angle) > chg:
                self.turning_angle += chg if (self.turning_angle < 0) else -chg

            else:
                self.turning_angle = 0

        else:
            if np.sign(self.turning_angle) != np.sign(self.steerstate):
                chg *= 3

            self.turning_angle += chg*self.steerstate
            if self.turning_angle > np.pi/6 or self.turning_angle < -np.pi/6:
                self.turning_angle = float(np.pi/6*np.sign(self.turning_angle))

        #Adjust the speed based on acceleration and decelleration values
        if self.speedstate != self.SpeedState.const:
            if self.speedstate == self.SpeedState.deccel:
                self.speed -= time_elapsed*self.max_deccel
                if self.speed < 0: self.speed = 0

            elif self.speedstate == self.SpeedState.accel:
                self.speed += time_elapsed*self.max_accel

        #If there is tire deflection, calculate turning radius using
        #   Ackermann steering geometry.
        if self.turning_angle != 0:
            radius = np.sqrt((((2/np.tan(abs(self.turning_angle)))+1)**2)+1)
        #If not, super high turning radius for "straight driving"
        else:
            radius = 1000

        max_speed = np.sqrt(radius*60)/1000
        if self.speed > max_speed:
            radius = ((self.speed*1000)**2)/60

        #Change in angle calculation.
        d_angle = np.sign(self.turning_angle)*(
            (self.speed/radius)*time_elapsed)
        self.car_angle += float(d_angle)

    #Player car tick.
    def tick(self, time_elapsed):
        super().tick(time_elapsed)
        self.steering(time_elapsed)
        self.movement_calc(time_elapsed)
        self.d = self.get_current_dist()


# Ai car child class, inherits from the parent.
class AiCar(Car):
    # Initilizes ai spesific values.
    def __init__(self, start_pos, max_accel, max_deccel, genome, config,
    cl_points):
        Car.__init__(self, start_pos, cl_points)
        self.max_accel = max_accel/1000000
        self.max_deccel = max_deccel/1000000
        self.state = 1 #1 for alive, 0 for dead
        self.distance = 0
        self.genome = genome
        self.config = config
        self.n_net = nn.FeedForwardNetwork.create(self.genome, self.config)
        self.d = 0
        self.last_time = 0
        self.last_dist = 0

    # Reset function that resets a ai to its defualt values.
    def reset(self):
        self.pos = [0,1]
        self.car_angle = np.pi/2
        self.target_cl_index = 1
        self.speed = 0
        self.turning_angle = 0
        self.steerstate = self.SteerState.center
        self.speedstate = self.SpeedState.const
        self.d = 0
        self.time = 0

    # Ai tick
    def tick(self, time_elapsed):
        super().tick(time_elapsed)
        self.brain_calc(17)
        self.movement_calc(time_elapsed)

    # Returns wether or not the ai is alive, for training purposes.
    def get_alive(self): return self.state

    # Returns a reward based off the total distance travled, trianing purposes.
    def get_reward(self): return self.distance

    # Returns a set of data points that the trained neural network uses to
    # decide how to steer and accelerate.
    def get_data(self):
        data = [self.speed/0.1, float(self.d/7)]
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
        for i in range(1, 4):
            next_point = np.array(self.cl_points[(self.target_cl_index+i)%
                                                 len(self.cl_points)])
            cur_vector = next_point - prev_point
            cur_angle = np.arctan2(cur_vector[1], cur_vector[0])
            data.append(float(np.linalg.norm(cur_vector)/7))
            data.append(float((cur_angle - prev_angle)/np.pi))
            prev_point = next_point
            prev_angle = cur_angle

        return data

    # Brain function of the ai, handles the nerual network and steering.
    def brain_calc(self, time_elapsed):
        self.d = self.get_current_dist()
        reason = None

        if self.time > 600:
            reason = "Finished"
            self.state = 0
            if reason is not None and self.distance > 1300:
                print(reason, self.distance, self.time, self.speed, self.d)

        if self.time > self.last_time + 10:
            if (self.distance - self.last_dist) /\
            (self.time - self.last_time) < 80/3.6:
                reason = "Too slow"
                self.state = 0
            self.last_dist = self.distance
            self.last_time = self.time

        # Resets if it goes off track for whatever reason.
        if abs(self.d) >= 7:
            reason = "Off Track"
            self.state = 0
            self.reset()

        #Nueral network output, gets the choice via max function, and changes
        #  the speed/turning angle based off the choices.
        output = self.n_net.activate(self.get_data())
        steer = min(1, max(-1, output[0]))
        accel = min(1, max(-1, output[1]))

        accel *= self.max_deccel if accel < 0 else self.max_accel
        self.speed += accel*time_elapsed
        if self.speed < 0: self.speed = 0

        radius = ((self.speed*1000)**2)/50

        if radius > 0:
            self.car_angle += float(steer*self.speed/radius*time_elapsed)



# vim: set sw=4 ts=4 sts=4 et sta sr ai si cin cino=>1s(0u0W1s:
