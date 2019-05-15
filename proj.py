import math

def cross(a, b):
    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]

    return c

def mag(a):
	c = (a[0]**2 + a[1]**2)**(1/2)
	return c

	
class Projectile:
	
	# Constants
	radius = 0.4
	range = 15
	
	def __init__(self, x, y, vx, vy, ownerID):
		self.x = x
		self.y = y
		self.vx = vx
		self.vy = vy
		self.ownerID = ownerID
		self.lastX = x
		self.lastY = y
		self.distance = 0
		
		self.tempDist = 9999999
		self.distanceX = 9999999
		self.distanceY = 9999999
	
	def __repr__(self):
		return '{}: {}'.format(self.__class__.__name__, self.tempDist)
	
	def __cmp__(self, other):
		if hasattr(other, 'tempDist'):
			return self.tempDist.__cmp__(other.tempDist)
	
	def update(self, dt):
		dx = self.vx * dt
		dy = self.vy * dt
		self.lastX = self.x
		self.lastY = self.y
		self.x += dx
		self.y += dy
		self.distance += mag([dx, dy])
		if self.distance > Projectile.range:
			return False
		return True