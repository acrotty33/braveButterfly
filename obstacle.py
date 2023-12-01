from cmu_graphics import *
import random
import time
from PIL import Image

# all obstacle images are from Adobe Stock!!
# backgrounds removed with: https://www.remove.bg/

class Obstacle:

    # constructor
    def __init__(self, app):
        self.x = app.width + 30
        self.y = random.randrange(app.height)
        self.dx = -3
        self.r = random.randrange(30, 80)
        self.color = "red"
    
    # moves obstacle towards player every step
    def takeStep(self):
        self.x += self.dx
    
    # draws obstacle
    def draw(self):
        drawImage(self.image, self.x, self.y, width = 2*self.r, height=2*self.r, align="center")

    # removes obstacle if player avoided it
    def obstaclePassed(self):
        if (self.x < 0 - self.r):
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
        # self.color = "yellow"
        # self.spriteCounter = 0
        # self.stepCounter = 0
        self.image = app.waspImage
        level = app.difficulty
        if level == 0:
            if app.timeSurvived < 20: # first level speed
                self.dx = -5
            elif app.timeSurvived < 40: # second level speed
                self.dx = -6
            else:
                self.dx = -7
        if level == 1:
            if app.timeSurvived: # first level speed
                self.dx = -6
            elif app.timeSurvived: # second level speed
                self.dx = -7
            else:
                self.dx = -8
        if level == 2:
            if app.timeSurvived: # first level speed
                self.dx = -7
            elif app.timeSurvived: # second level speed
                self.dx = -8
            else:
                self.dx = -9
        if level == 3:
            if app.timeSurvived < (1/3)*app.timeToSurvive:
                self.dx = app.waspSpeed
            elif app.timeSurvived < (2/3)*app.timeToSurvive:
                self.dx  = app.waspSpeed - 1
            else:
                self.dx = app.waspSpeed - 2
    
    def draw(self):
        drawImage(self.image, self.x, self.y, width = 2*self.r, height=2*self.r, align="center")


class Web(Obstacle):

    # constructor
    def __init__(self, level):
        self.r = random.randrange(0.08*app.width, 0.15*app.width)
        self.x = app.width + self.r
        self.y = self.r
        self.color = "gray"
        self.image = app.webImage

        # self.spriteCounter = 0
        # self.stepCounter = 0
        level = app.difficulty
        if app.nextPlayerSpeed == 0: 
            self.dx = app.firstPlayerSpeed
        else: 
            self.dx = app.nextPlayerSpeed
        # if level == 0:
        #     if app.timeSurvived < 20: # first level speed
        #         self.dx = -3
        #     elif app.timeSurvived < 40: # second level speed
        #         self.dx = -4
        #     else:
        #         self.dx = -5
        # if level == 1:
        #     if app.timeSurvived < 20: # first level speed
        #         self.dx = -4
        #     elif app.timeSurvived < 40: # second level speed
        #         self.dx = -5
        #     else:
        #         self.dx = -6
        # if level == 2:
        #     if app.timeSurvived < 20: # first level speed
        #         self.dx = -5
        #     elif app.timeSurvived < 40: # second level speed
        #         self.dx = -6
        #     else:
        #         self.dx = -7


class Net(Obstacle):

    # constructor
    def __init__(self, level):
        self.r = random.randrange(0.1*app.width, 0.15*app.width)
        self.x = app.width + self.r
        self.y = app.height - self.r
        self.dx = -3
        self.color = "brown"
        self.image = app.netImage
        level = app.difficulty
        if level == 0:
            if app.timeSurvived < 20: # first level speed
                self.dx = -4
            elif app.timeSurvived < 40: # second level speed
                self.dx = -5
            else:
                self.dx = -6
        if level == 1:
            if app.timeSurvived: # first level speed
                self.dx = -5
            elif app.timeSurvived: # second level speed
                self.dx = -6
            else:
                self.dx = -7
        if level == 2:
            if app.timeSurvived < 20: # first level speed
                self.dx = -6
            elif app.timeSurvived < 40: # second level speed
                self.dx = -7
            else:
                self.dx = -8
        if level == 3:
            if app.timeSurvived < (1/3)*app.timeToSurvive:
                self.dx = app.netSpeed
            elif app.timeSurvived < (2/3)*app.timeToSurvive:
                self.dx -= 1
            else:
                self.dx -= 1
        
    def draw(self):
        drawImage(self.image, self.x, self.y + 0.75*self.r, width = 4*self.r, height=4*self.r, align="center")