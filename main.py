from cmu_graphics import *
import math
import random

def buildShip(dims):
    len_ship = random.randint(3, dims)
    orientation = random.randint(0, 1) # Ship is horizontal if orientation is 0 and vertical if orientation is 1
    if orientation == 0:
        # based on the orientation randomly assigns row and col values of ship and assigns as a tuple
        row_ship = [random.randint(0, dims - 1)] * len_ship
        col = random.randint(0, 4)
        col_ship = list(range(col, col + len_ship))
        coords = tuple(zip(row_ship, col_ship))
    else:
        # Same as above but opposite orientation
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
    
def isLegal(board):
    for i in range(len(board)-1):
        comp1 = set(board[i])
        comp2 = set(board[i+1])
        if len(comp1 & comp2) >= 1:
            return False
    return True

# sample user board
ship1 = [(1,1), (1,2), (1,3)]
ship2 = [(1,6), (2,6), (3,6), (4,6)]
ship3 = [(4,1), (5,1), (6,1), (7,1)]
ship4 = [(4,2), (4,3), (4,4)]
app.board = [ship1] + [ship2] + [ship3] + [ship4]

def makeMove(app, x, y):
    if app.userTurn:
        dx = x - app.boardLeft1
        dy = y - app.boardTop
        cellWidth, cellHeight = getCellSize(app)
        row = math.floor(dy / cellHeight)
        col = math.floor(dx / cellWidth)
        if (0 <= row < app.rows) and (0 <= col < app.cols):
            app.userGuesses.append((row,col))
            return (row, col)
        else:
            return None
    elif app.oppTurn:
        row = random.randint(0, 7)
        col = random.randint(0, 7)
        app.oppGuesses.append((row,col))
        return (row,col)

    
def isDestroyed(row, col, board):
    for i in range(len(board)):
        ship = board[i]
        if (row, col) in ship:
            return (True, i)
    return (False, 0)
   
def onMousePress(app, mouseX, mouseY):
    if ((app.boardLeft1 <= mouseX < app.boardLeft1+app.boardWidth) and 
        (app.boardTop <= mouseY < app.boardTop+app.boardHeight) and app.userTurn):
        row, col = makeMove(app, mouseX, mouseY)
        if isDestroyed(row, col, app.opponentBoard)[0]: 
            index = isDestroyed(row, col, app.opponentBoard)[1]
            app.opponentBoard[index].remove((row, col))
            app.message = "You hit the opponent's ship!"
            app.userTurn, app.oppTurn = False, True
            return app.board
    
    elif app.oppTurn:
        row, col = makeMove(app, mouseX, mouseY)
        if isDestroyed(row, col, app.board)[0]: 
            index = isDestroyed(row, col, app.board)[1]
            app.board[index].remove((row, col))
            app.message = "Opponent hit your ship!"
            app.userTurn, app.oppTurn = True, False
            return app.opponentBoard
    
    else:
        app.message = "Missed! Next Turn."
        app.userTurn = not app.userTurn
        app.oppTurn = not app.oppTurn
        return app.opponentBoard if app.userTurn else app.board 

def onAppStart(app):
    app.message = 'hi!'
    app.rows = 8
    app.cols = 8
    app.boardLeft1 = app.width/15 
    app.boardTop = app.height/5
    app.boardWidth = app.width/2.4
    app.boardHeight = app.height/2.4
    app.cellBorderWidth = 1
    app.cellWidth = app.boardWidth / app.cols
    app.cellHeight = app.boardHeight / app.rows
    app.userTurn = True
    app.oppTurn = False
    app.userGuesses = []
    app.oppGuesses = []

    # Parameters for the user's board
    app.boardLeft2 = app.boardLeft1 + app.boardWidth + 20  # Separation of 20 pixels
    app.boardWidth2 = app.boardWidth
    app.boardHeight2 = app.boardHeight

    #opponent's board
    app.opponentBoard = opponentBoard(4)

def redrawAll(app):
    drawLabel(app.message, app.width/2, app.height/10)

    if app.userTurn:
        name = 'user'
    else:
        name = 'Opponent'
    drawLabel(name, app.width/2, app.height/15)

    drawBoard(app, app.boardLeft1)
    drawBoardBorder(app, app.boardLeft1)

    drawBoard(app, app.boardLeft2)
    drawBoardBorder(app, app.boardLeft2)

    drawRect(app.width/2, 500, 80, 50, fill=None, border='black')

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
    if (row, col) in app.userGuesses and boardLeft == app.boardLeft1:
        color = 'red'
    elif (row,col) in app.oppGuesses and boardLeft == app.boardLeft2:
        color = 'black'
    else:
        color = None
    drawRect(cellLeft, cellTop, cellWidth, cellHeight,
             fill=color, border='black',
             borderWidth=app.cellBorderWidth)

    # make sure only users can see their boards
    if boardLeft == app.boardLeft2:
        changed = []
        for ships in app.board:
            for points in ships:
                changed.append(points)
        if (row, col) in changed:
            drawLabel('1', cellLeft + cellWidth/2, cellTop + cellHeight/2)
        else:
            drawLabel('0', cellLeft + cellWidth/2, cellTop + cellHeight/2)

    # opponents' board
    if boardLeft == app.boardLeft1:
        changed = []
        for ships in app.opponentBoard:
            for points in ships:
                changed.append(points)
        if (row, col) in changed:
            drawLabel('1', cellLeft + cellWidth/2, cellTop + cellHeight/2)
        else:
            drawLabel('0', cellLeft + cellWidth/2, cellTop + cellHeight/2)
        
def getCellLeftTop(app, row, col, boardLeft):
    cellWidth, cellHeight = getCellSize(app)
    cellLeft = boardLeft + col * cellWidth
    cellTop = app.boardTop + row * cellHeight
    return (cellLeft, cellTop)

def getCellSize(app):
    cellWidth = app.boardWidth / app.cols
    cellHeight = app.boardHeight / app.rows
    return (cellWidth, cellHeight)

def main():
    runApp(800, 600)

main()