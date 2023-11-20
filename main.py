from cmu_graphics import *
import math


ship1 = [(1,1), (1,2), (1,3)]
ship2 = [(1,6), (2,6), (3,6), (4,6)]
ship3 = [(4,1), (5,1), (6,1), (7,1)]
ship4 = [(4,2), (4,3), (4,4)]
app.board = ship1 + ship2 + ship3 + ship4

# [['0', '0', '0', '0', '0', '0', '0', '0'], ['0', '1', '1', '1', '0', '0', '1', '0'],
#                ['0', '0', '0', '0', '0', '0', '1', '0'], ['0', '0', '0', '0', '0', '0', '1', '0'],
#                ['0', '1', '1', '1', '1', '0', '1', '0'], ['0', '1', '0', '0', '0', '0', '0', '0'], 
#               ['0', '1', '0', '0', '0', '0', '0', '0'], ['0', '1', '0', '0', '0', '0', '0', '0'] ]

def makeMove(app, x, y):
    dx = x - app.boardLeft1
    dy = y - app.boardTop
    cellWidth, cellHeight = getCellSize(app)
    row = math.floor(dy / cellHeight)
    col = math.floor(dx / cellWidth)
    if (0 <= row < app.rows) and (0 <= col < app.cols):
      return (row, col)
    else:
        return None
    
def isDestroyed(app, row, col):
    if (row, col) in app.board:
        return True
    return False
   
def onMousePress(app, mouseX, mouseY):
    row, col = makeMove(app, mouseX, mouseY)
    if (row, col) != None and isDestroyed(app, row, col): 
        app.board.remove((row, col))
        app.message = "Successful Hit!"
        return app.board
    else:
        app.message = "missed!"
        return app.board

def onAppStart(app):
    app.message = 'hi!'
    app.rows = 8
    app.cols = 8
    app.boardLeft1 = app.width/15 
    # parameter for the opponents's board
    app.boardTop = app.height/5
    app.boardWidth = app.width/2.4
    app.boardHeight = app.height/2.4
    app.cellBorderWidth = 1
    app.cellWidth = app.boardWidth / app.cols
    app.cellHeight = app.boardHeight / app.rows

    # Parameters for the user's board
    app.boardLeft2 = app.boardLeft1 + app.boardWidth + 20  # Separation of 20 pixels
    app.boardWidth2 = app.boardWidth
    app.boardHeight2 = app.boardHeight

def redrawAll(app):
    drawLabel(app.message, app.width/2, app.height/10)

    drawBoard(app, app.boardLeft1)
    drawBoardBorder(app, app.boardLeft1)

    drawBoard(app, app.boardLeft2)
    drawBoardBorder(app, app.boardLeft2)

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
    drawRect(cellLeft, cellTop, cellWidth, cellHeight,
             fill=None, border='black',
             borderWidth=app.cellBorderWidth)

    # make sure only users can see their boards
    if boardLeft == app.boardLeft1:
        if (row, col) in app.board:
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