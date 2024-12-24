from neat_classes import *
from copy import deepcopy


neat = NEAT(6,1,100)
neat.initalizeSpecies()
print(repr(neat))
for _ in range(100):
    neat.addRandomFitness()
    neat.keepFittestGenomes()
    neat.breedWithinSpecies()
    print(sum([len(list) for list in neat.species]))