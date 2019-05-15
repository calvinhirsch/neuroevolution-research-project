import pygame
import pygame
import math
from character import *
from proj import *
import time
from operator import attrgetter, itemgetter
import neat
import os
import visualize


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 180, 0)
RED = (255, 0, 0)

# Cross product of two vectors


class Simulation(object):
	
	# Constants
	rebound = 0.75 # fraction of momentum reversed when colliding with a wall
	camMoveSpeed = 30
	zoomSpeed = 20
	foodRadius = 0.25
	foodLifeAddition = 5
	foodReserveAddition = 2
	projectileSpeed = 30
	maxFreq = 20000
	minFreq = 1
	
	
	endWindowH = 200
	endWindowW = 400
	
	def __init__(self, game, screen, clock, playerCount, mapSize, foodCount, genomes, aiNets, nodeNames, startX, startY, width, height, addHumanPlayer):
		self.game = game
		self.screen = screen
		self.clock = clock
		self.playerCount = playerCount
		self.mapSize = mapSize
		self.foodCount = foodCount
		self.aiNets = aiNets
		self.startX = startX
		self.startY = startY
		self.width = width
		self.height = height
		self.addHumanPlayer = addHumanPlayer
		self.nodeNames = nodeNames
				
		self.gamestate = 0 # running: 0, game over: 1
		self.paused = False
		self.wasHoldingPause = False
		
		self.done = False
		
		local_dir = os.path.dirname(__file__)
		config_path = os.path.join(local_dir, 'config')
		self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
		
		self.camX = mapSize / 2
		self.camY = mapSize / 2
		
		if width <= height:
			self.minZoom = width / mapSize
		else:
			self.minZoom = height / mapSize
		
		self.zoom = self.minZoom
		
		self.fps = 60
		self.frames = 0
		
		self.projectiles = []
		self.soundSources = []
		
		# Creating + spawning players
		rowCount = math.ceil(math.sqrt(playerCount))
		spacing = mapSize / (rowCount + 1)
		
		self.players = []
				
		for i in range(rowCount):
			for j in range(rowCount):
				x = i * rowCount + j
				if x < self.playerCount:
					net = None
					genome = None
					if len(aiNets) > x:
						net = aiNets[x - 1]
						genome = genomes[x - 1][1]
					if i + j is self.playerCount - 1 and self.addHumanPlayer:
						self.players.append(Character((i + 1) * spacing, (j + 1) * spacing, genome, net, True))
					else:
						self.players.append(Character((i + 1) * spacing, (j + 1) * spacing, genome, net, False))
					
		# Creating food
		foodRowCount = math.ceil(math.sqrt(foodCount))
		foodSpacing = mapSize / (foodRowCount + 1)
		
		self.food = []
		
		for i in range(foodRowCount):
			for j in range(foodRowCount):
				if i + j < self.foodCount:
					self.food.append([(i + 1) * foodSpacing, (j + 1) * foodSpacing])
		
	def update(self, dt):
	
		keys = pygame.key.get_pressed()
		
		id = len(self.players) - 1
		p = self.players[id]
		if p.isAlive and self.addHumanPlayer:
			if keys[pygame.K_d]:
				p.vx += Character.accSpeed * dt
			if keys[pygame.K_a]:
				p.vx -= Character.accSpeed * dt
			if keys[pygame.K_w]:
				p.vy -= Character.accSpeed * dt
			if keys[pygame.K_s]:
				self.players[len(self.players) - 1].vy += Character.accSpeed * dt
			if keys[pygame.K_RIGHT]:
				if p.shoot():
					self.projectiles.append(Projectile(p.x, p.y, p.vx + Simulation.projectileSpeed, p.vy, id))
			if keys[pygame.K_LEFT]:
				if p.shoot():
					self.projectiles.append(Projectile(p.x, p.y, p.vx - Simulation.projectileSpeed, p.vy, id))
			if keys[pygame.K_UP]:
				if p.shoot():
					self.projectiles.append(Projectile(p.x, p.y, p.vx, p.vy - Simulation.projectileSpeed, id))
			if keys[pygame.K_DOWN]:
				if p.shoot():
					self.projectiles.append(Projectile(p.x, p.y, p.vx, p.vy + Simulation.projectileSpeed, id))
			
		
		if keys[pygame.K_l]:
			self.camX += Simulation.camMoveSpeed * dt
		if keys[pygame.K_j]:
			self.camX -= Simulation.camMoveSpeed * dt
		if keys[pygame.K_i]:
			self.camY -= Simulation.camMoveSpeed * dt
		if keys[pygame.K_k]:
			self.camY += Simulation.camMoveSpeed * dt
		if keys[pygame.K_LEFTBRACKET]:
			self.zoom -= Simulation.zoomSpeed * dt
		if keys[pygame.K_RIGHTBRACKET]:
			self.zoom += Simulation.zoomSpeed * dt
		if keys[pygame.K_0]:
			self.zoom = self.minZoom
		if keys[pygame.K_SPACE]:
			if not self.wasHoldingPause:
				self.paused = not self.paused
			self.wasHoldingPause = True
		else:
			self.wasHoldingPause = False
			
		if pygame.mouse.get_pressed()[0]:
			position = pygame.mouse.get_pos()
			offsetX = self.camX - (self.width / 2 / self.zoom)
			offsetY = self.camY - (self.height / 2 / self.zoom)
			for index, p in enumerate(self.players):
				centerX = (p.x - offsetX) * self.zoom
				centerY = (p.y - offsetY) * self.zoom
				d = ((centerX - position[0])**2 + (centerY - position[1])**2)**(1/2)
				if d < Character.radius * self.zoom:
					print("Drawing net #"+str(index))
					visualize.draw_net(self.config, p.genome, True, node_names=self.nodeNames)
			
				
		if self.zoom < self.minZoom:
			self.zoom = self.minZoom
		if self.camX < self.width / self.zoom / 2:
			self.camX = self.width / self.zoom / 2
		elif self.camX > self.mapSize - (self.width / self.zoom / 2):
			self.camX = self.mapSize - (self.width / self.zoom / 2)
		if self.camY < self.height / self.zoom / 2:
			self.camY = self.height / self.zoom / 2
		elif self.camY > self.mapSize - (self.height / self.zoom / 2):
			self.camY = self.mapSize - (self.height / self.zoom / 2)
		
		aliveCount = 0
		
		for index, p in enumerate(self.players):
			p.update(dt)
			buttonsPressed = [False,False,False,False,False,False,False,False]
			if p.net is not None:
				# w, s, d, a, up, down, left, right
				buttonsPressed = p.net.activate(self.getInputs(index))
						
			if buttonsPressed[0] >= 1:
				p.vy -= Character.accSpeed * dt
			if buttonsPressed[1] >= 1:
				p.vy += Character.accSpeed * dt
			if buttonsPressed[2] >= 1:
				p.vx += Character.accSpeed * dt
			if buttonsPressed[3] >= 1:
				p.vx -= Character.accSpeed * dt
			if buttonsPressed[4] >= 1:
				if p.shoot():
					self.projectiles.append(Projectile(p.x, p.y, p.vx, p.vy - Simulation.projectileSpeed, index))
			if buttonsPressed[5] >= 1:
				if p.shoot():
					self.projectiles.append(Projectile(p.x, p.y, p.vx, p.vy + Simulation.projectileSpeed, index))
			if buttonsPressed[6] >= 1:
				if p.shoot():
					self.projectiles.append(Projectile(p.x, p.y, p.vx - Simulation.projectileSpeed, p.vy, index))
			if buttonsPressed[7] >= 1:
				if p.shoot():
					self.projectiles.append(Projectile(p.x, p.y, p.vx + Simulation.projectileSpeed, p.vy, index))
			
			if p.x > self.mapSize - Character.radius:
				p.x = self.mapSize - Character.radius
				p.vx = p.vx * -1 * Simulation.rebound
			elif p.x < Character.radius:
				p.x = Character.radius
				p.vx = p.vx * -1 * Simulation.rebound
			if p.y > self.mapSize - Character.radius:
				p.y = self.mapSize - Character.radius
				p.vy = p.vy * -1 * Simulation.rebound
			elif p.y < Character.radius:
				p.y = Character.radius
				p.vy = p.vy * -1 * Simulation.rebound
			
			if p.isAlive and p.lifeTimer < 0:
				p.kill()
				p.fitness = self.calculateFitness(p)
			
			if p.isAlive:
				aliveCount += 1
			
			# Check food eating
			for f in self.food:
				if (p.x - f[0])**2 + (p.y - f[1])**2 < (Simulation.foodRadius + Character.radius)**2:
					self.food.remove(f)
					p.lifeTimer += Simulation.foodLifeAddition
					p.reserve += Simulation.foodReserveAddition
		
		# print(aliveCount)
		if aliveCount <= 1 and self.gamestate is 0:
			print("Game over")
			for p in self.players:
				if p.fitness is -1:
					p.fitness = self.calculateFitness(p)
			self.gamestate = 1
		
		for p in self.projectiles:
			if (p.update(dt)):
				for index, player in enumerate(self.players):
					if player.isAlive:
						radii = Character.radius + Projectile.radius
						withinX = False
						withinY = False
						
						if p.lastX < p.x:
							withinX = player.x > p.lastX - radii and player.x < p.x + radii
						else:
							withinX = player.x > p.x - radii and player.x < p.lastX + radii
						if p.lastY < p.y:
							withinY = player.y > p.lastY - radii and player.y < p.y + radii
						else:
							withinY = player.y > p.y - radii and player.y < p.lastY + radii
						
						if withinX and withinY and p.ownerID is not index:
							dirVec = [p.x - p.lastX, p.y - p.lastY, 0]
							pq = [player.x - p.x, player.y - p.y, 0]
							# distance from point (player) to line (direction vector of projectile)
							if mag(cross(dirVec, pq)) / mag(dirVec) < (Character.radius + Projectile.radius):
								player.kill()
								player.fitness = self.calculateFitness(player)
								self.players[p.ownerID].lifeTimer += player.lifeTimer
								self.players[p.ownerID].reserve += player.reserve
								self.players[p.ownerID].kills += 1
								self.projectiles.remove(p)
								break
			else:
				self.projectiles.remove(p)
		
		# if self.gamestate is 1:
			# check mouse click location
			
	def render(self):
		self.screen.fill(WHITE)
		
		offsetX = self.camX - (self.width / 2 / self.zoom)
		offsetY = self.camY - (self.height / 2 / self.zoom)
		for p in self.players:
			if p.isAlive:
				centerX = (p.x - offsetX) * self.zoom
				centerY = (p.y - offsetY) * self.zoom
				
				if centerX > 0 and centerX < self.width and centerY > 0 and centerY < self.height:
					pos = [int(centerX), int(centerY)]
					self.game.draw.circle(self.screen, BLACK, pos, int(Character.radius * self.zoom), 0)
		
		for f in self.food:
			centerX = (f[0] - offsetX) * self.zoom
			centerY = (f[1] - offsetY) * self.zoom
			
			if centerX > 0 and centerX < self.width and centerY > 0 and centerY < self.height:
				pos = [int(centerX), int(centerY)]
				self.game.draw.circle(self.screen, GREEN, pos, int(Simulation.foodRadius * self.zoom), 0)
		
		for p in self.projectiles:
			centerX = (p.x - offsetX) * self.zoom
			centerY = (p.y - offsetY) * self.zoom
			
			if centerX > 0 and centerX < self.width and centerY > 0 and centerY < self.height:
				pos = [int(centerX), int(centerY)]
				self.game.draw.circle(self.screen, RED, pos, int(Projectile.radius * self.zoom), 0)
		
		font = pygame.font.SysFont(None, 48)
		
		t = "0"
		if self.time > 0.1:
			t = str(int(self.frames / self.time))
		t1 = " >"
		if self.paused:
			t1 = " ||"
		t = t + t1
			
		text = font.render(t, True, BLACK, WHITE)
		textrect = text.get_rect()
		textrect.centerx = 80
		textrect.centery = 50
		self.screen.blit(text, textrect)
		
		# Update
		self.game.display.flip()

	def getInputs(self, playerID):
		# closestplayer: xdis,ydis,vx,vy (repeat with 2nd-4th closest players and 1st-4th closest food and projectiles)
		# wall distance on each side
		# self.vx,vy,lifetimer,reserve,soundfreq,soundamp
				
		p = self.players[playerID]
		for player in self.players:
			if player.isAlive:
				player.distanceX = player.x - p.x
				player.distanceY = player.y - p.y
				player.distance = (player.distanceX**2 + player.distanceY**2)**(0.5)
			else:
				player.distanceX = 999999
				player.distanceY = 999999
				player.distance = 99999999
			
			if player.distanceX < 0.00001 and player.distanceX >= 0:
				player.distanceX = 0.00001
			elif player.distanceX > -0.00001 and player.distanceX < 0:
				player.distanceX = -0.00001
			if player.distanceY < 0.00001 and player.distanceY >= 0:
				player.distanceY = 0.00001
			elif player.distanceY > -0.00001 and player.distanceY < 0:
				player.distanceY = -0.00001
				
		sortedPlayers = sorted(self.players, key=attrgetter("distance"))
		
		foodDistances = []
		for f in self.food:
			dx = f[0] - p.x
			dy = f[1] - p.y
			if dx < 0.00001 and dx >= 0:
				dx = 0.000001
			elif dx > -0.00001 and dx < 0:
				dx = -0.00001
			if dy < 0.00001 and dx >= 0:
				dy = 0.00001
			elif dy > -0.00001 and dx < 0:
				dy = -0.00001
			foodDistances.append([dx, dy, (dx**2+dy**2)**(0.5)])
		
		sortedFood = sorted(foodDistances, key=itemgetter(2))
		
		for proj in self.projectiles:
			proj.distanceX = proj.x - p.x
			if proj.distanceX < 0.00001 and proj.distanceX >= 0:
				proj.distanceX = 0.00001
			elif proj.distanceX > -0.00001 and proj.distanceX < 0:
				proj.distanceX = -0.00001
			
			proj.distanceY = proj.y - p.y
			if proj.distanceY < 0.00001 and proj.distanceY >= 0:
				proj.distanceY = 0.00001
			elif proj.distanceY > -0.00001 and proj.distanceY < 0:
				proj.distanceY = -0.00001
			
			proj.tempDist = (proj.distanceX**2 + proj.distanceY**2)**(0.5)
		
		sortedProj = sorted(self.projectiles, key=attrgetter("tempDist"))
		
		inputs = []
		
		# Nearest players
		for i in range(4):
			inputs.extend([1/sortedPlayers[i + 1].distanceX, 1/sortedPlayers[i + 1].distanceY, sortedPlayers[i + 1].vx, sortedPlayers[i + 1].vy])
				
		# Nearest food
		numFood = len(self.food)
		if numFood > 4:
			numFood = 4
		for i in range(numFood):
			inputs.extend([1/foodDistances[i][0], 1/foodDistances[i][1]])
		for i in range(4 - numFood):
			inputs.extend([0, 0])
				
		# Nearest projectiles
		numProj = len(self.projectiles)
		if numProj > 4:
			numProj = 4
		for i in range(numProj):
			inputs.extend([1/(sortedProj[i].distanceX), 1/(sortedProj[i].distanceY), sortedProj[i].vx, sortedProj[0].vy])
		for i in range(4 - numProj):
			inputs.extend([0, 0, 0, 0])
				
		# Wall distances
		inputs.extend([1/(self.mapSize - p.x), 1/(p.x), 1/(self.mapSize - p.y), 1/(p.y)])
		# Self attributes
		inputs.extend([p.vx, p.vy, 1/p.lifeTimer, p.reserve])
				
		return inputs
	
	def calculateFitness(self, p):
		t = self.simTime
		if p.isAlive:
			# Add life timer onto game timer to get total time survived, multiply by 1.2 because they are the last one alive
			t += p.lifeTimer
			t *= 1.2
		return t
		