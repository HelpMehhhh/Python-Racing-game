import os
from cars import AiCar
import random as r
import cProfile
import torch
import pickle
import numpy as np





def eval_genomes(genomes, config):
    with open(os.path.join(local_dir, 'center_points_08.pickle'), 'rb') as f: cent_line = pickle.load(f)
    cars = []
    accel_values = [7, 10, 11, 12, 13, 14, 15]
    deccel_values = [14, 17, 18, 19, 20, 21, 22]
    for g_id, g in genomes:
        g.fitness = 0
        #speed_index = r.randrange(0, 7)
        cars.append(AiCar(0, 0, [0,1], 1, accel_values[5], deccel_values[5], g, config, cent_line))

    have_live = True
    while have_live:
        have_live = False
        for i, car in enumerate(cars):
            if not car.get_alive(): continue
            car.tick(17, 0)
            have_live = True

    for i, car in enumerate(cars):
        genomes[i][1].fitness = car.get_reward()





if __name__ == '__main__':
    #profiler = cProfile.Profile()
    #profiler.enable()
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')

    #profiler.disable()
    #stats = pstats.Stats(profiler).sort_stats('cumulative')
    #stats.print_stats()
