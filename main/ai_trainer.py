import os
import neat
from cars import AiCar
import random as r
import pickle
import cProfile
import pstats
from neat.checkpoint import Checkpointer

def eval_genomes(genomes, config):
    with open(os.path.join(local_dir, 'center_points_08.pickle'), 'rb') as f: cent_line = pickle.load(f)
    global cars
    cars = []
    accel_values = [7, 10, 11, 12, 13, 14, 15]
    deccel_values = [14, 17, 18, 19, 20, 21, 22]
    for g_id, g in genomes:
        g.fitness = 0
        speed_index = r.randrange(0, 7)
        cars.append(AiCar(0, 0, [0,1], 1, accel_values[speed_index], deccel_values[speed_index], g, config, cent_line))

    have_live = True
    while have_live:
        have_live = False
        for i, car in enumerate(cars):
            if not car.get_alive(): continue
            car.tick(17, 0)
            have_live = True

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
    with open(os.path.join(local_dir, 'genome_config.pickle'), 'wb') as f: pickle.dump(config, f)
    checkpoint_dir = "models"
    if not extract: pop = neat.Population(config)
    else:
        pop = Checkpointer.restore_checkpoint(os.path.join(checkpoint_dir, "neat-checkpoint-894"))
        #pop = neat.Population(config, initial_state=pop.population)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    pop.add_reporter(Checkpointer(generation_interval=100, filename_prefix=os.path.join(checkpoint_dir, "neat-checkpoint-")))
    pop.run(eval_genomes, generations)
    final_genomes = pop.population
    for genome_id, genome in final_genomes.items(): print(f"Genome ID: {genome_id}, Fitness: {genome.fitness}")
    winner_genome = stats.best_genome()
    with open(os.path.join(local_dir, 'winner.pickle'), 'wb') as f: pickle.dump(winner_genome, f)

if __name__ == '__main__':
    #profiler = cProfile.Profile()
    #profiler.enable()
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path, None, False)
    #profiler.disable()
    #stats = pstats.Stats(profiler).sort_stats('cumulative')
    #stats.print_stats()
