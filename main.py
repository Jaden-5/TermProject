from cmu_graphics import *
import math
import copy
import random
import ast
from PIL import Image
from SetUp import *
from GamePlay import *
from SaveLoad import *


################################################################################
# Variable and image initialization

# initializes necessary image and gif files on app start
def onAppStart(app):
    # loads images from the 'Images' folder
    # source for ship images: https://www.freepik.com/free-photos-vectors/battleship 
    app.ship1H = CMUImage(Image.open('Images/ship1H.png'))
    app.ship1V = CMUImage(Image.open('Images/ship1V.png'))
    app.ship2H = CMUImage(Image.open('Images/ship2H.png'))
    app.ship2V = CMUImage(Image.open('Images/ship2V.png'))
    app.ship3H = CMUImage(Image.open('Images/ship3H.png'))
    app.ship3V = CMUImage(Image.open('Images/ship3V.png'))
    # source for sea surface: https://stock.adobe.com/search?k=ocean+from+above 
    app.seaFloor = CMUImage(Image.open('Images/floor.jpeg'))
    # source for starting screen: 
    # https://arstechnica.com/gaming/2013/11/battlefield-4-the-brutal-broken-beautiful-pinnacle-of-first-person-shooters/
    app.startbg = CMUImage(Image.open('Images/startbg.jpeg'))
    # source for explosion image: https://pngfre.com/explosion-png/ 
    app.staticImage = CMUImage(Image.open('Images/explosion.png'))
    # source for splash: 
    # https://www.vectorstock.com/royalty-free-vector/water-splash-animation-dripping-special-vector-39065396 
    app.splash = CMUImage(Image.open('Images/splash.png'))
    # source for explosion gif file: https://tenor.com/search/explosions-gifs 
    explosionGif = Image.open('Images/explosiongif.gif')
    # setting up gif animations referenced from F23_demos animatedGifs.py
    app.spriteList = []
    for frame in range(explosionGif.n_frames):
        explosionGif.seek(frame)
        fr = explosionGif.resize((explosionGif.size[0]//2, explosionGif.size[1]//2))
        fr = fr.transpose(Image.FLIP_LEFT_RIGHT)
        fr = CMUImage(fr)
        app.spriteList.append(fr)
    app.spriteCounter = 0
    app.stepsPerSecond = 10

    return restart(app)

# initializes all variable needed for game every time game is restarted
def restart(app):
    # variables for starting screen
    app.startScreen = True

    # variables needed for the board
    app.rows = 8
    app.cols = 8
    app.boardLeft1 = app.width/26 
    app.boardTop = app.height/3.5
    app.boardWidth = app.width/2.2
    app.boardHeight = app.height/2.2
    app.cellBorderWidth = 1
    app.cellWidth = app.boardWidth / app.cols
    app.cellHeight = app.boardHeight / app.rows

    # variables needed for the 'set-up' stage
    app.selectedShip = None
    app.setUpMessage = 'Choose Ship'
    app.setUpStage = 'shipSelection'
    app.oppLevel = None
    app.cx = 0
    app.cy = 0
    app.chosenX = 0
    app.chosenY = 0

    # variables needed for playing screen
    app.message = "Let's Destroy!"
    app.userTurn = True
    app.oppTurn = False
    app.userGuesses = []
    app.oppGuesses = []
    app.wrongGuessesUser = []
    app.wrongGuessesOpp = []
    app.setUpScreen = False
    app.playingScreen = False
    app.gameOver = False
    # Parameters for the user's board
    app.boardLeft2 = app.boardLeft1 + app.boardWidth + 20 
    app.boardWidth2 = app.boardWidth
    app.boardHeight2 = app.boardHeight
    app.board = []
    app.drawingUser = []
    #opponent's board
    app.opponentBoard = opponentBoard(5)
    app.drawingOpp = copy.deepcopy(app.opponentBoard)
    app.solution = False
   

################################################################################
# Mouse Mechanism

def onMousePress(app, mouseX, mouseY):
    if app.startScreen:

        # buttons used for selecting the level of difficulty
        if (50 <= mouseX <= 250) and (app.height*14.2/16 <= mouseY <= ((app.height*14.2/16)+50)):
            app.oppLevel = 'standard'
            app.startScreen = not app.startScreen
            app.setUpScreen = not app.setUpScreen
        elif (300 <= mouseX <= 500) and (app.height*14.2/16 <= mouseY <= ((app.height*14.2/16)+50)):
            app.oppLevel = 'intermediate'
            app.startScreen = not app.startScreen
            app.setUpScreen = not app.setUpScreen
        elif (550 <= mouseX <= 750) and (app.height*14.2/16 <= mouseY <= ((app.height*14.2/16)+50)):
            app.oppLevel = 'advanced'
            app.startScreen = not app.startScreen
            app.setUpScreen = not app.setUpScreen

        # loads previously saved game by reading external txt file
        if (31 <= mouseX <= 81) and (app.height/13 <= mouseY <= (app.height/13)+20):
            with open("saveProgress.txt","r+") as f:
                fileString = f.read() 
                if len(fileString) != 0:
                    loadGame(app)
                    app.startScreen = not app.startScreen
                    app.playingScreen = not app.playingScreen


    if app.setUpScreen:

        # first lets the user select one out of ships of different length
        if app.setUpStage == 'shipSelection':
            app.selectedShip = getShip(app, mouseX, mouseY)
            if app.selectedShip and isinstance(app.selectedShip, Ship):
                app.setUpStage = 'locationSelection'
                app.setUpMessage = 'Choose Location'
                app.cx = mouseX
                app.cy = mouseY
        
        # button used for changing the orientation
        if (((app.width/2)-35 <= mouseX < (app.width/2)+35) and ((app.height/1.2)-15 <= mouseY < (app.height/1.2)+15)
             and app.setUpStage != 'complete' and app.selectedShip != None): 
            app.selectedShip.orientation = 'Vertical' if app.selectedShip.orientation == 'Horizontal' else 'Horizontal'

        # button used for switching from set-up to playing screen
        if (((app.width/2)-35 <= mouseX < (app.width/2)+35) and ((app.height/1.2)-15 <= mouseY < (app.height/1.2)+15)
             and app.setUpStage == 'complete'):  
            app.setUpScreen = not app.setUpScreen
            app.playingScreen = not app.playingScreen
                    

    if app.playingScreen:
        
        # saves progress of the current game
        if (31 <= mouseX <= 81) and (app.height/13 <= mouseY <= (app.height/13)+20):
            app.message = "Progress Saved!"
            return saveGame(app)
        
        # checking if the game is over, and stopping if so
        if len(app.board) == 0 or len(app.opponentBoard) == 0:
            app.gameOver = True
            # deletes all saved progress once the game is complete
            with open("saveProgress.txt",'r+') as file:
                file.truncate()

        # receives (row,col) from user and evaluates if the attack was successful
        # removes all 'sunk' points and the whole ship if the list is empty
        if (not app.gameOver and (app.boardLeft1 <= mouseX < app.boardLeft1+app.boardWidth) 
            and (app.boardTop <= mouseY < app.boardTop+app.boardHeight) and app.userTurn):
            row, col = makeMove(app, mouseX, mouseY) 
            if isDestroyed(row, col, app.opponentBoard)[0]: 
                app.userGuesses.append((row,col))
                index = isDestroyed(row, col, app.opponentBoard)[1]
                app.opponentBoard[index].remove((row, col))
                completelySunk(app.opponentBoard)
                app.message = "You hit the opponent's ship!"
                app.userTurn, app.oppTurn = False, True 
                return app.opponentBoard
            elif app.userTurn and not isDestroyed(row, col, app.opponentBoard)[0]:
                app.wrongGuessesUser.append((row,col))
                app.message = "You missed! Opponent's turn."
                app.userTurn = not app.userTurn
                app.oppTurn = not app.oppTurn
                return app.opponentBoard

        # completes same task as above but for AI's guesses
        elif (not app.gameOver and((app.width/2)-67.5 <= mouseX < (app.width/2)+67.5) 
              and (480 <= mouseY < 530) and app.oppTurn):
            row, col = makeMove(app, mouseX, mouseY)
            if isDestroyed(row, col, app.board)[0]: 
                app.oppGuesses.append((row,col))
                index = isDestroyed(row, col, app.board)[1]
                app.board[index].remove((row, col))
                completelySunk(app.board)
                app.message = "Opponent hit your ship!"
                app.userTurn, app.oppTurn = True, False
                return app.opponentBoard
            elif app.oppTurn and not isDestroyed(row, col, app.board)[0]:
                app.wrongGuessesOpp.append((row,col))
                app.message = "Missed! Your turn."
                app.userTurn = not app.userTurn
                app.oppTurn = not app.oppTurn
                return app.opponentBoard if app.userTurn else app.board 


def onMouseRelease(app, mouseX, mouseY):
    if app.setUpStage == 'locationSelection':
        # as the mouse is released, it assumes that point as the 'chosen' cell
        app.chosenX = mouseX
        app.chosenY = mouseY
        if (app.boardLeft1 <= app.chosenX < app.boardLeft1 + app.boardWidth and
            app.boardTop <= app.chosenY < app.boardTop + app.boardHeight):
            (row, col) = getCell(app, app.chosenX, app.chosenY)
            prev = copy.deepcopy(app.selectedShip.points)
            app.selectedShip.updateLocation(app, row, col)
            # if invalid, the points are not updated, so users have to re-choose
            if (app.selectedShip.points == prev or 
            isIntersecting(app.selectedShip.points, app.board)): 
                app.setUpMessage = 'Invalid Position! Try Different Spot'
            else:
                # if valid, appends the ship to the list where all ships are saved
                app.setUpMessage = 'Successful! Continue with Different Ships'    
                app.setUpStage = 'shipSelection'
                app.board.append(app.selectedShip.points)
                app.selectedShip = None
            if len(app.board) == 5: 
                app.setUpMessage = 'Successful! Hit the Play Button to Begin'  
                app.setUpStage = 'complete'
                app.drawingUser = copy.deepcopy(app.board)


def onMouseDrag(app, mouseX, mouseY):
    if app.setUpStage == 'locationSelection':
        app.cx = mouseX
        app.cy = mouseY


################################################################################
# Graphical Components     


def redrawAll(app):
    if app.startScreen:

        # image
        drawRect(0,0,app.width,app.height)
        drawImage(app.startbg, 0,0, width=app.width, height=app.height/1.15)
 
        # heading
        drawRect(app.width/2, app.height/15, app.width/2 + 170, 50, align='center', opacity=70, fill='white')
        drawLabel('King of the Pacific', app.width/2, app.height/15, 
                  font='monospace', align='center', size=50, bold=True, fill='navy')
        
        # instructions
        instructions1 = 'Emergency! 5 enemy ships are approaching the coast!'
        instructions2 = 'Protect your 5 ships with safe arrangement and' 
        instructions3 = 'SINK all opponent ships!'
        drawLabel(instructions1, app.width/2, app.height/1.47, fill='white', bold=True, 
                    size = 20, font='monospace')
        drawLabel(instructions2, app.width/2, app.height/1.47 + 40, fill='white', bold=True, 
                    size = 20, font='monospace')
        drawLabel(instructions3, app.width/2,  app.height/1.47 + 80, fill='white', bold=True, 
                    size = 20, font='monospace')
 
        # buttons
        drawRect(50, app.height*14.2/16, 200, 50, fill='lightGray')
        drawLabel('Standard', 150, app.height*14.8/16, bold=True,size=20, font='monospace')
        drawRect(300, app.height*14.2/16, 200, 50, fill='lightSlateGray')
        drawLabel('Intermediate', 400, app.height*14.8/16, bold=True,size=20, font='monospace')
        drawRect(550, app.height*14.2/16, 200, 50, fill='darkSlateGray')
        drawLabel('Advanced', 650, app.height*14.8/16, bold=True,size=20, font='monospace')

        # button for loading saved game 
        drawRect(31, app.height/13, 50, 20, fill='whiteSmoke', border='black', opacity=50)
        drawLabel('Load', 56, (app.height/13)+10, bold=True, size=20)


    if app.setUpScreen:

        # background image
        drawImage(app.seaFloor, 0, 0, width=app.width, height=app.height)

        # set up board
        drawBoard(app, app.boardLeft1)
        drawBoardBorder(app, app.boardLeft1)

        # ship selection grid
        drawRect(450, app.boardTop, 245, app.boardHeight, fill=None, border='black')
        lengthIllustrater(3, 500, 220, 45, 'deepSkyBlue')
        drawRect(500, 220, 135, 50, fill=None, border='deepSkyBlue')
        drawImage(app.ship1H, 500, 220, width = 130, height = 50)
        lengthIllustrater(4, 480, 290, 45, 'deepSkyBlue')
        drawRect(460, 360, 180, 50, fill=None, border='deepSkyBlue')
        drawImage(app.ship2H, 480, 290, width=170, height=50)
        lengthIllustrater(5, 460, 360, 45, 'deepSkyBlue')
        drawRect(460, 360, 225, 50, fill=None, border='deepSkyBlue')
        drawImage(app.ship3H, 460, 360, width=210, height=50)
        drawSelectedShip(app, app.cx, app.cy)

        # displays relevant messages while arranging the ships
        drawRect(app.width/2, app.height/1.2, 420, 50, border='black', fill='white', opacity=40, align='center')
        drawLabel(app.setUpMessage, app.width/2, app.height/13, bold=True, size=30)
        drawLabel(f'{len(app.board)}/5 ships arranged', app.width/2, 
                  app.height/4.5, bold=True, size=20)
        if app.selectedShip != None:
            drawLabel(f'Orientation: {app.selectedShip.orientation}', app.width/2, 
                      app.height/6, bold=True, size=20)
        elif app.selectedShip == None and app.setUpStage != 'complete':
            drawLabel(f'CLICK and DRAG the ship to place it!', app.width/2, 
                    app.height/1.2, bold=True, size=20, fill='black')
        
        # button for moving onto the play screen
        if app.setUpStage == 'complete':
            drawRect(app.width/2, app.height/1.2, 70, 30, fill=None, border='black', align='center')
            drawLabel("Play!", app.width/2, app.height/1.2, bold=True, size=15)
        # Rotate Button
        if app.setUpStage != 'complete' and app.selectedShip != None:
            drawRect(app.width/2, app.height/1.2, 70, 30, fill=None, border='black', align='center')
            drawLabel("Rotate", app.width/2, app.height/1.2, bold=True, size=15)
       
        # draws images of the ship as they are getting set up
        drawShip(app, app.board, app.boardLeft1)


    if app.playingScreen:

        # draws background image
        drawImage(app.seaFloor, 0, 0, width=app.width, height=app.height)  
        
        # indicates whether both sides' attacks were successful or not
        drawLabel(app.message, app.width/2, app.height/13, bold=True, size=30)

        # indicates the turn for each round
        if app.userTurn:
            name = 'TURN: USER'
        else:
            name = 'TURN: OPPONENT'
        drawLabel(name, app.width/2, app.height/6, bold=True, size=20)
        drawLabel("Opponent", app.width/4, 160, bold=True, size=20)
        drawLabel("Player", 3*app.width/4, 160, bold=True, size=20)

        # indicates how many ships are left
        drawLabel(f'{5-len(app.opponentBoard)}/5 ships sunk!', app.width/2, 
                  app.height/4.5, bold=True, size=20)

        # drawing boards and images of ships
        drawBoard(app, app.boardLeft1)
        drawBoardBorder(app, app.boardLeft1)
        drawBoard(app, app.boardLeft2)
        drawBoardBorder(app, app.boardLeft2)
        drawShip(app, app.drawingUser, app.boardLeft2)
        drawExplosion(app, app.drawingOpp, app.boardLeft1)
        drawExplosion(app, app.drawingUser, app.boardLeft2)
        drawSplash(app, app.wrongGuessesUser, app.userGuesses, app.boardLeft1)
        drawSplash(app, app.wrongGuessesOpp, app.oppGuesses, app.boardLeft2)
        
        # button for next turn
        if app.oppTurn:
            drawRect((app.width/2)-75, 480, 150, 50, fill='whiteSmoke', border='black',opacity=50)
            drawLabel("Opponent's Attack", app.width/2, 505, bold=True, size=15,fill='black')

        # illustrates solution
        if app.solution:
            drawRect(0,0, app.width, app.height, fill='white', opacity=50)
            drawBoard(app, app.boardLeft1)
            drawBoardBorder(app, app.boardLeft1)
            drawShip(app, app.drawingOpp, app.boardLeft1)

        # button for saving 
        drawRect(31, app.height/13, 50, 20, fill='whiteSmoke', border='black', opacity=50)
        drawLabel('Save', 56, (app.height/13)+10, bold=True, size=20)

        # displays the result if the game is over
        if app.gameOver and app.solution != True:
            if len(app.board) == 0:
                drawRect(0, 0, app.width, app.height, fill='red', opacity=30)
                drawRect((app.width/2)-140,(app.height/2)-20, 280, 120, fill='white', opacity=50)
                drawLabel("YOU LOST!", app.width/2, app.height/2, size=50, bold=True)
                drawLabel("Press r to restart!",app.width/2,app.height*9/16,size = 20, bold=True)
                drawLabel("Press s to see solution",app.width/2,app.height*10/16,size = 20, bold=True)
            elif len(app.opponentBoard) == 0:
                drawRect(0, 0, app.width, app.height, fill='green', opacity=30)
                drawRect((app.width/2)-140,(app.height/2)-20, 280, 120, fill='white', opacity=50)
                drawLabel("YOU WIN!", app.width/2, app.height/2, size=50, bold=True)
                drawLabel("Press r to restart!",app.width/2,app.height*9/16,size = 20, bold=True)
                drawLabel("Press s to see solution",app.width/2,app.height*10/16,size = 20, bold=True)


def drawShip(app, board, boardLeft):
    shipPositions = []
    # first figures out given ship's orientation
    for ship in board:
        row, col = ship[0]
        testx, testy = ship[1]
        if row == testx:
            orientation = 'Horizontal' 
        elif col == testy:
            orientation = 'Vertical'
        shipPositions.append((orientation, len(ship), row, col)) 
    
    for orientation, length, shipRow, shipCol in shipPositions:
        # adjusts the reference position based on the board it is drawing on
        if app.playingScreen:
            if boardLeft == app.boardLeft1:
                shipLeft, shipTop = getCellLeftTop(app, shipRow, shipCol, boardLeft)
            elif boardLeft == app.boardLeft2:
                shipLeft, shipTop = getCellLeftTop(app, shipRow, shipCol, boardLeft)
        elif app.setUpScreen: 
            shipLeft, shipTop = getCellLeftTop(app, shipRow, shipCol, app.boardLeft1)

        # draw ship of length 3
        if length == 3 and orientation == 'Horizontal':
            drawImage(app.ship1H, shipLeft, shipTop, width = 3*app.cellWidth, height = app.cellHeight)
        elif length == 3 and orientation == 'Vertical':
            drawImage(app.ship1V, shipLeft, shipTop, width = app.cellWidth, height = 3 * app.cellHeight)
        
        # draw ship of length 4
        elif length == 4 and orientation == 'Horizontal':
            drawImage(app.ship2H, shipLeft, shipTop, width = 4*app.cellWidth, height = app.cellHeight)
        elif length == 4 and orientation == 'Vertical':
            drawImage(app.ship2V, shipLeft, shipTop, width = app.cellWidth, height = 4 * app.cellHeight)
       
        # draw ship of length 5
        elif length == 5 and orientation == 'Horizontal':
            drawImage(app.ship3H, shipLeft, shipTop, width = 5*app.cellWidth, height = app.cellHeight)
        elif length == 5 and orientation == 'Vertical':
            drawImage(app.ship3V, shipLeft, shipTop, width = app.cellWidth, height = 5 * app.cellHeight)


# function called to draw the ship as it is getting dragged to the cell
def drawSelectedShip(app, x, y):
    # draw ship of length 3, ship1
    if app.selectedShip == ship1 and app.selectedShip.orientation == 'Horizontal':
        drawImage(app.ship1H, x, y, width = 3*app.cellWidth, height = app.cellHeight, align='center')
    elif app.selectedShip == ship1 and app.selectedShip.orientation == 'Vertical':
        drawImage(app.ship1V, x, y, width = app.cellWidth, height = 3 * app.cellHeight, align='center')
    
    # draw ship of length 4, ship2
    elif app.selectedShip == ship2 and app.selectedShip.orientation == 'Horizontal':
        drawImage(app.ship2H, x, y, width = 4*app.cellWidth, height = app.cellHeight, align='center')
    elif app.selectedShip == ship2 and app.selectedShip.orientation == 'Vertical':
        drawImage(app.ship2V, x, y, width = app.cellWidth, height = 4 * app.cellHeight, align='center')
    
    # draw ship of length 5, ship3
    elif app.selectedShip == ship3 and app.selectedShip.orientation == 'Horizontal':
        drawImage(app.ship3H, x, y, width = 5*app.cellWidth, height = app.cellHeight, align='center')
    elif app.selectedShip == ship3 and app.selectedShip.orientation == 'Vertical':
        drawImage(app.ship3V, x, y, width = app.cellWidth, height = 5 * app.cellHeight, align='center')


# illustrating special effects 
# utilizing gif animations referenced from F23_demos animatedGifs.py
def drawExplosion(app, board, boardLeft):
    if boardLeft == app.boardLeft1: check=app.userGuesses 
    else: check=app.oppGuesses
    for ship in board:
        for (row, col) in ship:
            if (row, col) in check:
                cellLeft, cellTop = getCellLeftTop(app, row, col, boardLeft)
                drawImage(app.spriteList[app.spriteCounter], cellLeft, cellTop, 
                              width=app.cellWidth, height=app.cellHeight)

def drawSplash(app, errors, correct, boardLeft):
    errors = set(errors)
    correct = set(correct)
    for row in range(8):
        for col in range(8):
            if (row, col) in errors and (row, col) not in correct:
                cellLeft, cellTop = getCellLeftTop(app, row, col, boardLeft)
                drawImage(app.splash, cellLeft, cellTop, width = app.cellWidth, height = app.cellHeight)

def lengthIllustrater(n, left, top, width, color):
    for i in range(n):
        drawRect(left + width*i, top, width, 50, fill=None, border=color)


# illustrating boards for both set-up and playing screen
def drawBoard(app, boardLeft):
    for row in range(app.rows):
        for col in range(app.cols):
            drawCell(app, row, col, boardLeft)
def drawBoardBorder(app, boardLeft):
    drawRect(boardLeft, app.boardTop, app.boardWidth, app.boardHeight,
             fill=None, border='black',
             borderWidth=2*app.cellBorderWidth)

def drawCell(app, row, col, boardLeft):
    cellLeft, cellTop = getCellLeftTop(app, row, col, boardLeft)
    cellWidth, cellHeight = getCellSize(app)

    if app.setUpScreen:
        # board used in the set-up screen
        drawRect(cellLeft, cellTop, cellWidth, cellHeight,
                fill=None, border='black',
                borderWidth=app.cellBorderWidth)

    if app.playingScreen:
        # different colors based on whether the hit was successful
        if (row, col) in app.userGuesses and boardLeft == app.boardLeft1:
            color = 'red'
        elif (row, col) in app.oppGuesses and boardLeft == app.boardLeft2:
            color = 'black'
        else:
            color = None
        drawRect(cellLeft, cellTop, cellWidth, cellHeight,
                fill=color, border='black',
                borderWidth=app.cellBorderWidth)


################################################################################
# Extra functions needed


def onStep(app):
    app.spriteCounter = (app.spriteCounter + 1) % len(app.spriteList)

def onKeyPress(app, key):
    if key == 'r':
        # resets the game
        restart(app)
    elif key == 's':
        # illustrates solution
        app.solution = not app.solution

def main():
    runApp(800, 600)

main()