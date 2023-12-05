from cmu_graphics import *
import math
import copy
import random
import ast
from PIL import Image
# from SetUp import Ship

# Builds User's Board
class Ship:
    # https://discuss.codecademy.com/t/excellent-battleship-game-written-in-python/430605 
    # general structure of the Ship class is inspired from the source above
    #constructor initializes size, orientation, and specific coordinates of ships
    def __init__(self, size):
        self.size = size
        self.orientation = 'Horizontal'
        self.points = [(0,0) for i in range(size)]    
    
    #method is called on mousepress when the player drags the ship to the cell
    def updateLocation(self, app, row, col):
        testPoints = copy.deepcopy(self.points)
        if self.size % 2 == 1:
            midPoint = self.size // 2
            end = midPoint+1
        elif self.size == 4:
            midPoint = 1
            end = midPoint+2
        if self.orientation == 'Horizontal':
            for cell in range(-midPoint, end):
                if 0 <= col + cell < app.cols:
                    testPoints[cell+midPoint] = (row, col+cell)
                else:
                    return self.points
        elif self.orientation == 'Vertical':
            for cell in range(-midPoint, end):
                if 0 <= row + cell < app.rows:
                    testPoints[cell+midPoint] = (row+cell, col)
                else:
                    return self.points
        self.points = testPoints
        return self.points

# helper function for checking if all ships are arranged correctly
def flatten(L):
    if L == []:
        return []
    else:
        first = L[0]
        rest = L[1:]
        if isinstance(first, list):
            return flatten(first + flatten(rest))
        else:
            return [first] + flatten(rest)
def isIntersecting(ship1, board):
    search = set(flatten(board))
    for row, col in ship1:
        if (row, col) in search:
            return True
    return False

# returns the selected ship as a new instance of the Ship class
def getShip(app, mouseX, mouseY):
    if (500 <= mouseX <= 630) and (220 <= mouseY <= 270):
        return ship1
    elif (500 <= mouseX <= 630) and (290 <= mouseY <= 340):
        return ship2
    elif (500 <= mouseX <= 630) and (360 <= mouseY <= 410):
        return ship3

ship1 = Ship(3)
ship2 = Ship(4)
ship3 = Ship(5)

# Builds Opponent Board, based on the source code from below
# https://bigmonty12.github.io/battleship 
def buildShip(dims):
    len_ship = random.randint(3, dims-1)
    orientation = random.randint(0, 1) 
    # Ship is horizontal if orientation is 0 and vertical if orientation is 1
    if orientation == 0:
        # based on the orientation randomly assigns (row, col)
        row_ship = [random.randint(0, dims - 1)] * len_ship
        col = random.randint(0, 4)
        col_ship = list(range(col, col + len_ship))
        coords = tuple(zip(row_ship, col_ship))
    else:
        # Same as above but with opposite orientation
        col_ship = [random.randint(0, dims - 1)] * len_ship
        row = random.randint(0, 4)
        row_ship = list(range(row, row + len_ship))
        coords = tuple(zip(row_ship, col_ship))
    return list(coords)

# generates n opponent ships and cumulate them into a single list
def opponentBoard(n):
    result = []
    for i in range(5):
        result.append(buildShip(n))
    if isLegal(result):
        return result
    else:
        return opponentBoard(n)
#checks the legality of the opponent ship arrangement    
def isLegal(board):
    if len(board) != 5: return False
    for i in range(len(board)):
        for j in range(len(board)):
            if i != j:
                comp1 = set(board[i])
                comp2 = set(board[j])
                if len(comp1 & comp2) >= 1:
                    return False
    return True



#functions Used for Game Plays
def makeMove(app, x, y):
    if app.userTurn:
        return getCell(app, x, y)
    elif app.oppTurn:
        if app.oppLevel == 'standard':
            row = random.randint(0, 7)
            col = random.randint(0, 7)
        elif app.oppLevel == 'intermediate':
            if app.oppGuesses == []:
                row = random.randint(0, 7)
                col = random.randint(0, 7)
            else:
                # guesses are based on cells with high chance of ships being lcoated
                goodRow, goodCol = app.oppGuesses[-1]
                moveOptions = smartTarget(app, goodRow, goodCol)
                if moveOptions != []:
                    row, col = moveOptions.pop()
                else:
                    row = random.randint(0, 7)
                    col = random.randint(0, 7)
                    if (row,col) in app.wrongGuessesOpp or (row,col) in app.oppGuesses:
                        # if the guess was already made, it recursively generates another guess
                        return makeMove(app, x, y)
        elif app.oppLevel == 'advanced':
            if app.oppGuesses == []:
                # in smarterRandom, the guesses are generated randomly for quadrant at a time
                row, col = smarterRandom(app)
            elif (len(app.oppGuesses) > 1 and (app.oppGuesses[-1][0] == app.oppGuesses[-2][0] 
                or app.oppGuesses[-1][1] == app.oppGuesses[-2][1])):
                pastRow, pastCol = app.oppGuesses[-2]
                goodRow, goodCol = app.oppGuesses[-1]
                # compares the two cells that has been hit correctly
                moveOptions = trackSameShip(app, pastRow, pastCol, goodRow, goodCol)
                if moveOptions != []:
                    row, col = moveOptions.pop()
                else:
                    row, col = smarterRandom(app)
                    if (row,col) in app.wrongGuessesOpp or (row,col) in app.oppGuesses:
                        return makeMove(app, x, y)
            else:
                # first tries adjacent cells
                goodRow, goodCol = app.oppGuesses[-1]
                moveOptions = smartTarget(app, goodRow, goodCol)
                if moveOptions != []:
                    row, col = moveOptions.pop()
                else:
                    row, col = smarterRandom(app)
                    if (row,col) in app.wrongGuessesOpp or (row,col) in app.oppGuesses:
                        return makeMove(app, x, y)              
        return (row,col)

# used for advanced guesses; returns coordinates of cells adjacent to 'correct' hits
# https://towardsdatascience.com/coding-an-intelligent-battleship-agent-bf0064a4b319  
def smartTarget(app, guessRow, guessCol):
    targetOptions = []
    potentialTargets = [(guessRow + 1, guessCol), (guessRow, guessCol + 1),
                           (guessRow - 1, guessCol), (guessRow, guessCol - 1)]
    for row, col in potentialTargets:
        # ensures that all potential guesses are within the boundary
        if ((0 <= row <= 7) and (0 <= col <= 7) and (row,col) not in app.wrongGuessesOpp 
            and (row,col) not in app.oppGuesses):
            targetOptions.append((row, col))
    return targetOptions

def trackSameShip(app, row1, col1, row2, col2):
    # based on two correct hits, guesses the orientation of the ship
    if row1 == row2:
        colLeft = min(col1, col2) - 1
        colRight = max(col1, col2) + 1
        result = [(row1, colLeft), (row1, colRight)]
    elif col1 == col2:
        rowUp = min(row1, row2) - 1
        rowDown = max(row1, row2) + 1
        result = [(rowUp, col1), (rowDown, col1)]
    # returns potential points along the same orientation, excluding ones already tried
    editedResult = []
    i = 0
    while i < len(result):
        point = result[i]
        if point not in app.wrongGuessesOpp and point not in app.oppGuesses:
            editedResult.append(point)
        i += 1
    return editedResult

def smarterRandom(app):
    # whenever the opponent needs a new completely random guess, it goes around each quadrant 
    # and returns fairly scattered set of guesses from different quadrant each time
    quadrant = (len(app.wrongGuessesOpp))%4
    if quadrant == 0:
        row = random.randint(0, 3)
        col = random.randint(0,3)  
    elif quadrant == 1:
        row = random.randint(0, 3)
        col = random.randint(4, 7)  
    elif quadrant == 2:
        row = random.randint(4, 7) 
        col = random.randint(0, 3)
    elif quadrant == 3:
        row = random.randint(4, 7) 
        col = random.randint(4, 7)
    return row, col

def isDestroyed(row, col, board):
    for i in range(len(board)):
        ship = board[i]
        if (row, col) in ship:
            return (True, i)
    return (False, 0)
def completelySunk(board):
    if [] in board:
        board.remove([])
    return board
   

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
        # displays message indicating whether the attack was successful
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
    # source for explosion: https://pngfre.com/explosion-png/ 
    app.staticImage = CMUImage(Image.open('Images/explosion.png'))
    # source for splash: 
    # https://www.vectorstock.com/royalty-free-vector/water-splash-animation-dripping-special-vector-39065396 
    app.splash = CMUImage(Image.open('Images/splash.png'))
    # source for gif file of explosion: https://tenor.com/search/explosions-gifs 
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

    # variables needed for the 'set-up' stage
    app.selectedShip = None
    app.setUpMessage = 'Choose Ship'
    app.setUpStage = 'shipSelection'
    app.oppLevel = None
    app.cx = 0
    app.cy = 0
    app.chosenX = 0
    app.chosenY = 0

# https://www.guru99.com/reading-and-writing-files-in-python.html referenced for saving and loading game 
# opens the txt file in writing mode and writes all relevant variables as of current status
def saveGame(app):
    f = open("saveProgress.txt","w+")
    f.write(str(app.board))
    f.write('\n')
    f.write(str(app.opponentBoard))
    f.write('\n')
    f.write(str(app.wrongGuessesUser))
    f.write('\n')
    f.write(str(app.wrongGuessesOpp))
    f.write('\n')
    f.write(str(app.userGuesses))
    f.write('\n')
    f.write(str(app.oppGuesses))
    f.write('\n')
    f.write(str(app.drawingUser))
    f.write('\n')
    f.write(str(app.drawingOpp))
    f.write('\n')
    f.write(str(app.oppLevel))
    # userTurn is saved as 1 and opponentTurn is saved as 0
    if app.userTurn: i = 1
    else: i = 0
    f.write('\n')
    f.write(str(i))
    f.close()

def loadGame(app):
    # opens the txt file in reading mode and assigns all data to relevant variables
    # https://codedamn.com/news/python/how-to-convert-a-string-to-a-list-in-python 
    # referenced to look for other ways to convert a string to a list as list() would not work
    with open("saveProgress.txt","r+") as f:
        fileString = f.read() 
        app.board = ast.literal_eval(fileString.splitlines()[0])
        app.opponentBoard = ast.literal_eval(fileString.splitlines()[1])
        app.wrongGuessesUser = ast.literal_eval(fileString.splitlines()[2])
        app.wrongGuessesOpp = ast.literal_eval(fileString.splitlines()[3])
        app.userGuesses = ast.literal_eval(fileString.splitlines()[4])
        app.oppGuesses = ast.literal_eval(fileString.splitlines()[5])
        app.drawingUser = ast.literal_eval(fileString.splitlines()[6])
        app.drawingOpp = ast.literal_eval(fileString.splitlines()[7])
        app.oppLevel = fileString.splitlines()[8]
        i = fileString.splitlines()[9]
        if i == '1': app.userTurn, app.oppTurn = True, False
        elif i == '0': app.userTurn, app.oppTurn = False, True


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
        # adjusts the position based on the board it is drawing on
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
def onStep(app):
    app.spriteCounter = (app.spriteCounter + 1) % len(app.spriteList)

def drawSplash(app, errors, correct, boardLeft):
    errors = set(errors)
    correct = set(correct)
    for row in range(8):
        for col in range(8):
            if (row, col) in errors and (row, col) not in correct:
                cellLeft, cellTop = getCellLeftTop(app, row, col, boardLeft)
                drawImage(app.splash, cellLeft, cellTop, width = app.cellWidth, height = app.cellHeight)

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
        drawLabel(instructions1, app.width/2, app.height/1.47, fill='white', bold=True, size = 20, font='monospace')
        drawLabel(instructions2, app.width/2, app.height/1.47 + 40, fill='white', bold=True, size = 20, font='monospace')
        drawLabel(instructions3, app.width/2,  app.height/1.47 + 80, fill='white', bold=True, size = 20, font='monospace')
 
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
        
        # button for moving onto the set up screen
        if app.setUpStage == 'complete':
            drawRect(app.width/2, app.height/1.2, 70, 30, fill=None, border='black', align='center')
            drawLabel("Play!", app.width/2, app.height/1.2, bold=True, size=15)
        # Rotate Button
        if app.setUpStage != 'complete' and app.selectedShip != None:
            drawRect(app.width/2, app.height/1.2, 70, 30, fill=None, border='black', align='center')
            drawLabel("Rotate", app.width/2, app.height/1.2, bold=True, size=15)
       
        # draws images of the ship
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

#helper functions needed for board and cell set up 
def getCellLeftTop(app, row, col, boardLeft):
    cellWidth, cellHeight = getCellSize(app)
    cellLeft = boardLeft + col * cellWidth
    cellTop = app.boardTop + row * cellHeight
    return (cellLeft, cellTop)

def getCellSize(app):
    cellWidth = app.boardWidth / app.cols
    cellHeight = app.boardHeight / app.rows
    return (cellWidth, cellHeight)

def getCell(app, x, y):
    dx = x - app.boardLeft1
    dy = y - app.boardTop
    cellWidth, cellHeight = getCellSize(app)
    row = math.floor(dy / cellHeight)
    col = math.floor(dx / cellWidth)
    if (0 <= row < app.rows) and (0 <= col < app.cols):
        return (row, col)
    else:
        return None
    
def lengthIllustrater(n, left, top, width, color):
    for i in range(n):
        drawRect(left + width*i, top, width, 50, fill=None, border=color)

def onMouseDrag(app, mouseX, mouseY):
    if app.setUpStage == 'locationSelection':
        app.cx = mouseX
        app.cy = mouseY

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