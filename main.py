from cmu_graphics import *
import math
import copy
import random
from PIL import Image

# Builds User's Board
class Ship:
    #constructor initializes size, orientation, and specific coordinates of ships
    def __init__(self, size):
        self.size = size
        self.orientation = 'Horizontal'
        self.points = [(0,0) for i in range(size)]    
    
    #method is called on mousepress when the player selects the cell to locate
    def updateLocation(self, row, col):
        testPoints = copy.copy(self.points)
        testPoints[0] = (row,col)
        if self.orientation == 'Horizontal':
            for i in range(len(testPoints)):
                testPoints[i] = (row, col+i)
                if not pointsLegal(row, col+i):
                    return self.points
        elif self.orientation == 'Vertical':
            for i in range(len(testPoints)):
                testPoints[i] = (row+i, col)
                if not pointsLegal(row+i, col):
                    return False          
        self.points = testPoints
        return self.points

# helper function that checks if the ship is arranged correctly
def pointsLegal(row, col):
    if row>=8 or row<0 or col<0 or col>=8:
        return False
    return True

def isIntersecting(ship1, board):
    pass
    # for row, col in ship1:
    #     for ship in board:
    #         if (row, col) in ship:
    #             return True
    # return False

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

# Builds Opponent Board
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


#Functions Used for Game Plays
def makeMove(app, x, y):
    if app.userTurn:
        return getCell(app, x, y)
    elif app.oppTurn:
        if app.oppLevel == 'standard':
            row = random.randint(0, 7)
            col = random.randint(0, 7)
        elif app.oppLevel == 'advanced':
            if app.oppGuesses == []:
                row = random.randint(0, 7)
                col = random.randint(0, 7)
            else:
                goodRow, goodCol = app.oppGuesses[-1]
                moveOptions = smartTarget(app, goodRow, goodCol)
                if moveOptions != []:
                    row, col = moveOptions.pop()
                else:
                    row = random.randint(0, 7)
                    col = random.randint(0, 7)
        return (row,col)
    
def smartTarget(app, guessRow, guessCol):
    targetOptions = []
    potentialTargets = [(guessRow + 1, guessCol), (guessRow, guessCol + 1),
                           (guessRow - 1, guessCol), (guessRow, guessCol - 1)]
    for row, col in potentialTargets:
        if ((0 <= row <= 7) and (0 <= col <= 7) and (row,col) not in app.wrongGuessesOpp 
            and (row,col) not in app.oppGuesses):
            targetOptions.append((row, col))
    return targetOptions

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
        
        if ((((app.width/3)-100) <= mouseX <= ((app.width/3)+100)) 
            and (((app.height*15/16)-25) <= mouseY <= ((app.height*15/16)+25))):
            app.oppLevel = 'standard'
            app.startScreen = not app.startScreen
            app.setUpScreen = not app.setUpScreen
        elif ((((2*app.width/3)-100) <= mouseX <= ((2*app.width/3)+100)) 
              and (((app.height*15/16)-25) <= mouseY <= ((app.height*15/16)+25))):
            app.oppLevel = 'advanced'
            app.startScreen = not app.startScreen
            app.setUpScreen = not app.setUpScreen


    #mouse presses used for set up screen
    if app.setUpScreen:
        
        # first lets the user select one out of ships of different length
        if app.setUpStage == 'shipSelection':
            app.selectedShip = getShip(app, mouseX, mouseY)
            if app.selectedShip and isinstance(app.selectedShip, Ship):
                app.setUpStage = 'locationSelection'
                app.setUpMessage = 'Choose Location'
        # then moves onto selecting the location for the given ship
        elif app.setUpStage == 'locationSelection':
            if (app.boardLeft1 <= mouseX < app.boardLeft1 + app.boardWidth and
                app.boardTop <= mouseY < app.boardTop + app.boardHeight):
                (row, col) = getCell(app, mouseX, mouseY)
                prev = app.selectedShip.points
                app.selectedShip.updateLocation(row, col)
                # if invalid, the points are not updated, so users have to re-choose
                if app.selectedShip.points == prev and len(app.board) == 1: 
                    app.setUpMessage = 'Invalid Position! Try Different Spot'
                    app.setUpStage = 'locationSelection'
                else:
                    # if valid, appends the ship to the list where all ships are saved
                    app.setUpMessage = 'Successful! Continue with Different Ships'    
                    app.setUpStage = 'shipSelection'
                    app.board.append(app.selectedShip.points)
                if len(app.board) == 5: 
                    app.setUpStage = 'complete'
                    app.drawingUser = copy.deepcopy(app.board)
        
        # button used for changing the orientation
        if (500 <= mouseX < 570) and (480 <= mouseY < 550) and app.setUpStage != 'complete': 
            app.selectedShip.orientation = 'Vertical' if app.selectedShip.orientation == 'Horizontal' else 'Horizontal'

        # button used for switching from set-up to playing screen
        if (600 <= mouseX < 735) and (480 <= mouseY < 530): 
            app.setUpScreen = not app.setUpScreen
            app.playingScreen = not app.playingScreen
                    

    if app.playingScreen:
        # checking if the game is over, and stopping if so
        if len(app.board) == 0 or len(app.opponentBoard) == 0:
            app.gameOver = True

        # receives (row,col) from user and evaluates if the attack was successful
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

        # completes same task as above but for AI's guessed (row,col) 
        elif (not app.gameOver and(600 <= mouseX < 735) and (480 <= mouseY < 530) 
            and app.oppTurn):
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

def onAppStart(app):
    app.ship1H = CMUImage(Image.open('Images/ship1H.png'))
    app.ship1V = CMUImage(Image.open('Images/ship1V.png'))
    app.ship2H = CMUImage(Image.open('Images/ship2H.png'))
    app.ship2V = CMUImage(Image.open('Images/ship2V.png'))
    app.ship3H = CMUImage(Image.open('Images/ship3H.png'))
    app.ship3V = CMUImage(Image.open('Images/ship3V.png'))
    app.seaFloor = CMUImage(Image.open('Images/floor.jpeg'))
    app.startbg = CMUImage(Image.open('Images/startbg.jpeg'))
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


def drawShip(app, board, boardLeft):
    shipPositions = []
    for ship in board:
        row, col = ship[0]
        testx, testy = ship[1]
        if row == testx:
            orientation = 'Horizontal' 
        elif col == testy:
            orientation = 'Vertical'
        shipPositions.append((orientation, len(ship), row, col)) 
    
    for orientation, length, shipRow, shipCol in shipPositions:
        # adjusts the position ships are drawn based on the selection of each side
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
        elif length == 3 and app.selectedShip.orientation == 'Vertical':
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
            drawImage(app.ship3V, shipLeft, shipTop, width = app.cellWidth, height = 4 * app.cellHeight)


def redrawAll(app):
    if app.startScreen:
        drawRect(0,0,app.width,app.height)
        # image
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
        drawRect(app.width/3, app.height*15/16, 200, 50, fill='lightGray',align = 'center')
        drawLabel('Standard', app.width/3, app.height*15/16, bold=True,size=20, font='monospace')
        drawRect(2*app.width/3, app.height*15/16, 200, 50, fill='lightSlateGray',align = 'center')
        drawLabel('Advanced', 2*app.width/3, app.height*15/16, bold=True,size=20, font='monospace')


    if app.setUpScreen:
        drawImage(app.seaFloor, 0, 0, width=app.width, height=app.height)    
        # set up board
        drawBoard(app, app.boardLeft1)
        drawBoardBorder(app, app.boardLeft1)

        # ship selection grid
        drawRect(500, 220, 130, 50, fill=None, border='cyan')
        drawImage(app.ship1H, 500, 220, width = 130, height = 50)
        drawRect(480, 290, 170, 50, fill=None, border='cyan')
        drawImage(app.ship2H, 480, 290, width=170, height=50)
        drawRect(460, 360, 210, 50, fill=None, border='cyan')
        drawImage(app.ship3H, 460, 360, width=210, height=50)

        # displays the message while arranging the ships
        drawLabel(app.setUpMessage, app.width/2, app.height/13, bold=True, size=30)
        drawLabel(f'{len(app.board)}/5 ships arranged', app.width/2, 
                  app.height/4.5, bold=True, size=20)
        if app.selectedShip != None:
            drawLabel(f'Orientation: {app.selectedShip.orientation}', app.width/2, 
                      app.height/6, bold=True, size=20)
        elif app.selectedShip == None:
            drawLabel(f'Click the ship and select the cell to place it!', app.width/2, 
                    app.height/1.2, bold=True, size=20)

        # when pressed, moves onto the set up screen
        if app.setUpStage == 'complete':
            drawRect(600, 480, 135, 50, fill=None, border='black')
            drawLabel("Let's Play!", 665, 505, bold=True, size=15)

        # Rotate Button
        if app.setUpStage != 'complete' and app.selectedShip != None:
            drawLabel("Rotate", 535, 515, bold=True, size=15)
            drawRect(500, 480, 70, 70, fill=None, border='black')
        
        drawShip(app, app.board, app.boardLeft1)


    if app.playingScreen:
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
        
        # button for next turn
        drawRect(600, 480, 135, 50, fill=None, border='white')
        drawLabel("Opponent's Attack", 665, 505, bold=True, size=15,fill='white')

        # illustrates solution
        if app.solution:
            drawRect(0,0, app.width, app.height, fill='white', opacity=50)
            drawBoard(app, app.boardLeft1)
            drawBoardBorder(app, app.boardLeft1)
            drawShip(app, app.drawingOpp, app.boardLeft1)

        # displays the result if the game is over
        if app.gameOver:
            if len(app.board) == 0:
                drawRect(0, 0, app.width, app.height, fill='red', opacity=30)
                drawRect(app.width/2,app.height/2, 280, 50, fill='white', opacity=50, align='center')
                drawLabel("YOU LOST!", app.width/2, app.height/2, size=50, bold=True)
                drawLabel("Press r to restart!",app.width/2,app.height*14.5/16,size = 30, font='monospace')
            elif len(app.opponentBoard) == 0:
                drawRect(0, 0, app.width, app.height, fill='green', opacity=30)
                drawRect(app.width/2,app.height/2, 280, 50, fill='white', opacity=50, align='center')
                drawLabel("YOU WIN!", app.width/2, app.height/2, size=50, bold=True, font='monospace')
                drawLabel("Press r to restart!",app.width/2,app.height*14.5/16,size = 30, font='monospace')

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
        # illustrating ships in the set-up screen
        drawRect(cellLeft, cellTop, cellWidth, cellHeight,
                fill=None, border='black',
                borderWidth=app.cellBorderWidth)

    if app.playingScreen:
        # different colors based on whether the hit was successful
        if (row, col) in app.userGuesses and boardLeft == app.boardLeft1:
            color = 'red'
        elif (row, col) in app.wrongGuessesUser and boardLeft == app.boardLeft1:
            color = 'grey'
        elif (row, col) in app.oppGuesses and boardLeft == app.boardLeft2:
            color = 'black'
        elif (row, col) in app.wrongGuessesOpp and boardLeft == app.boardLeft2:
            color = 'grey'
        else:
            color = None
        drawRect(cellLeft, cellTop, cellWidth, cellHeight,
                fill=color, border='black',
                borderWidth=app.cellBorderWidth)

#helper functions needed for board set up and basic game play  
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
    
def onKeyPress(app, key):
    if key == 'r':
        restart(app)
    elif key == 's':
        app.solution = not app.solution

def main():
    runApp(800, 600)

main()