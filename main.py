'''
ISSUES:
- player jump height unknown, isSurvivable ???
    - add isSurvivable condition when generating obstacles

THINGS TO ADD:
- working difficulty selection
- sprites: butterflies(3), wasp, net, web, flowers(2)
- moving/infinite background
- win screen confetti animation
- custom levels?
- wind???
'''

from cmu_graphics import *
from player import Player
from obstacle import *
from flower import *
import random
import time

def onAppStart(app):
    restartApp(app)

def restartApp(app):
    app.player = Player()
    app.obstacles = []
    app.flowers = []
    app.stepsPerSecond = 30
    app.startTime = time.time()
    app.lastSummonedObstacle = app.lastSummonedFlower = time.time()
    app.numFlowersCaught = 0

    app.freqObstacles = 5 # every [num] steps, generate an obstacle
    app.freqFlowers = 5
    app.numObstacles = 7
    app.numFlowers = 4
    app.difficulty = 0 # 0 = easy, 1 = medium, 2 = hard, 3+ = custom

    app.startMenu = False
    app.gameOver = False
    app.paused = False
    app.won = False
    app.death = 0

def onStep(app):
    # if time.time() > 5:
    #     app.startMenu = False
    if not app.paused:
        app.player.takeStep()
    if app.gameOver: return

    # player won
    if time.time() - app.startTime >= 60:
        app.won = True

    # summoning obstacles smartly
    numSummoning = random.randrange(1, app.numObstacles) # number of obstacles
    if not app.paused:
        # removing obstacles if player passes them
        obIndex = 0
        while obIndex < len(app.obstacles):
            obstacle = app.obstacles[obIndex]
            obstacle.takeStep()
            if obstacle.obstaclePassed():
                app.obstacles.pop(obIndex) # delete obstacle when it's passed
            else:
                obIndex += 1
        
        # removing flowers if player passes them
        flowerIndex = 0
        while flowerIndex < len(app.flowers):
            flower = app.flowers[flowerIndex]
            flower.takeStep()
            if flower.flowerPassed():
                app.flowers.pop(flowerIndex) # delete flower when it's passed
            else:
                flowerIndex += 1
    
        # summoning obstacles
        enoughTimePassed = time.time() - app.lastSummonedObstacle > 1
        if enoughTimePassed and (len(app.obstacles) < numSummoning):
            obstacle = randomObstacle(app, random.randrange(10))
            # makes sure obstacles aren't conjoined
            for ob in app.obstacles:
                if type(obstacle) == type(ob):
                    while obstacle.inOtherObstacle(ob) and not isSurvivable(app, obstacle): ############## ADD SURVIVIABLE CONDITION!!!!!
                        obstacle = randomObstacle(app, random.randrange(10))
            app.obstacles.append(obstacle)
            # print(type(obstacle), obstacle.dx)
            app.lastSummonedObstacle = time.time()
        
    # summoning flowers
    if not app.paused:
        numFlowersSummoning = random.randrange(0, app.numFlowers)
        flowerTime = time.time() - app.lastSummonedFlower > 2
        if flowerTime and (len(app.flowers) < numFlowersSummoning):
            flower = randomFlower(app, random.randrange(10))
            app.flowers.append(flower)
            app.lastSummonedFlower = time.time()
        
        # if player touched a flower, give player energy
        i = 0
        while i < len(app.flowers):
            if app.player.gotFlower(app.flowers[i]):
                app.player.addEnergy(app.flowers[i])
                app.flowers.pop(i)
            else:
                i += 1

    # full energy depletion = lose condition 
    if app.player.energy <= 0:
        app.death = 0
        app.gameOver = True
    
    # game over if player hits an obstacle or touches bottom/top of screen
    playerFell = app.player.y >= app.height
    playerTooHigh = app.player.y < 0
    if app.player.isColliding(app.obstacles) or playerFell or playerTooHigh:
        if playerFell: app.death = 4
        elif playerTooHigh: app.death = 5
        app.gameOver = True

def onKeyPress(app, key):
    if key == "space" and not app.gameOver and not app.paused:
        app.player.jump()
    if key == "p" and not app.gameOver:
        app.paused = not app.paused
    if key == "r":
        restartApp(app)

def redrawAll(app):
    if app.startMenu:
        drawStartMenu(app)
    elif app.won:
        drawWinScreen(app)
    else:
        drawRect(0, 0, app.width, app.height, fill = "lightskyblue")
        for obstacle in app.obstacles:
            obstacle.draw()
        for flower in app.flowers:
            flower.draw()
        drawEnergyBar(app)
        
        # draw game over screen
        if app.gameOver:
            drawLoseScreen(app)
        
        # draws player dying
        app.player.draw()

def onMousePress(app, mousex, mousey):
    if app.startMenu:
        pass
    pass

# generates an obstacle
def randomObstacle(app, num):
    if num < 3:
        return Web(app.difficulty)
    elif num > 8:
        return Net(app.difficulty)
    else:
        return Wasp(app.difficulty)

# generates a flower
def randomFlower(app, num):
    if num < 7:
        return SmallFlower()
    else:
        return BigFlower()

# checks if the obstacles are passable
def isSurvivable(app, potentialObstacle):
    potentialObList = app.obstacles + [potentialObstacle]
    # get a list of all the x values and radii of obstacles, including potential
    for i in range(len(potentialObList)):
        curr = potentialObList[i]
        withinSameishX = [curr] 
        # makes a list of obstacles within sameish x
        # sameish x means within curr's x +/- combinedRadii of curr and other
        for j in range(i+1, len(potentialObList)):
            other = potentialObList[j]
            combinedRadii = curr.r + other.r
            if (other.x < curr.x + combinedRadii):
                withinSameishX.append(other)
        # now checking if there's at least one gap between sameishX obstacles
        # that the player's jump can fit through
        for k in range(len(withinSameishX)):
            if k < len(withinSameishX)-1:
                first = withinSameishX[k]
                next = withinSameishX[k+1]
                y = abs(first.y - next.y)
                r = first.r + next.r
                if y - r > 10: # REPLACE ONE WITH JUMP HEIGHT
                    return True
    return False

def drawStartMenu(app):
    drawRect(0, 0, app.width, app.height, fill = "lightskyblue")
    drawLabel("Start Menu", app.width/2, app.height/10, size = 36, 
              bold = True, font="montserrat")
    
    difficultySelected = False
    # difficulty selection
    drawLabel("Click to choose a difficulty level", 
              app.width/2, app.height/4, size = 24)
    easyx = app.width/8
    drawLabel("Easy", app.width/8, app.height/3, size = 20, italic = True)

    intermediatex = easyx + 100
    drawLabel("Intermediate", intermediatex, app.height/3, size=20, italic=True)

    hardx = easyx + 200
    drawLabel("Hard", hardx, app.height/3, size=20, italic=True)

    
    # butterfly color selection
    colors = ["red", "orange", "yellow", "green", "blue", "purple", "pink"]

# draws and updates player's energy bar
def drawEnergyBar(app):
    energyRatio = app.player.energy/10
    color = None
    if app.player.energy < 3:
        color = "red"
    elif app.player.energy < 6:
        color = "yellow"
    else:
        color = "green"
    
    # draw used energy
    barTopX = 20
    barTopY = 10
    barWidth = 20
    fullBarHeight = app.height/2-30
    drawRect(barTopX, barTopY, barWidth, fullBarHeight, fill=None, border=color)

    # draw energy that's still left
    topY = 10 + (1-energyRatio)*fullBarHeight
    if energyRatio > 0: 
        drawRect(barTopX, topY, barWidth, energyRatio*fullBarHeight, fill=color, 
                 border=color)
    
    # draw energy label
    labelX = barTopX + barWidth/2
    labelY = 20 + fullBarHeight
    drawLabel("Energy", labelX, labelY, size=16, fill=color, bold=True)
    drawLabel(f"{app.player.energy}/10", labelX, labelY + 15, fill=color, 
              bold=True)
    
# draws the win screen: player wins if they survived a minute
def drawWinScreen(app):
    drawRect(0, 0, app.width, app.height, fill="lightskyblue")
    drawLabel("You won!", app.width/2, app.height/4, size=48, bold=True)

    # stats
    if app.difficulty == 0: difficulty = "Easy"
    elif app.difficulty == 1: difficulty = "Intermediate"
    elif app.difficulty == 2: difficulty = "Hard"
    else: difficulty = "Custom"
    difficultyY = app.width/3
    drawLabel(f"Difficulty: {difficulty}", app.width/2, difficultyY, size=24)

    drawLabel(f"Flowers caught: {app.numFlowersCaught}", app.width/2, 
              difficultyY + 30, size=24)

# draws lose screen: player loses if they hit obstacle or ran out of energy
def drawLoseScreen(app):
    drawRect(0, 0, app.width, app.height, fill="black", opacity = 80)
    drawLabel("GAME OVER", app.width/2, app.height/4, size=60, fill="white")
    
    # cause of death
    death = "None"
    if app.death == 0: death = "Death by Exhaustion"
    elif app.death == 1: death = "Death by Wasp"
    elif app.death == 2: death = "Death by Spider"
    elif app.death == 3: death = "Death by Butterfly Net"
    elif app.death == 4: death = "Death by Going Too Low"
    elif app.death == 5: death = "Death by Going Too High"
    deathY = app.height/4 + 40
    drawLabel(death, app.width/2, deathY, size=24, fill="white")

    # stats
    if app.difficulty == 0: difficulty = "Easy"
    elif app.difficulty == 1: difficulty = "Intermediate"
    elif app.difficulty == 2: difficulty = "Hard"
    else: difficulty = "Custom"
    drawLabel(f"Difficulty: {difficulty}", app.width/2, deathY+60, size=24,
              fill="white")

    drawLabel(f"Flowers caught: {app.numFlowersCaught}", app.width/2, 
              deathY + 90, size=24, fill="white")


def main():
    runApp(width = 800, height = 600)

main()
#if __name__ == '__main__':
    #runApp()
    # cmu_graphics.run()