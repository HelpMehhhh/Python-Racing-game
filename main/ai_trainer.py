import os
import neat

def eval_genomes(genomes, config):
    cars = []




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