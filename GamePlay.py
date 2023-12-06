import math
import random
#functions Used for Game Plays

# when it is user's turn, it returns the cell selected 
# when it is opponent's turn, it generates guesses and the intelligence of this 
# guess is based on the level of difficulty selected
def makeMove(app, x, y):
    if app.userTurn:
        return getCell(app, x, y)
    elif app.oppTurn:
        if app.oppLevel == 'standard':
            # if standard, all guesses are completely randomized
            row = random.randint(0, 7)
            col = random.randint(0, 7)
        elif app.oppLevel == 'intermediate':
            if app.oppGuesses == []:
                # in intermediate, guesses are first randomly generated
                row = random.randint(0, 7)
                col = random.randint(0, 7)
            else:
                # once correct guess is made, next guesses are based on adjacent 
                # cells which has high chance of rest of the ship being located
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
                # compares the two cells that has been hit correctly and tracks rest of the ship
                moveOptions = trackSameShip(app, pastRow, pastCol, goodRow, goodCol)
                if moveOptions != []:
                    row, col = moveOptions.pop()
                else:
                    row, col = smarterRandom(app)
                    if (row,col) in app.wrongGuessesOpp or (row,col) in app.oppGuesses:
                        return makeMove(app, x, y)
            else:
                # when there is only one correct guess, it tries adjacent cells
                goodRow, goodCol = app.oppGuesses[-1]
                moveOptions = smartTarget(app, goodRow, goodCol)
                if moveOptions != []:
                    row, col = moveOptions.pop()
                else:
                    row, col = smarterRandom(app)
                    if (row,col) in app.wrongGuessesOpp or (row,col) in app.oppGuesses:
                        return makeMove(app, x, y)              
        return (row,col)

# used for intermediate guesses; returns coordinates of cells adjacent to 'correct' hits
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


# two functions below are used for advanced guesses
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


# checks if a ship is destroyed
def isDestroyed(row, col, board):
    for i in range(len(board)):
        ship = board[i]
        if (row, col) in ship:
            return (True, i)
    return (False, 0)

# if a ship is completely sunk, it removes that ship out of the main board
def completelySunk(board):
    if [] in board:
        board.remove([])
    return board

# returns the cell selected
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

# helper function needed for getting the (row, col) of cell 
def getCellSize(app):
    cellWidth = app.boardWidth / app.cols
    cellHeight = app.boardHeight / app.rows
    return (cellWidth, cellHeight)


# helper function needed for game play in separate files
def getCellLeftTop(app, row, col, boardLeft):
    cellWidth, cellHeight = getCellSize(app)
    cellLeft = boardLeft + col * cellWidth
    cellTop = app.boardTop + row * cellHeight
    return (cellLeft, cellTop)