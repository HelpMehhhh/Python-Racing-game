import os
from cars import AiCar
import random as r
import pickle
import cProfile






if __name__ == '__main__':
    #profiler = cProfile.Profile()
    #profiler.enable()
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')

    #profiler.disable()
    #stats = pstats.Stats(profiler).sort_stats('cumulative')
    #stats.print_stats()
