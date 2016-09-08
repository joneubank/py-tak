from enum import Enum

class COLORS(Enum):
    '''Colors of the two players in Tak
    '''
    white = 0
    black = 1


class STATES(Enum):
    '''State of Tak Game
    '''
    new             = 0
    playing         = 1
    complete        = 2
    draw            = 3


class WINS(Enum):
    ''' Result type of completed tak game
    '''
    road        = 0
    flat        = 1
    time        = 2


class PIECES(Enum):
    '''List of playing piece types
    '''
    flat = 0
    wall = 1
    cap  = 2


class DIRECTIONS(Enum):
    up    = 0
    down  = 1
    right = 2
    left  = 3

def symbolToDirection(symbol):
    data = {
        '+' : DIRECTIONS.up,
        '-' : DIRECTIONS.down,
        '>' : DIRECTIONS.right,
        '<' : DIRECTIONS.left
    }

    return data[symbol]


def directionToSymbol(direction):

    data = {
        DIRECTIONS.up    : '+',
        DIRECTIONS.down  : '-',
        DIRECTIONS.right : '>',
        DIRECTIONS.left  : '<'
    }

    return data[direction]


def getDirectionMods(direction):
    rowMod = 0
    filMod = 0

    if   direction == DIRECTIONS.up:
        filMod = 1
    elif direction == DIRECTIONS.down:
        filMod = -1
    elif direction == DIRECTIONS.right:
        rowMod = 1
    elif direction == DIRECTIONS.left:
        rowMod = -1

    return filMod, rowMod

class Player(object):

    def __init__(self, color, name):
        self.name           = name

        self.color          = color

        self.flats          = 0
        self.flatsPlayed    = 0

        self.caps           = 0
        self.capsPlayed   = 0

    def __str__(self):
        return "{}".format(self.name)


class Stone(object):

    def __init__(self, color, piece):
        self.color = color
        self.piece = piece

    def __str__(self):
        return "{} {}".format(self.color.name, self.piece.name)

class Space(object):

    # Rows are numbered, files (fil) are lettered
    def __init__(self, row, fil):
        self.row = row
        self.fil = fil

    def __str__(self):
        return "({}, {})".format(self.row, self.fil)

    def ptn(self):
        fils = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
        return "{}{}".format(fils[self.fil], self.row)


class Turn(object):

    def __init__(self, color, space, isMove=False, direction=0, drops=[], piece=PIECES.flat):
        self.color = color
        self.space = space

        self.isMove = isMove # Boolean
        self.direction = direction
        self.drops = drops

        self.piece = piece

        # Number of stones lifted from starting space
        self.picks = sum(drops)

    def __str__(self):

        pieceName = ''
        moveText  = ''
        if self.isMove:
            direction = directionToSymbol(self.direction)
            return "{} move {} from {}, move {} dropping: {}".format(self.color.name, self.picks, self.space, self.direction.name, self.drops)
        else:
            return "{} {} {}".format(self.color.name, self.piece.name, self.space)

    def ptn(self):
        picks = ""
        piece = ""
        space = self.space.ptn()
        direction = ""
        drops = ""

        if not isMove:
            if self.piece == PIECES.cap:
                self.piece = "C"
            elif self.piece == PIECES.wall:
                self.piece = "S"
        else:
            picks = self.picks
            direction = directionToSymbol(self.direction)
            drops = ''.join(drops)


        return "{}".format(
            picks,
            piece,
            space,
            direction,
            drops
        )

class Stack(object):

    def __init__(self):
        self.stones = []
        self.color = None

    def updateColor(self):
        if len(self.stones) > 0:
            self.color = self.stones[-1].color
        else:
            self.color = None

    def pick(self, num):
        if num == None:
            num = 1

        stackheight = len(self.stones)
        if num > stackheight:
            num = stackheight

        picked = self.stones[-num:]
        self.stones = self.stones[:-num]


        self.updateColor()
        return picked

    def place(self, stones):
        """Pieces should be an array
        """
        self.stones += stones
        self.updateColor()

    def height(self):
        return len(self.stones)


    def __str__(self):
        return self.space.__str__()


class Board(object):
    """Tak Game Board, representing a game state
    """

    def __init__(self, size):
        self.size = size
        self.grid = [ [Stack() for y in range(size)] for x in range(size) ]

    def getStack(self, space):
        if space.row < 0 or space.row >= self.size or space.fil < 0 or space.fil >= self.size:
            #reached an off board square, move to next direction
            return None
        return self.grid[space.row][space.fil]

    def apply(self, turn):
        space = self.grid[turn.space.row][turn.space.fil]
        if turn.isMove:
            # move some stones
            stones = space.pick(turn.picks)

            rowMod, filMod = getDirectionMods(turn.direction)
            row = turn.space.row
            fil = turn.space.fil

            for dropNum in turn.drops:
                row += rowMod
                fil += filMod
                dropSpace = self.grid[row][fil]

                # handle flattening walls
                if dropSpace.stones and dropSpace.stones[-1].piece == PIECES.wall:
                    dropSpace.stones[-1].piece = PIECES.flat

                dropSpace.place(stones[:dropNum])
                stones = stones[dropNum:]

        else:
            # Place a stone
            stone = Stone(turn.color, turn.piece)
            space.place([stone])

        # print(self)

    def checkWinner(self):
        """Returns None for no winner, otherwise winning color
        """

        # Find all groups, check for any that reach both sides
        groups = []




    def __str__(self):
        # [ b, w, bwb]
        # [ ., bSw w]
        # [ Cb, w, .]
        output = ""

        for row in reversed(self.grid):

            output += "["
            for stack in row:
                if stack.height() > 0:
                    for stone in stack.stones:

                        #Stone Type
                        if stone.piece == PIECES.wall:
                            output += "S"
                        elif stone.piece == PIECES.cap:
                            output += "C"

                        #Stone Color
                        if stone.color == COLORS.black:
                            output += "b"
                        else:
                            output += "w"

                else:
                    output += "."
                output += "|"

            # Remove extra pipe
            output = output[:-1]
            output +="]\n"


        return output



class Game(object):
    """Tak Game
    """

    def __init__(self):
        self.host               = None
        self.date               = None

        self.size               = None
        self.board              = None

        self.players            = {COLORS.black : Player(COLORS.black, None), COLORS.white : Player(COLORS.white, None)}
        self.white              = None
        self.black              = None

        self.state              = STATES.new
        self.turns              = []
        self.winner             = None # Color
        self.winCondition       = None # WinCondition
        self.ptn_result         = None

    def addTurn(self, turn):
        print(turn)
        self.turns.append(turn)
        if not turn.isMove:
            if turn.piece == PIECES.cap:
                self.players[turn.color].caps -= 1
            else:
                self.players[turn.color].flats -= 1

        if self.board:
            self.board.apply(turn)

    def turnColor(self):
        if (len(self.turns)/2) % 1 == 0:
            output = COLORS.white
        else:
            output = COLORS.black

        output = len(self.turns) < 2
        if firstTurn:
            if output == COLORS.black:
                output = COLORS.white
            else:
                output = COLORS.black

        return output


    def __str__(self):

        if      self.state == STATES.new:
            return "Tak Game - {} (black) vs {} (white) - unstarted".format(
                self.players[COLORS.black],
                self.players[COLORS.white]
            )
        elif    self.state == STATES.playing:
            return "Tak Game - {} (black) vs {} (white) - {} - Turn {}".format(
                self.players[COLORS.black],
                self.players[COLORS.white],
                self.date,
                len(self.turns)/2
            )

        # Default, complete state game
        else:
            return "Tak Game - {} (black) vs {} (white) - {} - {}({}) wins via {} in {} turns".format(
                self.players[COLORS.black],
                self.players[COLORS.white],
                self.date,
                self.players[self.winner].name, # name of winner
                self.winner.name, # color of winner
                self.winCondition.name,
                len(self.turns)/2
            )


if __name__ == '__main__':
    game = Game(5)
