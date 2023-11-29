from cmu_graphics import *
import random
import time

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
        drawCircle(self.x, self.y, self.r, fill = self.color)
    
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
        self.color = "yellow"
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

class Web(Obstacle):

    # constructor
    def __init__(self, level):
        self.r = random.randrange(0.08*app.width, 0.15*app.width)
        self.x = app.width + self.r
        self.y = self.r
        self.color = "gray"
        level = app.difficulty
        if level == 0:
            if app.timeSurvived < 20: # first level speed
                self.dx = -3
            elif app.timeSurvived < 40: # second level speed
                self.dx = -4
            else:
                self.dx = -5
        if level == 1:
            if app.timeSurvived < 20: # first level speed
                self.dx = -4
            elif app.timeSurvived < 40: # second level speed
                self.dx = -5
            else:
                self.dx = -6
        if level == 2:
            if app.timeSurvived < 20: # first level speed
                self.dx = -5
            elif app.timeSurvived < 40: # second level speed
                self.dx = -6
            else:
                self.dx = -7

class Net(Obstacle):

    # constructor
    def __init__(self, level):
        self.r = random.randrange(0.08*app.width, 0.15*app.width)
        self.x = app.width + self.r
        self.y = app.height - self.r
        self.dx = -3
        self.color = "brown"
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