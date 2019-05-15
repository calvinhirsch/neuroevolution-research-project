import math

class Character(object):
	
	# Constants
	minShotInterval = 1
	accSpeed = 60
	maxSpeed = 6
	lifeTimerInitial = 10
	radius = 0.6 # in map units
	friction = 4
	reserveInitial = 5
	
	def __init__(self, startX, startY, genome, net, humanControlled):
		self.x = startX
		self.y = startY
		self.net = net
		self.genome = genome
		self.lifeTimer = Character.lifeTimerInitial
		self.humanControlled = humanControlled
		
		self.distance = 0
		self.vx = 0
		self.vy = 0
		self.shotTimer = 0
		self.reserve = Character.reserveInitial
		self.isAlive = True
		self.kills = 0
		self.fitness = -1
	
	def __repr__(self):
		return '{}: {}'.format(self.__class__.__name__, self.distance)
	
	def __cmp__(self, other):
		if hasattr(other, 'distance'):
			return self.distance.__cmp__(other.distance)
	
	def update(self, dt):
		if self.isAlive:
			mag = math.sqrt(self.vx**2 + self.vy**2)
			if mag > Character.maxSpeed:
				self.vx = self.vx / mag * Character.maxSpeed
				self.vy = self.vy / mag * Character.maxSpeed
			
			self.x += self.vx*dt
			self.y += self.vy*dt
			
			self.vx -= Character.friction * self.vx * dt
			self.vy -= Character.friction * self.vy * dt
			
			self.lifeTimer -= dt
			self.shotTimer += dt
	
	def shoot(self):
		# If it's been long enough since the last shot, shoots then returns true
		if self.shotTimer > Character.minShotInterval and self.reserve > 0:
			self.shotTimer = 0
			self.reserve -= 1
			return True
		return False
	
	def kill(self):
		self.isAlive = False