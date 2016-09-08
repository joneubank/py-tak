import copy
from Tak import COLORS, DIRECTIONS, PIECES, getDirectionMods, Turn, Space

class Group(object):

    def __init__(self, color):
        self.color  = color
        self.stones = []

# ====================================================
#                     Check Roads
#
# Includes functions for building groups and checking
# groups for roads across the board
# ====================================================

def checkRoads(board):
    """ Board of type Tak.Board
    Returns {white:True, black:True}
    """

    # Find all groups, check for any that reach both sides
    groups = []
    used = []

    size = board.size

    for x in range(size):
        for y in range(size):

            if board.grid[x][y].color and (x, y) not in used:
                if board.grid[x][y].stones[-1].piece != PIECES.wall:
                    # There is a piece at the coordinates (x,y)
                    group = Group(board.grid[x][y].color)

                    buildGroup(board, group, (x, y))

                    groups.append(group)
                    used += group.stones

                    # print( "Group Found - {} - {}".format(group.color.name, group.stones) )


    output = {COLORS.black:False, COLORS.white:False}
    for group in groups:
        if checkGroupForRoad(board.size, group):
            output[group.color] = True

    # print(output)
    return output


def buildGroup(board, group, space):

    # print("Enter build group - {}({}) - group: {}".format(
    #     space,
    #     board.grid[space[0]][space[1]].color,
    #     group['color'])
    # )

    if space not in group.stones and board.grid[space[0]][space[1]].color == group.color and board.grid[space[0]][space[1]].stones[-1].piece != PIECES.wall:

        group.stones.append(space)

        neighbours = getNeighbours(board.size, space)

        # print("Added to group. Will test Neighbours: {}".format(neighbours) )

        for neighbour in neighbours:
            buildGroup(board, group, neighbour)


def getNeighbours(size, space):
    x = space[0]
    y = space[1]

    output = []

    if x < size-1:
        output.append( (x+1,y) )

    if x > 0:
        output.append( (x-1, y) )

    if y < size-1:
        output.append( (x,y+1) )

    if y > 0:
        output.append( (x, y-1) )

    return output


def checkGroupForRoad(size, group):
    horizontalMin = False
    horizontalMax = False
    verticalMin = False
    verticalMax = False

    for stone in group.stones:
        if stone[0] == 0:
            horizontalMin = True
        if stone[0] == size-1:
            horizontalMax = True

        if stone[1] == 0:
            verticalMin = True
        if stone[1] == size-1:
            verticalMax = True

    return (horizontalMin and horizontalMax) or (verticalMin and verticalMax)


# ====================================================
#                     Count Flats
# ====================================================

def countFlats(board):
    #Returns object like: {white:5, black:7}

    output = {COLORS.white:0, COLORS.black:0}
    for row in board.grid:
        for stack in row:
            if stack.color and stack.stones[-1].piece == PIECES.flat:
                output[stack.color] += 1

    print("countFlats output - {}".format(output) )
    return output

# ====================================================
#                     Check for Tak
# Tak is checked for both players having next move,
# The response object has a key for each color with
# the TAK status based on that color moving next.
#
# The method also returns a list of the moves which
#  would complete a road win.
# ====================================================

def checkTak(game):
    """Return object {white:True, black:False}
    """

    output = {
        COLORS.white: {
            COLORS.black:False, COLORS.white:False,
            'turns': {
                COLORS.black:[], COLORS.white:[],
            }
        },
        COLORS.black: {
            COLORS.black:False, COLORS.white:False,
            'turns': {
                COLORS.black:[], COLORS.white:[],
            }
        }
    }

    for moveColor in [COLORS.white, COLORS.black]:
        allMoves = getAllMoves(game, moveColor)

        # 2.
        for move in allMoves:
            testBoard = copy.deepcopy(game.board)
            testBoard.apply(move)

            roadWins = checkRoads(testBoard)
            if roadWins[COLORS.black]:
                output[moveColor][COLORS.black] = True
                output[moveColor]['turns'][COLORS.black].append(move)
            if roadWins[COLORS.white]:
                output[moveColor][COLORS.white] = True
                output[moveColor]['turns'][COLORS.white].append(move)

    return output


def blockTak(game):
    """Returns a list of Tak.Turn objects that will prevent Tak from occurring this turn
    """
    return []

def getAllMoves(game, setColor=None):
    """For a given game state, return a list of all tak moves that are possible
    for the next player.
    If the color of the next player to move is provided, moves will be calculated
    for that player, else the next player to move will be inferred from the current game state
    """
    board = game.board

    turns = []

    firstTurn = len(game.turns) < 2

    if setColor:
        color = setColor

    else:
        if (len(game.turns)/2) % 1 == 0:
            color = COLORS.white
        else:
            color = COLORS.black

        if firstTurn:
            if color == COLORS.black:
                color = COLORS.white
            else:
                color = COLORS.black

        if oppositeColor:
            if color == COLORS.black:
                color = COLORS.white
            else:
                color = COLORS.black

    for x in range(game.size):
        for y in range(game.size):
            space = Space(x, y)
            stack = board.getStack(space)

            # Placements
            if not stack.stones:
                if game.players[color].flats > 0:
                    #  Flats
                    turn = Turn(color, Space(x, y))
                    turns.append(turn)
                    #  Walls
                    if not firstTurn:
                        turn = Turn(color, Space(x, y), piece=PIECES.wall)
                        turns.append(turn)
                if game.players[color].caps > 0 and not firstTurn:
                    #  Caps
                    turn = Turn(color, Space(x, y), piece=PIECES.cap)
                    turns.append(turn)


            # Moves
            #  stack move permutations from max drop to min (shortest move to longest)
            elif stack.color == color and not firstTurn:
                available = len(stack.stones)
                for picks in range(1,min(game.size, available)+1):
                    for direction in DIRECTIONS:
                        xmod, ymod = getDirectionMods(direction)
                        for moveSpaces in range(1,picks+1):
                            xcheck = x+xmod*moveSpaces
                            ycheck = y+ymod*moveSpaces


                            finalSpace = Space(xcheck, ycheck)
                            finalStack = board.getStack(finalSpace)

                            if not finalStack:
                                #reached an off board square, move to next direction
                                break

                            elif finalStack.stones and finalStack.stones[-1].piece == PIECES.cap:
                                # can't stack onto a cap
                                break

                            elif finalStack.stones and finalStack.stones[-1].piece == PIECES.wall and stack.stones[-1].piece == PIECES.cap:
                                # write moves for flattening a wall
                                if moveSpaces == 1:
                                    if picks == 1:
                                        turn = Turn(color, Space(x,y), isMove=True, direction=direction, drops=[picks])
                                        turns.append(turn)
                                    else:
                                        #can't move more than just the cap onto a wall
                                        break
                                else:
                                    dropSequences = dropPermutations(picks-1, moveSpaces-1, permutations=[], drops=[])
                                    for sequence in dropSequences:
                                        sequence.append(1)
                                        turn = Turn(color, Space(x,y), isMove=True, direction=direction, drops=sequence)
                                        turns.append(turn)

                                break

                            else:
                                dropSequences = dropPermutations(picks, moveSpaces, permutations=[], drops=[])
                                for sequence in dropSequences:
                                    turn = Turn(color, Space(x,y), isMove=True, direction=direction, drops=sequence)
                                    turns.append(turn)

    return turns


def dropPermutations(stones, spaces, permutations=[], drops=[]):
    """Given a stack of a set number of stones, with a limited number of spaces
    available to move, this function returns a list of lists, where each sublist
    is a potential sequence of number of stones dropped at each space.
    """
    if stones+len(drops) < spaces:
        return permutations

    # Final call
    if len(drops) == spaces-1:
        drops.append(stones)
        permutations.append(drops)
        return permutations
    else:
        for drop in range(1, stones-spaces+len(drops) + 2 ):
            nextDrops = list(drops)
            nextDrops.append(drop)
            nextStones = stones-drop
            permutations = dropPermutations(nextStones, spaces, permutations=permutations, drops=nextDrops)

    return permutations


def main():
    print(dropPermutations(2,1))
    print(dropPermutations(4,2))

if __name__ == '__main__':
    main()
