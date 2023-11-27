from cmu_graphics import *
import random
# import time

class Flower:

    # constructor
    def __init__(self):
        self.r = random.randrange(5,10)
        self.x = app.width + self.r
        self.y = random.randrange(app.height)
        self.dx = -3
        self.dy = 2
        self.color = "pink"
        self.energy = 0.5
    
    # moves flower towards player every step
    def takeStep(self):
        self.x += self.dx
        self.y += self.dy
    
    # draws flower
    def draw(self):
        drawCircle(self.x, self.y, self.r, fill = self.color)
    
    # removes obstacle if player avoided it
    def flowerPassed(self):
        if (self.x < 0 - self.r) or (self.y > app.height + self.r):
            return True
        return False

class BigFlower(Flower):
    # constructor
    def __init__(self):
        self.r = random.randrange(15,20)
        self.x = app.width + self.r
        self.y = -self.r
        self.dx = -3
        self.dy = 2
        self.color = "red"
        self.energy = 1.25

class SmallFlower(Flower):

    # constructor
    def __init__(self):
        self.r = random.randrange(10,15)
        self.x = app.width + self.r
        self.y = -self.r
        self.dx = -3
        self.dy = 2
        self.color = "pink"
        self.energy = 0.5