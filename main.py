'''
ISSUES:
- player jump height unknown, isSurvivable ???
    - add isSurvivable condition when generating obstacles
    - if jump height too big, obstacles are conjoined
- timer doesn't stop when paused, only appears so
- smart obstacle generation doesn't work when obstacles move at diff speeds
    - idea: when summoning nets, check lowest y of all obstacles, and summon one
    that has top y value at least 40 greater than that

THINGS TO ADD:
- working difficulty selection
- sprites: butterflies(3), wasp, net, web, flowers(2)
- moving/infinite background -- moves at same speed as webs
- tutorial/autoplay
- timer bar
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
    app.lastSummonedObstacle = app.lastSummonedFlower = time.time()
    app.numFlowersCaught = 0

    app.startTime = time.time()
    app.stopTime = None
    app.timeStopped = 0
    app.timeSurvived = 0
    app.stoppedTime = False

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

    # stopping the timer bar if player died or paused
    # if app.gameOver or app.paused and not app.stoppedTime:
    #     app.stopTime = time.time()
    #     app.stoppedTime = True
    # else:
    #     #app.stopTime = time.time()
    #     app.stoppedTime = False

    # player won
    if not app.paused and not app.gameOver:
        app.timeSurvived  = time.time() - app.startTime - app.timeStopped
    else:
        app.timeStopped = time.time() - app.stopTime

    if app.timeSurvived >= 60:
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
                # if type(obstacle) == type(ob): # same obstacle
                if type(ob) == Wasp: continue
                while obstacle.inOtherObstacle(ob) or not isSurvivable(app, obstacle):
                    # if isinstance(obstacle, Wasp):
                    #     if obstacle.y > ob.y: # below a prior obstacle
                    #         obstacle.y += ob.y
                    #     else:
                    #         obstacle.y -= ob.y
                    # print("in other obstacle: ", obstacle.inOtherObstacle(ob))
                    # print("isSurvivable: ", isSurvivable(app, obstacle))
                    if obstacle.inOtherObstacle(ob):
                        #print("in other obstacle")
                        obstacle.x += ob.r
                    elif isinstance(obstacle, Web) and not isSurvivable(app, obstacle):
                        # print("is web")
                        # print("distance between centers: ", distance(ob.x, ob.y, obstacle.x, obstacle.y))
                        # print(f"ob radius: {ob.r} \t ob.x = {ob.x}")
                        # print(f"web radius: {obstacle.r} \t web x = {obstacle.x}")
                        obstacle.r -= 10
                        #obstacle.x += ob.r
                        obstacle.y = obstacle.r
                    elif isinstance(obstacle, Net):
                        # print("is net")
                        obstacle.r -= 10
                        obstacle.y = app.height-obstacle.r
                    else:
                        # print("something else") 
                        obstacle = randomObstacle(app, random.randrange(10))
                # else:
                #     if not isSurvivable(app, obstacle):
                #         pass
            # makes sure the player can fit between the obstacles
            # if isinstance(obstacle, Net):
            #     maxY = getGreatestY(app)
            #     if (obstacle.y - maxY.y) < (maxY.r + obstacle.r + 40):
            #         obstacle.r -= 40
            #         obstacle.y = app.height - obstacle.r
            # if isinstance(obstacle, Wasp):
            #     pass
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
        app.stopTime = time.time()
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
        drawTimerBar(app)
        
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
    for i in range(len(app.obstacles)):
        curr = app.obstacles[i]
        #withinSameishX = [curr]

        # makes a list of obstacles within sameish x
        # sameish x means within curr's x +/- combinedRadii of curr and other
        # for j in range(i+1, len(potentialObList)):
        #     other = potentialObList[j]
        #     combinedRadii = curr.r + other.r
        #     if (other.x < curr.x + combinedRadii):
        #         withinSameishX.append(other)

        # # now checking if there's at least one gap between sameishX obstacles
        # # that the player's jump can fit through
        # for k in range(len(withinSameishX)):
        #     if k < len(withinSameishX)-1:
        #         first = withinSameishX[i]
        #         next = withinSameishX[k+1]
        #         y = abs(first.y - next.y)
        #         r = first.r + next.r
        #         if y - r > 40: # REPLACE WITH JUMP HEIGHT !!!!!!!
        #             return True
        # for l in range(len(potentialObList)):
        #     check = potentialObList[l]
        #     y = abs(curr.y - check.y)
        #     r = curr.r + check.r
        #     if y - r > 80:
        #         return True
        if isinstance(curr, Wasp): continue
        if potentialObstacle.x - curr.x > app.width/2: continue
        y = abs(curr.y - potentialObstacle.y)
        r = curr.r + potentialObstacle.r
        if abs(y - r) < 60:
            return False
    return True

# from list of obstacles, returns the obstacle with greatest y value 
def getGreatestY(app):
    maxY = 0
    if app.obstacles != []: 
        maxObstacle = app.obstacles[0]
        for obstacle in app.obstacles:
            if obstacle.y > maxY:
                maxY = obstacle.y
                maxObstacle = obstacle
        return maxObstacle

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
    fullBarHeight = app.height/2-50
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

# draws and updates the player's time bar (shows how much time they have left)
def drawTimerBar(app):
    timeRatio = app.timeSurvived / 60
    color = "blue"
    fullBarHeight = app.height/2 - 50
    barTopX = 20
    barTopY = app.height/2
    barWidth = 20

    # draw total time of 60 seconds to fill up
    drawRect(barTopX, barTopY, barWidth, fullBarHeight, fill=None, border=color)

    # draw time that's left
    topY = app.height/2 + (1-timeRatio)*fullBarHeight
    if timeRatio > 0: 
        drawRect(barTopX, topY, barWidth, timeRatio*fullBarHeight, fill=color, 
                 border=color)
    
    # draw labels
    timeLeft = 60 - int(app.timeSurvived)
    if app.gameOver or app.paused: 
        timeLeft = 60 - int(app.stopTime - app.startTime)
    labelX = barTopX + barWidth/2
    labelY = 20 + fullBarHeight + app.height/2
    drawLabel("Time", labelX, labelY, size=16, fill=color, bold=True)
    drawLabel(f"{timeLeft}", labelX, labelY + 15, fill=color, bold=True)
    


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

# classic distance function
def distance(x0, y0, x1, y1):
    x = x0 - x1
    y = y0 - y1
    return (x**2 + y**2)**0.5

def main():
    runApp(width = 800, height = 600)

main()
#if __name__ == '__main__':
    #runApp()
    # cmu_graphics.run()