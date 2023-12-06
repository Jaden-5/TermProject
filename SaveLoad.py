# Organized functions used for Reading and Writing external text file

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

import ast
def loadGame(app):
    # opens the txt file in reading mode and assigns all data to relevant variables
    # https://codedamn.com/news/python/how-to-convert-a-string-to-a-list-in-python 
    # referenced to look for other ways to convert a string to a list since list() command would not work
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