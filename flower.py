from cmu_graphics import *
import random

class Flower:

    # constructor
    def __init__(self):
        self.x = app.width + self.r
        #self.y = random.randrange(app.height)
        self.dx = -3
        self.dy = 2
    
    # moves flower towards player every step
    def takeStep(self):
        self.x += self.dx
        self.y += self.dy
    
    # draws flower
    def draw(self):
        drawImage(self.image, self.x, self.y, 
                  width=self.r*1.9, height = 1.7*self.r, align="center")
    
    # removes obstacle if player avoided it
    def flowerPassed(self):
        if (self.x < 0 - self.r) or (self.y > app.height + self.r):
            return True
        return False

class BigFlower(Flower):

    # image: https://www.cleanpng.com/png-exotic-red-flower-png-image-53394/
    # BG removed with: https://www.remove.bg/

    # constructor
    def __init__(self):
        self.r = random.randrange(20, 25)
        self.x = app.width + self.r
        self.y = -self.r
        self.dx = -3
        self.dy = random.uniform(2, 3)
        self.energy = 4*app.energyLoss
        self.image = app.redFlower

class SmallFlower(Flower):

    # image: https://www.cleanpng.com/png-royalty-free-flower-illustration-petal-drawing-6988270/
    # BG removed with: https://www.remove.bg/

    # constructor
    def __init__(self):
        self.r = random.randrange(18, 23)
        self.x = app.width + self.r
        self.y = -self.r
        self.dx = -3
        self.dy = random.uniform(1, 2)
        self.energy = 2*app.energyLoss
        self.image = app.pinkFlower