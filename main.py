'''
ISSUES:
- smart obstacle generation doesn't work when obstacles move at diff speeds
    - idea: when summoning wasp, check greatest y's for the webs and nets and if the net is after the web, don't summon wasp?

THINGS TO ADD:
- sprites: butterflies(3), wasp, net, web, flowers(2)
- custom difficulty selection
- moving/infinite background -- moves at same speed as webs
- tutorial/autoplay
- win screen confetti animation
'''

from cmu_graphics import *
from player import Player
from obstacle import *
from flower import *
import random
import time

def onAppStart(app):
    restartApp(app)

# initialize app variables
def restartApp(app):
    app.player = Player()
    app.obstacles = []
    app.flowers = []
    app.stepsPerSecond = 30
    app.numFlowersCaught = 0

    app.startTime = None
    app.stopTime = None
    app.timeStopped = 0
    app.timeSurvived = 0
    app.lastSummonedObstacle = app.lastSummonedFlower = time.time()

    app.freqObstacles = 5 # every [num] steps, generate an obstacle
    app.freqFlowers = 5
    app.numObstacles = 7
    app.numFlowers = 4

    app.startMenu = True
    app.gameOver = False
    app.paused = False
    app.won = False
    app.death = 0 # refers to type of death for death screen

    # difficulty selection + coords
    app.difficulty = 0 # 0 = easy, 1 = medium, 2 = hard, 3+ = custom MAKE IT NONE
    app.diffy = 0.3*app.height
    app.easyx = 0.2*app.width
    app.medx = 0.4*app.width
    app.hardx = 0.6*app.width
    app.customx = 0.8*app.width
    app.isHighlighting = None

    # butterfly color selection + coords
    app.playerColor = "magenta" # MAKE IT NONE
    app.flyy = 0.5*app.height
    app.pinkx = 0.25*app.width
    app.orangex = 0.5*app.width
    app.bluex = 0.75*app.width

# check win/lose, summon/remove obstacles and flowers
def onStep(app):
    if app.startTime != None:
         app.startMenu = False
    if not app.paused and not app.startMenu:
        app.player.takeStep()
    if app.gameOver: return

    # making sure timer doesn't keep going when paused/over
    if not app.startMenu:
        if not app.paused and not app.gameOver:
            app.timeSurvived  = time.time() - app.startTime - app.timeStopped
        else:
            app.timeStopped = time.time() - app.stopTime
    
        # player won
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
                    if type(ob) == Wasp: continue
                    while obstacle.inOtherObstacle(ob) or not isSurvivable(app, obstacle):
                        if obstacle.inOtherObstacle(ob):
                            obstacle.x += ob.r
                        elif isinstance(obstacle, Web) and not isSurvivable(app, obstacle):
                            obstacle.r -= 10
                            obstacle.y = obstacle.r
                        elif isinstance(obstacle, Net):
                            obstacle.r -= 10
                            obstacle.y = app.height-obstacle.r
                        else:
                            obstacle = randomObstacle(app, random.randrange(10))
                app.obstacles.append(obstacle)
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

# spacebar to jump, r to reset, p to pause
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
        app.player.draw(app.player.x, app.player.y, app.playerColor, 100)

def onMousePress(app, mousex, mousey):
    wordRadius = 20
    if app.startMenu:
        # difficulty selection
        if distance(mousex, mousey, app.easyx, app.diffy) < wordRadius:
            app.difficulty = 0
        elif distance(mousex, mousey, app.medx, app.diffy) < wordRadius:
            app.difficulty = 1
        elif distance(mousex, mousey, app.hardx, app.diffy) < wordRadius:
            app.difficulty = 2
        elif distance(mousex, mousey, app.customx, app.diffy) < wordRadius:
            app.difficulty = 3
        # player color selection
        if distance(mousex, mousey, app.pinkx, app.flyy) < wordRadius:
            app.playerColor = "magenta"
        elif distance(mousex, mousey, app.orangex, app.flyy) < wordRadius:
            app.playerColor = "orange"
        elif distance(mousex, mousey, app.bluex, app.flyy) < wordRadius:
            app.playerColor = "blue"
        # start button
        if distance(mousex, mousey, app.width/2, 0.9*app.height) < wordRadius:
            app.startTime = time.time()

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
    drawLabel("Start Menu", app.width/2, app.height/10, size = 48, 
              bold = True, font="montserrat")
    
    # difficulty selection
    drawLabel("Click to choose a difficulty level", 
              app.width/2, 0.2*app.height, size = 24)
    if app.difficulty == 0: 
        drawLabel("Easy", app.easyx, app.diffy, size = 20, italic = True, bold=True)
    else: drawLabel("Easy", app.easyx, app.diffy, size = 20, italic = True)
    
    if app.difficulty == 1:
        drawLabel("Medium", app.medx, app.diffy, size=20, italic=True, bold=True)
    else: drawLabel("Medium", app.medx, app.diffy, size=20, italic=True)
    
    if app.difficulty == 2:
        drawLabel("Hard", app.hardx, app.diffy, size=20, italic=True, bold=True)
    else: drawLabel("Hard", app.hardx, app.diffy, size=20, italic=True)
    
    if app.difficulty == 3:
        drawLabel("Custom", app.customx, app.diffy, size=20, italic=True, bold=True)
    else: drawLabel("Custom", app.customx, app.diffy, size=20, italic=True)

    # butterfly color selection
    drawLabel("Click to choose your butterfly", app.width/2, 0.4*app.height, size=24)

    if app.playerColor == "orange":
        app.player.draw(app.orangex, app.flyy, "orange", 100)
    else: app.player.draw(app.orangex, app.flyy, "orange", 60)

    if app.playerColor == "magenta":
        app.player.draw(app.pinkx, app.flyy, "magenta", 100)
    else: app.player.draw(app.pinkx, app.flyy, "magenta", 60)

    if app.playerColor == "blue":
        app.player.draw(app.bluex, app.flyy, "blue", 100)
    else: app.player.draw(app.bluex, app.flyy, "blue", 60)

    # how to play
    drawLabel("Tips", 0.5*app.width, 0.6*app.height, size=24, bold=True)
    drawLabel("Press SPACE to jump, 'r' to restart, and 'p' to pause.", 
              0.2*app.width, 0.65*app.height, size=20, align="left")
    drawLabel("Avoid hitting obstacles like wasps, webs, and butterfly nets.", 
              0.2*app.width, 0.7*app.height, size=20, align="left")
    drawLabel("Make sure to catch flowers to replenish your energy!",
              0.2*app.width, 0.75*app.height, size=20, align="left")
    drawLabel("You must survive for one minute.",
              0.2*app.width, 0.8*app.height, size=20, align="left")
    # start button
    drawLabel("Start", 0.5*app.width, 0.9*app.height, size=24, bold=True)

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
    if app.paused: timeLeft = 60 - int(app.timeSurvived)
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
    
    # restart
    drawLabel("Press 'r' to restart", app.width/2, 0.8*app.height, size = 24, fill="white")

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
    
    # restart
    drawLabel("Press 'r' to restart", app.width/2, 0.8*app.height, size = 24, fill="white")

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