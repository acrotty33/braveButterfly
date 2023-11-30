from cmu_graphics import *
import random
from PIL import Image
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
        #drawCircle(self.x, self.y, self.r, fill = self.color)
        drawImage(self.image, self.x, self.y, align="center")
    
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
        self.r = 15
        self.x = app.width + self.r
        self.y = -self.r
        self.dx = -3
        self.dy = 2
        self.color = "red"
        self.energy = 1.25
        #self.image = CMUImage(Image.open("images/redFlowerNoBG.png"))
        image = Image.open("images/redFlowerNoBG.png")
        new = image.resize((image.size[0]//8, image.size[1]//8))
        self.image = CMUImage(new)

class SmallFlower(Flower):

    # image: https://www.cleanpng.com/png-royalty-free-flower-illustration-petal-drawing-6988270/
    # BG removed with: https://www.remove.bg/

    # constructor
    def __init__(self):
        self.r = 15
        self.x = app.width + self.r
        self.y = -self.r
        self.dx = -3
        self.dy = 2
        self.color = "pink"
        self.energy = 0.5
        # fr = flyGif.resize((flyGif.size[0]//5, flyGif.size[1]//5))
        image = Image.open("images/pinkFlowerNoBG.png")
        new = image.resize((image.size[0]//10, image.size[1]//10))
        self.image = CMUImage(new)