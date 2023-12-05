from cmu_graphics import *
from player import Player
from obstacle import Obstacle, Wasp, Web, Net
from flower import Flower, BigFlower, SmallFlower
from queue import SimpleQueue
import random, time
from PIL import Image

def onAppStart(app):
    restartApp(app)

# initialize app variables
def restartApp(app):
    #app.obstacles = []
    app.flowers = []
    app.wasps = []
    app.webs = []
    app.nets = []
    app.stepsPerSecond = 30
    app.numFlowersCaught = 0

    app.timeToSurvive = 60
    app.startTime = app.stopTime = None
    app.timeStopped = app.timeSurvived = 0
    app.lastSummonedObstacle = app.lastSummonedFlower = time.time()

    app.freqObstacles = 4 # every [num] steps, generate an obstacle
    app.freqFlowers = 5
    app.numObstacles = 6
    app.numFlowers = 3

    app.startMenu = True
    app.customDiff = app.gameOver = app.paused = app.won = False
    app.death = 0 # refers to type of death for death screen

    # difficulty selection + coords
    app.difficulty = 0 # 0 = easy, 1 = medium, 2 = hard, 3 = custom
    app.diffy = 0.3*app.height
    app.easyx, app.medx = 0.2*app.width, 0.4*app.width
    app.hardx, app.customx = 0.6*app.width, 0.8*app.width

    # butterfly color selection coords
    app.playerColor = "red"
    app.flyy = 0.5*app.height
    app.redx, app.pinkx = (1/6)*app.width, (2/6)*app.width
    app.orangex, app.lightTealx = (3/6)*app.width, (4/6)*app.width
    app.bluex = (5/6)*app.width

    # custom difficulty coords
    app.speedy = 0.25*app.width # wasp, net, web
    app.waspx, app.netx, app.webx = 0.2*app.width, 0.5*app.width, 0.8*app.width
    app.othery = 0.7*app.height
    app.timex, app.energyx = 0.25*app.width, 0.75*app.width
    app.waspSpeed = -5
    app.netSpeed = -4

    # custom difficulty selection/hightlighting
    app.customSelecting = None

    # obstacles
    app.waspImage = CMUImage(Image.open("images/waspNoBG.png"))
    app.webImage = CMUImage(Image.open("images/spiderwebNoBG.png"))
    netImage = Image.open("images/butterflyNet2Cropped.png")
    app.netImage = CMUImage(netImage)
    app.flippedNetImage = CMUImage(netImage.transpose(Image.FLIP_TOP_BOTTOM))

    # flowers
    app.redFlower = CMUImage(Image.open("images/redFlowerNoBG.png"))
    app.pinkFlower = CMUImage(Image.open("images/pinkFlowerNoBG.png"))

    # background
    app.backgroundImage = CMUImage(Image.open("images/DALLEforest1R.jpg"))
    app.bgx1 = 0.5*app.width
    app.bgx2 = 1.5*app.width
    app.bgy = app.height/2

    app.player = Player()
    app.firstPlayerSpeed = app.nextPlayerSpeed = -3
    app.energyLoss = 0.25

# check win/lose, summon/remove obstacles and flowers
def onStep(app):
    if app.startTime != None:
         app.startMenu = False
         app.customDiff = False
    if not app.paused and not app.startMenu and not app.customDiff:
        app.player.takeStep()
    if app.gameOver: return

    if not app.startMenu and not app.customDiff:
        # making sure timer doesn't keep going when paused or game over
        if not app.paused and not app.gameOver:
            app.timeSurvived  = time.time() - app.startTime - app.timeStopped
        else:
            app.timeStopped = time.time() - app.stopTime
    
        # player won
        if app.timeSurvived >= app.timeToSurvive:
            app.won = True
        
        # player speed increase
        if app.timeSurvived > app.timeToSurvive*(2/3):
            app.nextPlayerSpeed = app.firstPlayerSpeed - 2
        elif app.timeSurvived > app.timeToSurvive*(1/3):
            app.nextPlayerSpeed = app.firstPlayerSpeed - 1

        if not app.paused:
            moveBackground(app)
            
            updateObstaclePosition(app) # moves obstacles and deletes
            
            updateFlowerPosition(app) # moves flowers and deletes
        
            summonObstacles(app)
            
            summonFlowers(app)
            
            # if player touched a flower, give player energy
            updateEnergy(app)

        # game over if player has no energy left
        if app.player.energy <= 0:
            app.death = 0
            app.gameOver = True
        
        # game over if player hits an obstacle or touches bottom/top of screen
        playerFell = app.player.y >= app.height
        playerTooHigh = app.player.y < 0
        if (app.player.isColliding(app.wasps) or 
            app.player.isColliding(app.webs) or 
            app.player.isColliding(app.nets) or playerFell or playerTooHigh):
                if playerFell: app.death = 4
                elif playerTooHigh: app.death = 5
                app.gameOver = True

# spacebar to jump, r to reset, p to pause
def onKeyPress(app, key):
    # basic mechancis
    if key == "space" and not app.gameOver and not app.paused:
        app.player.jump()
    if key == "p" and not app.gameOver:
        app.stopTime = time.time()
        app.paused = not app.paused
    if key == "r":
        restartApp(app)
    
    # wasp customizing
    if app.customSelecting == "wasp":
        speedStr = str(abs(app.waspSpeed))
        if key.isdigit():
            speedStr = str(abs(app.waspSpeed)) + key
            if abs(int(speedStr)) <= 15: 
                app.waspSpeed = -1*int(speedStr)
        elif key == "backspace" and len(speedStr) > 1:
            speedStr = speedStr[:len(speedStr)-1]
            app.waspSpeed = abs(int(speedStr))
        elif key == "backspace" and len(speedStr) >= 0:
            app.waspSpeed = 0
    
    # net customizing 
    if app.customSelecting == "net":
        speedStr = str(abs(app.netSpeed))
        if key.isdigit():
            speedStr = str(abs(app.netSpeed)) + key
            if abs(int(speedStr)) <= 15: 
                app.netSpeed = -1*int(speedStr)
        elif key == "backspace" and len(speedStr) > 1:
            speedStr = speedStr[:len(speedStr)-1]
            app.netSpeed = abs(int(speedStr))
        elif key == "backspace" and len(speedStr) >= 0:
            app.netSpeed = 0
    
    # web customizing
    if app.customSelecting == "web":
        speedStr = str(abs(app.firstPlayerSpeed))
        if key.isdigit():
            speedStr = str(abs(app.firstPlayerSpeed)) + key
            if abs(int(speedStr)) <= 15: 
                app.firstPlayerSpeed = -1*int(speedStr)
        elif key == "backspace" and len(speedStr) > 1:
            speedStr = speedStr[:len(speedStr)-1]
            app.firstPlayerSpeed = abs(int(speedStr))
        elif key == "backspace" and len(speedStr) >= 0:
            app.firstPlayerSpeed = 0

def redrawAll(app):
    if app.startMenu:
        drawStartMenu(app)
    elif app.customDiff:
        drawCustomScreen(app)
    elif app.won:
        drawWinScreen(app)
    else:
        drawBackground(app, False)
        for wasp in app.wasps:
            wasp.draw()
        for web in app.webs:
            web.draw()
        for net in app.nets:
            net.draw()
        for flower in app.flowers:
            flower.draw()
        drawEnergyBar(app)
        drawTimerBar(app)
        
        # draw game over screen
        if app.gameOver: drawLoseScreen(app)
        
        # draw pause screen
        if app.paused:
            drawLabel("PAUSED", app.width/2, app.height/2, size=48, bold=True)
        
        # draws player dying
        app.player.draw(app.player.x, app.player.y)

def onMousePress(app, mousex, mousey):
    wordRadius = 20
    if app.startMenu:
        # difficulty selection
        if distance(mousex, mousey, app.easyx, app.diffy) < wordRadius:
            app.difficulty = 0 # easy
        elif distance(mousex, mousey, app.medx, app.diffy) < wordRadius:
            app.difficulty = 1 # medium
        elif distance(mousex, mousey, app.hardx, app.diffy) < wordRadius:
            app.difficulty = 2 # hard
        elif distance(mousex, mousey, app.customx, app.diffy) < wordRadius:
            app.difficulty = 3 # custom difficulty
            app.customDiff = True
            app.startMenu = False
        
        # player color selection
        if distance(mousex, mousey, app.redx, app.flyy) < wordRadius:
            app.playerColor = "red"
        elif distance(mousex, mousey, app.pinkx, app.flyy) < wordRadius:
            app.playerColor = "pink"
        elif distance(mousex, mousey, app.orangex, app.flyy) < wordRadius:
            app.playerColor = "orange"
        elif distance(mousex, mousey, app.lightTealx, app.flyy) < wordRadius:
            app.playerColor = "lightTeal"
        elif distance(mousex, mousey, app.bluex, app.flyy) < wordRadius:
            app.playerColor = "blue"

        # start button
        if distance(mousex, mousey, app.width/2, 0.9*app.height) < wordRadius:
            app.startTime = time.time()
    
    # in custom difficulty menu
    if app.customDiff:
        # back button, takes you back to start menu
        if distance(mousex, mousey, 0.1*app.width, 0.1*app.height) < wordRadius:
            app.startMenu = True
        elif distance(mousex, mousey, app.waspx, app.speedy) < 2*wordRadius:
            app.customSelecting = "wasp"
        elif distance(mousex, mousey, app.netx, app.speedy) < 2*wordRadius:
            app.customSelecting = "net"
        elif distance(mousex, mousey, app.webx, app.speedy) < 2*wordRadius:
            app.customSelecting = "web"
        elif distance(mousex, mousey, app.timex, app.othery) < 4*wordRadius:
            app.customSelecting = "time"
        elif distance(mousex, mousey, app.energyx, app.othery) < 4*wordRadius:
            app.customSelecting = "energy"
        
        # time increment button
        elif (distance(mousex, mousey, app.timex-30, app.othery+100) < 20 and
              app.timeToSurvive < 300):
            app.timeToSurvive += 10
        elif (distance(mousex, mousey, app.timex+30, app.othery+100) < 20 and 
              app.timeToSurvive > 10):
            app.timeToSurvive -= 10
        
        # energy increment button
        elif (distance(mousex, mousey, app.energyx-30, app.othery+100) < 20 and
              app.energyLoss < 10):
            app.energyLoss += 0.25
        elif (distance(mousex, mousey, app.energyx+30, app.othery+100) < 20 and 
              app.energyLoss > 0.25):
            app.energyLoss -= 0.25




# generates an obstacle
def randomObstacle(app, num):
    if num < 2: # 20%
        return Web(app.difficulty)
    elif num > 7: # 30$
        return Net(app.difficulty)
    else: # 50%
        return Wasp(app.difficulty)

# generates a flower
def randomFlower(num):
    if num < 7: # 70%
        return SmallFlower()
    else: # 30%
        return BigFlower()

# checks if the obstacles are passable
def isSurvivable(app, potentialObstacle):
    goodWithNets = goodWithWebs = True
    # for i in range(len(app.obstacles)):
    #     curr = app.obstacles[i]
    #     if isinstance(curr, Wasp): continue
    #     if (potentialObstacle.x - curr.x) > app.width/2: continue
    #     y = abs(curr.y - potentialObstacle.y)
    #     r = curr.r + potentialObstacle.r
    #     if abs(y - r) < 60:
    #         return False
    # return True
    if isinstance(potentialObstacle, Wasp): return True

    for w in range(len(app.webs)):
        curr = app.webs[w]
        if (potentialObstacle.x - curr.x) > app.width/2: continue
        y = abs(curr.y - potentialObstacle.y)
        r = curr.r + potentialObstacle.r
        if abs(y - r) < 60:
            goodWithWebs = False
    
    for n in range(len(app.nets)):
        curr = app.nets[n]
        if (potentialObstacle.x - curr.x) > app.width/2: continue
        y = abs(curr.y - potentialObstacle.y)
        r = curr.r + potentialObstacle.r
        if abs(y - r) < 60:
            goodWithNets = False
    return goodWithWebs and goodWithNets

def drawStartMenu(app):
    drawBackground(app, True)
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

    redGif = Image.open("images/red.gif")
    redPic = CMUImage(redGif.resize((redGif.size[0]//5, redGif.size[1]//5)))
    if app.playerColor == "red":
        drawImage(redPic, app.redx, app.flyy, align="center")
    else: drawImage(redPic, app.redx, app.flyy, align="center", opacity=60)

    pinkGif = Image.open("images/pink.gif")
    pinkPic = CMUImage(pinkGif.resize((pinkGif.size[0]//5, pinkGif.size[1]//5)))
    if app.playerColor == "pink":
        drawImage(pinkPic, app.pinkx, app.flyy, align="center")
    else: drawImage(pinkPic, app.pinkx, app.flyy, align="center", opacity=60)

    orangeGif = Image.open("images/orange.gif")
    orangePic = CMUImage(orangeGif.resize((orangeGif.size[0]//5, orangeGif.size[1]//5)))
    if app.playerColor == "orange":
        drawImage(orangePic, app.orangex, app.flyy, align="center")
    else: drawImage(orangePic, app.orangex, app.flyy, align="center", opacity=60)

    tealGif = Image.open("images/light-teal.gif")
    tealPic = CMUImage(tealGif.resize((tealGif.size[0]//5, tealGif.size[1]//5)))
    if app.playerColor == "lightTeal":
        drawImage(tealPic, app.lightTealx, app.flyy, align="center")
    else: drawImage(tealPic, app.lightTealx, app.flyy, align="center", opacity=60)

    blueGif = Image.open("images/blue.gif")
    bluePic = CMUImage(blueGif.resize((blueGif.size[0]//5, blueGif.size[1]//5)))
    if app.playerColor == "blue":
        drawImage(bluePic, app.bluex, app.flyy, align="center")
    else: drawImage(bluePic, app.bluex, app.flyy, align="center", opacity=60)

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

# draws the menu for custom difficulty
def drawCustomScreen(app):
    drawBackground(app, True)
    # title
    drawLabel("Custom Difficulty", app.width/2, 0.1*app.height, size=48, 
              bold=True)
    drawLabel("Speeds: Click a heading and type", app.width/2, 0.2*app.height, 
              size=24, bold=True)
    drawLabel("The max speed is 15.", app.width/2, 0.2*app.height+30, size=24, 
              bold=True)
    drawLabel("Click a heading and increment with the buttons", app.width/2, 
              0.6*app.height, size=24, bold=True)
    
    # wasp start speed
    if app.customSelecting == "wasp": # bolding if selected
        drawLabel(f"Wasp speed: {abs(app.waspSpeed)}", app.waspx, app.speedy, 
              size=24, bold=True)
    else: 
        drawLabel(f"Wasp speed: {abs(app.waspSpeed)}", app.waspx, app.speedy, 
              size=24)
    drawLabel("Easy: 5", app.waspx-50, app.speedy+25, size=18, align="left")
    drawLabel("Medium: 6", app.waspx-50, app.speedy+50, size=18, align="left")
    drawLabel("Hard: 7", app.waspx-50, app.speedy+75, size=18, align="left")

    # net start speed
    if app.customSelecting == "net": # bolding if selected
        drawLabel(f"Net speed: {abs(app.netSpeed)}", app.netx, app.speedy, 
                  size=24, bold=True)
    else: 
        drawLabel(f"Net speed: {abs(app.netSpeed)}", app.netx, app.speedy, 
                  size=24)
    drawLabel("Easy: 4", app.netx-50, app.speedy+25, size=18, align="left")
    drawLabel("Medium: 5", app.netx-50, app.speedy+50, size=18, align="left")
    drawLabel("Hard: 6", app.netx-50, app.speedy+75,size=18, align="left")

    # web start speed
    if app.customSelecting == "web":
        drawLabel(f"Web speed: {abs(app.firstPlayerSpeed)}", app.webx, 
                app.speedy, size=24, bold=True)
    else:
        drawLabel(f"Web speed: {abs(app.firstPlayerSpeed)}", app.webx, 
                app.speedy, size=24)
    drawLabel("Easy: 3", app.webx-50, app.speedy+25, size=18, align="left")
    drawLabel("Medium: 4", app.webx-50, app.speedy+50, size=18, align="left")
    drawLabel("Hard: 5", app.webx-50, app.speedy+75, size=18, align="left")
    
    # time
    minutes = app.timeToSurvive // 60
    seconds = app.timeToSurvive % 60
    if app.customSelecting == "time":
        drawLabel(f"Survival time (min:sec): {minutes}:{seconds}", app.timex, 
              app.othery, size=24, bold=True)
    else:
        drawLabel(f"Survival time (min:sec): {minutes}:{seconds}", app.timex, 
              app.othery, size=24)
    drawLabel("Normal: 1:00", app.timex-50, app.othery+25, size=18, 
              align="left")
    drawLabel("The max is 5 minutes.", app.timex, app.othery+50, size=18)
    # +/- 10 seconds buttons
    buttonRadius = 25
    drawCircle(app.timex-30, app.othery + 100, buttonRadius, fill="palegreen", 
               border="black")
    drawLabel("+10", app.timex-30, app.othery+100, size=16)
    drawCircle(app.timex+30, app.othery + 100, buttonRadius, fill="tomato", 
               border = "black")
    drawLabel("-10", app.timex+30, app.othery+100, size=16)
    
    # energy loss per jump
    if app.customSelecting == "energy":
        drawLabel(f"Energy loss per jump: {app.energyLoss}", app.energyx, 
              app.othery, size=24, bold=True)
    else:
        drawLabel(f"Energy loss per jump: {app.energyLoss}", app.energyx, 
              app.othery, size=24)
    drawLabel("Normal: 0.25", app.energyx-50, app.othery+25, size=18, 
              align="left")
    drawLabel("The max is 10, out of 10 energy points.", app.energyx, app.othery+50, size=18)
    drawCircle(app.energyx-30, app.othery+100, buttonRadius, fill="palegreen", 
               border="black")
    drawLabel("+0.25", app.energyx-30, app.othery+100, size=16)
    drawCircle(app.energyx+30, app.othery+100, buttonRadius, fill="tomato", 
               border="black")
    drawLabel("-0.25", app.energyx+30, app.othery+100, size=16)
    

    # go back button
    drawLabel("< Back", 0.1*app.width, 0.1*app.height, size=20, bold=True)

# draws and updates player's energy bar
def drawEnergyBar(app):
    energyRatio = app.player.energy/10
    color = None
    if app.player.energy < 3:
        color = "red"
    elif app.player.energy < 6:
        color = "yellow"
    else:
        color = "lime"
    barTopX = 20
    barTopY = 10
    barWidth = 20
    fullBarHeight = app.height/2-50

    # draw opaque sidebar
    drawRect(0, 0, barWidth+40, app.height, fill="white", opacity=30)
    
    # draw used energy
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
    timeRatio = app.timeSurvived / app.timeToSurvive
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
    timeLeft = app.timeToSurvive - int(app.timeSurvived)
    minLeft = timeLeft // 60
    secLeft = timeLeft % 60
    if app.paused: timeLeft = 60 - int(app.timeSurvived)
    labelX = barTopX + barWidth/2
    labelY = 20 + fullBarHeight + app.height/2
    drawLabel("Time", labelX, labelY, size=16, fill=color, bold=True)
    drawLabel(f"{minLeft}:{secLeft}", labelX, labelY + 15, fill=color, bold=True)
    
# draws the win screen: player wins if they survived a minute
def drawWinScreen(app):
    drawBackground(app, True)
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
    drawLabel(f"You survived for {int(app.timeToSurvive)} seconds.", 
              app.width/2, difficultyY+90, size=24)
    
    # restart
    drawLabel("Press 'r' to restart", app.width/2, 0.8*app.height, size = 24)

# draws lose screen: player loses if they hit obstacle or ran out of energy
def drawLoseScreen(app):
    drawRect(0, 0, app.width, app.height, fill="black", opacity = 80)
    drawLabel("GAME OVER", app.width/2, app.height/4, size=60, fill="white")
    
    # cause of death
    death = "None"
    if app.death == 0: death = "Death by Exhaustion"
    elif app.death == 1: death = "Death by Wasp"
    elif app.death == 2: death = "Death by Spider Web"
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
    drawLabel(f"You survived for {int(app.timeSurvived)} seconds.", app.width/2,
               deathY+120, size=24, fill="white")
    
    # restart
    drawLabel("Press 'r' to restart", app.width/2, 0.8*app.height, size = 24,
               fill="white")

# draws infinite background
def drawBackground(app, needsOpacity):
    drawImage(app.backgroundImage, app.bgx1, app.bgy, align="center")
    drawImage(app.backgroundImage, app.bgx2, app.bgy, align="center")
    #drawImage(app.backgroundImage, app.width/2, app.height/2, align="center")
    # opaque rectangle that lets you see text
    if needsOpacity: 
        drawRect(0, 0, app.width, app.height, fill="white", opacity=50)

# classic distance function
def distance(x0, y0, x1, y1):
    x = x0 - x1
    y = y0 - y1
    return (x**2 + y**2)**0.5




# ON STEP FUNCTIONS BELOW

# move the background
def moveBackground(app):
    app.bgx1 += app.nextPlayerSpeed
    app.bgx2 += app.nextPlayerSpeed
    if app.bgx1 <= -0.5*app.width:
        app.bgx1 = app.bgx2 + app.width
    elif app.bgx2 <= -0.5*app.width:
        app.bgx2 = app.bgx1 + app.width

def updateObstaclePosition(app):
    # obIndex = 0
    # while obIndex < len(app.obstacles):
    #     obstacle = app.obstacles[obIndex]
    #     obstacle.takeStep()
    #     if obstacle.obstaclePassed():
    #         app.obstacles.pop(obIndex) # delete obstacle when passed
    #     else:
    #         obIndex += 1
    for wasp in app.wasps:
        wasp.takeStep()
    for web in app.webs:
        web.takeStep()
    for net in app.nets:
        net.takeStep()

    if len(app.wasps) > 0:
        if app.wasps[0].x < -app.wasps[0].r:
            app.wasps.pop(0)
    if len(app.webs) > 0:
        if app.webs[0].x < -app.webs[0].r:
            app.webs.pop(0)
    if len(app.nets) > 0:
        if app.nets[0].x < -app.nets[0].r:
            app.nets.pop(0)

# remove flowers once they're passed
def updateFlowerPosition(app):
    # flowerIndex = 0
    # while flowerIndex < len(app.flowers):
    #     flower = app.flowers[flowerIndex]
    #     flower.takeStep()
    #     if flower.flowerPassed():
    #         app.flowers.pop(flowerIndex) # delete flower when passed
    #     else:
    #         flowerIndex += 1
    for flower in app.flowers:
        flower.takeStep()
    if len(app.flowers) > 0:
        if app.flowers[0].x < 0:
            app.flowers.pop(0)

# summoning obstacles survivably
def summonObstacles(app):
    numSummoning = random.randrange(1, app.numObstacles) # num of obstacles
    enoughTimePassed = (time.time() - app.lastSummonedObstacle) > 1
    totalLength = len(app.wasps) + len(app.webs) + len(app.nets)
    if enoughTimePassed and (totalLength < numSummoning):
        obstacle = randomObstacle(app, random.randrange(10))
        # makes sure obstacles aren't conjoined and are survivable
        # for ob in app.obstacles:
        #     if type(ob) == Wasp: continue
        #     while (obstacle.inOtherObstacle(ob) or 
        #             not isSurvivable(app, obstacle)):
        #         if obstacle.inOtherObstacle(ob):
        #             obstacle.x += ob.r # if conjoined, move it right a little
        #         elif (isinstance(obstacle, Web) and 
        #                 not isSurvivable(app, obstacle)):
        #             obstacle.r -= 10
        #             obstacle.y = obstacle.r
        #         elif isinstance(obstacle, Net):
        #                 obstacle.r -= 10
        #                 obstacle.y = app.height-obstacle.r
        #         else:
        #             obstacle = randomObstacle(app, random.randrange(10))
        for web in app.webs:
            while (obstacle.inOtherObstacle(web) or 
                   not isSurvivable(app, obstacle)):
                if obstacle.inOtherObstacle(web):
                    obstacle.x += web.r
                elif not isSurvivable(app, obstacle):
                    obstacle.r -= 10
                    if obstacle.y < 0.5*app.height:
                        obstacle.y = obstacle.r
                    else: 
                        obstacle.y = app.height - obstacle.r
                    obstacle.y = obstacle.r
        
        for net in app.nets:
            while (obstacle.inOtherObstacle(net) or 
                   not isSurvivable(app, obstacle)):
                if obstacle.inOtherObstacle(net):
                    obstacle.x += net.r
                elif not isSurvivable(app, obstacle):
                    obstacle.r -= 10
                    if obstacle.y < 0.5*app.height: obstacle.y = obstacle.r
                    else: obstacle.y = app.height - obstacle.r
                    #obstacle.y = obstacle.r
        #app.obstacles.append(obstacle)
        if isinstance(obstacle, Wasp): 
            app.wasps.append(obstacle)
        elif isinstance(obstacle, Web): 
            app.webs.append(obstacle)
        else: 
            app.nets.append(obstacle)
        app.lastSummonedObstacle = time.time()

# summon flowers
def summonFlowers(app):
    numFlowersSummoning = random.randrange(0, app.numFlowers)
    flowerTime = (time.time() - app.lastSummonedFlower) > 2
    if flowerTime and (len(app.flowers) < numFlowersSummoning):
        flower = randomFlower(random.randrange(10))
        app.flowers.append(flower)
        app.lastSummonedFlower = time.time()

# if a player got a flower, give them energy
def updateEnergy(app):
    # i = 0 
    # while i < len(app.flowers):
    #     if app.player.gotFlower(app.flowers[i]):
    #         app.player.addEnergy(app.flowers[i])
    #         app.flowers.pop(i)
    #     else:
    #         i += 1 
    if len(app.flowers) > 0:
        if app.player.gotFlower(app.flowers[0]):
            app.player.addEnergy(app.flowers[0])
            app.flowers.pop(0)


def main():
    runApp(width = 800, height = 600)

main()