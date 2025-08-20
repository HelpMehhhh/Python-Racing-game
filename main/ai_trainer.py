import os
import neat
from cars import AiCar
import random as r
import pickle
import cProfile
import pstats
from neat.checkpoint import Checkpointer
from graphics import Graphics

def eval_genomes(genomes, config):
    with open(os.path.join(local_dir, 'center_points_08.pickle'), 'rb') as f: cent_line = pickle.load(f)
    global cars
    cars = []
    accel_values = [7, 10, 11, 12, 13, 14, 16]
    deccel_values = [14, 17, 18, 19, 20, 21, 23]
    for g_id, g in genomes:
        g.fitness = 0
        #speed_index = r.randrange(0, 7)
        cars.append(AiCar([0,1], accel_values[5], deccel_values[5], g, config, cent_line))

    have_live = True
    #cars_graphics = [{"model": car, "color_id": 2, "focus": False} for car in cars]

    #graphics = Graphics(cars_graphics, 1)
    while have_live:
        have_live = False
        for i, car in enumerate(cars):
            if not car.get_alive(): continue
            car.tick(17)
            have_live = True
        #graphics.graphics_loop(cars_graphics)

    for i, car in enumerate(cars):
        genomes[i][1].fitness = car.get_reward()




def run(config_path, generations, extract):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    checkpoint_dir = "models"
    if not extract: pop = neat.Population(config)
    else:
        pop = Checkpointer.restore_checkpoint(os.path.join(checkpoint_dir, "neat-checkpoint-cfr-796"))
        #pop = neat.Population(config, initial_state=(pop.population, pop.species, pop.generation))
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    pop.add_reporter(Checkpointer(generation_interval=100, filename_prefix=os.path.join(checkpoint_dir, "neat-checkpoint-cfr-6_6-")))

    pop.run(eval_genomes, generations)
    final_genomes = pop.population
    winner_genome = None
    winner_fitness = 0
    for genome_id, genome in final_genomes.items():
       print(f"Genome ID: {genome_id}, Fitness: {genome.fitness}")
       if not genome.fitness: continue
       if genome.fitness <= winner_fitness: continue
       winner_genome = genome
       winner_fitness = genome.fitness
    print(f"Winner Fitness: {winner_genome.fitness}")

    with open(os.path.join(local_dir, 'genome_config.pickle'), 'wb') as f: pickle.dump(pop.config, f)
    with open(os.path.join(local_dir, 'winner.pickle'), 'wb') as f: pickle.dump(winner_genome, f)

if __name__ == '__main__':
    #profiler = cProfile.Profile()
    #profiler.enable()
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path, None, True)
    #profiler.disable()
    #stats = pstats.Stats(profiler).sort_stats('cumulative')
    #stats.print_stats()
