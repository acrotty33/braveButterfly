from cmu_graphics import *
from obstacle import *
class Player:

    # constructor
    def __init__(self):
        self.color = "blue"
        self.reset()
        self.energy = 10
    
    # resets player when game resets
    def reset(self):
        self.stepCounter = 0
        self.x = 100
        self.y = 100
        self.r = 20
        self.dy = 0 # velocity downwords
        self.ddy = 0.1 # acceleration downwards
    
    # draws player
    def draw(self):
        drawCircle(self.x, self.y, self.r, fill=self.color)
    
    # manages player falling
    def takeStep(self):
        self.stepCounter += 1
        if self.stepCounter >= 15:
            # sprite movement
            self.stepCounter = 0
        self.y += self.dy
        self.dy += self.ddy
    
    # manages player jumping
    def jump(self):
        #self.y -= app.height/8
        self.dy = -4
        self.ddy = 0.2
        self.energy -= 0.25        
    
    # checks if player hit an obstacle
    def isColliding(self, obstacles):
        for obstacle in obstacles:
            x = self.x - obstacle.x
            y = self.y - obstacle.y
            if (x**2 + y**2)**0.5 < obstacle.r + self.r:
                if isinstance(obstacle, Wasp): app.death = 1
                elif isinstance(obstacle, Web): app.death = 2
                elif isinstance(obstacle, Net): app.death = 3
                return True
        return False
    
    # checks if player nabbed a flower
    def gotFlower(self, flower):
        x = self.x - flower.x
        y = self.y - flower.y
        if (x**2 + y**2)**0.5 <= flower.r + 20:
            app.numFlowersCaught += 1
            return True
        return False
    
    # adds energy from a caught flower, but only up to 10 energy points
    def addEnergy(self, flower):
        if self.energy < 10-flower.energy:
            self.energy += flower.energy
        else:
            self.energy = 10
