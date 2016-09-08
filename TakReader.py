import sys
import os.path
from datetime import date
import TakWinSolver

# First Party
import Tak

"""
TakReader

Given a ptn file from playtak.com, this will convert the data into a usable
object (TakGame) or convert into an output format, such as json

"""

def parseLine(game, text):
    # remove new line character if present (all but final line of file)
    if text[-1] == "\n":
        text = text[:-1]

    # Ignore blank lines
    if not text:
        return

    if   text[0] == '[':
        parseHeader(game, text) #-2 because each line has a \n character
    elif text[0].isdigit():
        parseTurnLine(game, text) # Pass Full Text without line ending \n

def parseTurnLine(game, text):
    # Example text value: 15. c3< Cc3
    if game.state == Tak.STATES.new:
        game.state = Tak.STATES.playing

    indexSplit = text.split('. ')

    firstTurn = indexSplit[0] == '1'
    print(" - Turn: {}".format(indexSplit[1]))
    turnsSplit = indexSplit[1].split(' ')

    if firstTurn:
        firstColor = Tak.COLORS.black
        secondColor = Tak.COLORS.white
    else:
        firstColor = Tak.COLORS.white
        secondColor = Tak.COLORS.black

    parseTurn(game, turnsSplit[0], firstColor)
    if len(turnsSplit) == 2 and turnsSplit[1]:
        parseTurn(game, turnsSplit[1], secondColor)

def parseTurn(game, text, color):
    # Example text value: 4c1+112
    # __init__ (color, space, isMove=False, direction=0, drops=[], piece=TakPiece.flat):
    isMove = False
    modText = text
    pieceType = Tak.PIECES.flat
    picks = None

    # Check for multi-piece pick up
    if modText[0].isdigit():
        picks = modText[0]
        modText = modText[1:]

    # Check for special piece placement
    if modText[0] in ['C', 'S']:
        pieceName = modText[0]
        modText = modText[1:]
        if pieceName == 'C':
            pieceType = Tak.PIECES.cap
        elif pieceName == 'S':
            pieceType = Tak.PIECES.wall

    fil = letterToNumber(modText[0])-1
    row = int(modText[1])-1
    modText = modText[2:]

    space = Tak.Space(row, fil)

    direction = 0

    drops = []
    if len(modText) > 0:
        isMove = True

        directionSymbol = modText[0]
        direction = Tak.symbolToDirection(directionSymbol)
        if len(modText) > 1:
            drops = [int(drop) for drop in modText[1:] ]
        elif picks:
            drops = [int(picks)]
        else:
            drops = [1]
    turn = Tak.Turn(color, space, isMove, direction, drops, pieceType)

    game.addTurn( turn )


def letterToNumber(letter):
    data = {
        'a' : 1,
        'b' : 2,
        'c' : 3,
        'd' : 4,
        'e' : 5,
        'f' : 6,
        'g' : 7,
        'h' : 8,
        'i' : 9,
        'A' : 1,
        'B' : 2,
        'C' : 3,
        'D' : 4,
        'E' : 5,
        'F' : 6,
        'G' : 7,
        'H' : 8,
        'I' : 9
    }

    return data[letter]


def parseHeader(game, text):
    # Expecting this format: [Date "2016.5.11"]
    # Will still split and take key, value as [0] and [1] in case formatting differs

    splits = text[1:-1].split(' ') # Remove wrapping brackets then split
    key = splits[0]
    value = splits[1][1:-1] # Assume wrapped in "

    if   key == 'Site':
        game.host = value

    elif key == 'Date':
        dateSplits = value.split('.')
        game.date = date(int(dateSplits[0]), int(dateSplits[1]), int(dateSplits[2]))

    elif key == 'Player1':
        game.players[Tak.COLORS.white].name = value
    elif key == 'Player2':
        game.players[Tak.COLORS.black].name = value
    elif key == 'Size':
        game.size = int(value)
        game.board = Tak.Board(game.size)

        numFlats = [10,15,21,30,40,50][game.size-3]
        numCaps = [0,0,1,1,1,2,2][game.size-3]

        game.players[Tak.COLORS.black].flats = numFlats
        game.players[Tak.COLORS.white].flats = numFlats
        game.players[Tak.COLORS.black].caps  = numCaps
        game.players[Tak.COLORS.white].caps  = numCaps

    elif key == 'Result' and value:
        parseResult(game, key, value)


def parseResult(game, key, value):
    game.ptn_result = value
    game.state = Tak.STATES.complete

    whiteResult, blackResult = value.split('-')
    if blackResult == '1/2':
        # Draw Case
        game.state = Tak.STATES.draw

    else:
        # Non Draw Case
        # Check which color won and grab win type from other player's result

        if blackResult == '0':
            game.winner = Tak.COLORS.white
            wintype = whiteResult
        else:
            game.winner = Tak.COLORS.black
            wintype = blackResult

        if  wintype == 'R':
            game.winCondition = Tak.WINS.road
        elif wintype == 'F':
            game.winCondition = Tak.WINS.flat
        else:
            game.winCondition = Tak.WINS.time


def parseGame(filepath):

    game = Tak.Game()

    with open(filepath, 'r') as file:
        print("Reading Game File")
        index = 0
        for line in file:
            parseLine(game, line)


    print("Finished Reading.")

    return game


def main(argv):
    filepath = argv[0]
    if os.path.isfile(filepath):
        game = parseGame(filepath)
        print(game.board)
        print(game)

        # testWinSolver(game)
        # testMoveFinder(game)
        # testTak(game)

def testTak(game):
    print(TakWinSolver.checkTak(game))

def testWinSolver(game):
    roadWinners = TakWinSolver.checkRoads(game.board)
    flatScores  = TakWinSolver.countFlats(game.board)

def testMoveFinder(game):
    whiteMoves = TakWinSolver.getAllMoves(game)

    print(" =============================== ")
    print("Found {} Moves:".format(len(whiteMoves)))
    for move in whiteMoves:
        print(move)


if __name__ == '__main__':

    main(sys.argv[1:])
    # game = Tak.Game()
