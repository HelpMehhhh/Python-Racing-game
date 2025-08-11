import os
import neat
from cars import AiCar
import random as r
import pickle

def eval_genomes(genomes, config):
    with open(os.path.join(local_dir, 'center_points_08.pickle'), 'rb') as f: cent_line = pickle.load(f)

    cars = []
    accel_values = [7, 10, 11, 12, 13, 14, 15]
    deccel_values = [14, 17, 18, 19, 20, 21, 22]
    for g_id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        g.fitness = 0
        speed_index = r.randrange(0, 7)
        cars.append(AiCar(0, 0, [0,0], 1, accel_values[speed_index], deccel_values[speed_index], net, cent_line))

    while True:
        remain_cars = 0
        for i, car in enumerate(cars):
            if car.get_alive: 
                car.tick(17, 0)
                remain_cars += 1

            else: 
                genomes[i][1].fitness += car.get_reward()
                car.used_reward()

        if remain_cars == 0:
            break


def run(config_path, generations):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.run(eval_genomes, generations)
    final_genomes = pop.population
    for genome_id, genome in final_genomes.items(): print(f"Genome ID: {genome_id}, Fitness: {genome.fitness}")

if __name__ is '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path, 100)