import copy

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