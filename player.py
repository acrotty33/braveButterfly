from cmu_graphics import *
from obstacle import *
from PIL import Image

# all sprite stuff is code from lecture demos

class Player:

    # constructor
    def __init__(self):
        self.energy = 10

        # sprites, code is from animated gif lecture demo
        # pink buttefly: https://tenor.com/view/butterfly-freedom-pretty-nature-fly-gif-14485865
        # orange butterfly: https://tenor.com/view/butterfly-freedom-pretty-nature-fly-gif-14485862
        # red butterfly: https://tenor.com/view/butterfly-freedom-pretty-nature-fly-gif-14485863
        # blue butterfly: https://tenor.com/view/butterfly-blue-butterfly-freedom-pretty-nature-gif-14485845
        # light teal butterfly: https://tenor.com/view/butterfly-blue-butterfly-freedom-pretty-nature-gif-14485854
        self.reset()
    
    # resets player when game resets
    def reset(self):
        self.stepCounter = 0
        self.spriteCounter = 0
        self.x = 150
        self.y = 200
        self.r = 20
        self.dy = 0 # velocity downwords
        self.ddy = 0.1 # acceleration downwards
    
    # draws player, code from animated gif demo lecture
    def draw(self, x, y):
        # sprites, code is from animated gif lecture demo
        # pink buttefly: https://tenor.com/view/butterfly-freedom-pretty-nature-fly-gif-14485865
        # orange butterfly: https://tenor.com/view/butterfly-freedom-pretty-nature-fly-gif-14485862
        # red butterfly: https://tenor.com/view/butterfly-freedom-pretty-nature-fly-gif-14485863
        # blue butterfly: https://tenor.com/view/butterfly-blue-butterfly-freedom-pretty-nature-gif-14485845
        # light teal butterfly: https://tenor.com/view/butterfly-blue-butterfly-freedom-pretty-nature-gif-14485854
        if app.playerColor == "red":
            flyGif = Image.open("images/red.gif")
        elif app.playerColor == "pink":
            flyGif = Image.open("images/pink.gif")
        elif app.playerColor == "orange":
            flyGif = Image.open("images/orange.gif")
        elif app.playerColor == "lightTeal":
            flyGif = Image.open("images/light-teal.gif")
        else:
            flyGif = Image.open("images/blue.gif")

        self.spriteList = [] 
        for frame in range(flyGif.n_frames):
            flyGif.seek(frame)
            fr = flyGif.resize((flyGif.size[0]//5, flyGif.size[1]//5))
            fr = CMUImage(fr)
            self.spriteList.append(fr)
        butterfly = self.spriteList[self.spriteCounter]
        drawImage(butterfly, x, y, align="center")
    
    # manages player falling + sprite movement
    def takeStep(self):
        self.stepCounter += 1
        if self.stepCounter >= 10:
            # sprite movement
            self.spriteCounter = (self.spriteCounter + 1) % len(self.spriteList)
            self.stepCounter = 0
        self.y += self.dy
        self.dy += self.ddy
    
    # manages player jumping
    def jump(self):
        self.dy = -4
        self.ddy = 0.2
        self.energy -= app.energyLoss       
    
    # checks if player hit an obstacle
    def isColliding(self, obstacles):
        for obstacle in obstacles:
            x = self.x - obstacle.x
            y = self.y - obstacle.y
            if (x**2 + y**2)**0.5 < obstacle.r + self.r - 10:
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
