import pygame
from sim import *
import neat
import os
import visualize

pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Simulation")
clock = pygame.time.Clock()

shouldRender = True
realTime = False
targetFPS = 45

numPlayers = 49
mapSize = 100
numFood = 100
aiNets = []
offsetX = 0
offsetY = 0
windowWidth = 800
windowHeight = 800
addHumanPlayer = False

nodeNames = {0: "W", 1: "S", 2: "D", 3: "A", 4: "Up", 5: "Down", 6: "Left", 7: "Right", -1: "1playerX", -2: "1playerY", -3: "1playerVX", -4: "1playerVY", -5: "2playerX", -6: "2playerY", -7: "2playerVX", -8: "2playerVY", -9: "3playerX", -10: "3playerY", -11: "3playerVX", -12: "3playerVY", -13: "4playerX", -14: "4playerY", -15: "4playerVX", -16: "4playerVY", -17: "1foodX", -18: "1foodY", -19: "2foodX", -20: "2foodY", -21: "3foodX", -22: "3foodY", -23: "4foodX", -24: "4foodY", -25: "1projX", -26: "1projY", -27: "1projVX", -28: "1projVY", -29: "2projX", -30: "2projY", -31: "2projVX", -32: "2projVY", -33: "3projX", -34: "3projY", -35: "3projVX", -36: "3projVY", -37: "4projX", -38: "4projY", -39: "4projVX", -40: "4projVY", -41: "wallR", -42: "wallL", -43: "WallD", -44: "WallU", -45: "VX", -46: "VY", -47: "LifeTimer", -48: "Reserve"}



def loop(simulation):
	print("Starting simulation...")
	while not simulation.done:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return None
		
		if simulation.gamestate is 1:
			print("Real time:")
			print(simulation.time)
			print("Simulation time:")
			print(simulation.simTime)
			print()
			fitnesses = []
			for p in simulation.players:
				fitnesses.append(p.fitness)
			simulation.done = True
			
			return(fitnesses)
		
		t = time.time()
		if realTime:
			dt = t - simulation.lastUpdateTime
		else:
			dt = 1 / targetFPS
		
		if simulation.paused:
			dt = 0
		simulation.lastUpdateTime = t
		simulation.time = t - simulation.startTime
		simulation.simTime += dt
		simulation.frames += 1
		
		simulation.update(dt)
		
		for key, p in enumerate(simulation.players):
			if p.isAlive:
				simulation.getInputs(key)
		if shouldRender:
			simulation.render()
		
	pygame.quit()
	
def startSim(genomes, aiNets):
	simulation = Simulation(pygame, screen, clock, numPlayers, mapSize, numFood, genomes, aiNets, nodeNames, offsetX, offsetY, windowWidth, windowHeight, addHumanPlayer)

	simulation.startTime = time.time()
	simulation.time = 0
	simulation.simTime = 0
	simulation.lastUpdateTime = simulation.startTime
	
	return loop(simulation)

def evaluateFitness(genomes, config):
	aiNets = []
	aiNetIds = []
	for genome_id, genome in genomes:
		aiNets.append(neat.nn.RecurrentNetwork.create(genome, config))
		aiNetIds.append(genome_id)
	
	fitnesses = startSim(genomes, aiNets)
	print(fitnesses)
	
	for genome_id, genome in genomes:
		i = aiNetIds.index(genome_id)
		print(str(i) + " --> " + str(genome_id))
		genome.fitness = fitnesses[i]
	
def runNEAT():
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'config')
	config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
	
	#population = neat.Population(config)
	population = neat.Checkpointer.restore_checkpoint("neat-checkpoint-1956")
	
	population.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	population.add_reporter(stats)
	population.add_reporter(neat.Checkpointer(50))
	
	winner = population.run(evaluateFitness, 2018)

	visualize.draw_net(config, winner, True, node_names=nodeNames)
	visualize.plot_stats(stats, ylog=False, view=True)
	visualize.plot_species(stats, view=True)
	
runNEAT()

