import copy
import random

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