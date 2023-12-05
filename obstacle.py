from cmu_graphics import *
import random

# wasp and web obstacle images are from Adobe Stock!!
# backgrounds removed with: https://www.remove.bg/

class Obstacle:
    # constructor
    def __init__(self, app):
        self.x = app.width + 30
        self.y = random.randrange(app.height)
        self.dx = -3
    
    # moves obstacle towards player every step
    def takeStep(self):
        self.x += self.dx
    
    # draws obstacle
    def draw(self):
        drawImage(self.image, self.x, self.y, width = 2*self.r, height=2*self.r, 
                  align="center")

    # removes obstacle if player avoided it
    def obstaclePassed(self):
        if (self.x < 0 - 2*self.r):
            return True
        return False
    
    # checks if two obstacles are conjoined
    def inOtherObstacle(self, other):
        if isinstance(other, Obstacle):
            x = self.x - other.x
            y = self.y - other.y
            r = self.r + other.r
            if (x**2 + y**2)**0.5 <= r:
                return True
        return False

class Wasp(Obstacle):

    # constructor
    def __init__(self, level):
        self.r = random.randrange(0.02*app.width, 0.04*app.width)
        self.x = app.width + self.r
        self.y = random.randrange(30, app.height-30)
        self.image = app.waspImage
        level = app.difficulty
        if level == 0:
            if app.timeSurvived < 20: # first level speed
                self.dx = -7
            elif app.timeSurvived < 40: # second level speed
                self.dx = -8
            else:
                self.dx = -9
        if level == 1:
            if app.timeSurvived: # first level speed
                self.dx = -8
            elif app.timeSurvived: # second level speed
                self.dx = -9
            else:
                self.dx = -10
        if level == 2:
            if app.timeSurvived: # first level speed
                self.dx = -9
            elif app.timeSurvived: # second level speed
                self.dx = -10
            else:
                self.dx = -11
        if level == 3:
            if app.timeSurvived < (1/3)*app.timeToSurvive:
                self.dx = app.waspSpeed
            elif app.timeSurvived < (2/3)*app.timeToSurvive:
                self.dx  = app.waspSpeed - 1
            else:
                self.dx = app.waspSpeed - 2
    
    def draw(self):
        drawImage(self.image, self.x, self.y, 
                  width = 2*self.r, height=2*self.r, align="center")

class Web(Obstacle):

    # constructor
    def __init__(self, level):
        self.r = random.randrange(0.08*app.width, 0.15*app.width)
        self.x = app.width + self.r
        self.y = random.choice((self.r, app.height-self.r))
        self.image = app.webImage
        self.dx = app.playerSpeed
    
    def draw(self):
        drawImage(self.image, self.x, self.y, 
                  width = 1.8*self.r, height=1.8*self.r, align="center")

# image (uncropped): https://www.mycutegraphics.com/graphics/letter/net.html
class Net(Obstacle):

    # constructor
    def __init__(self, level):
        self.r = random.randrange(0.1*app.width, 0.15*app.width)
        self.x = app.width + self.r
        self.y = random.choice((self.r - 10, app.height-self.r+10)) # 10s are because the image height is too short
        self.dx = -6
        if self.y > self.r: 
            self.image = app.netImage
        else: # flip image if it's on the top of the screen
            self.image = app.flippedNetImage 
        level = app.difficulty
        if level == 0:
            if app.timeSurvived < 20: # first level speed
                self.dx = -6
            elif app.timeSurvived < 40: # second level speed
                self.dx = -7
            else:
                self.dx = -8
        if level == 1:
            if app.timeSurvived: # first level speed
                self.dx = -7
            elif app.timeSurvived: # second level speed
                self.dx = -8
            else:
                self.dx = -9
        if level == 2:
            if app.timeSurvived < 20: # first level speed
                self.dx = -8
            elif app.timeSurvived < 40: # second level speed
                self.dx = -9
            else:
                self.dx = -10
        if level == 3:
            if app.timeSurvived < (1/3)*app.timeToSurvive:
                self.dx = app.netSpeed
            elif app.timeSurvived < (2/3)*app.timeToSurvive:
                self.dx -= 1
            else:
                self.dx -= 1
        
    def draw(self):
        drawImage(self.image, self.x, self.y, 
                  width = 1.8*self.r, height=1.9*self.r, align="center")