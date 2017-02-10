import sys
import copy
from numpy import inf

# public variable
traverseLog = "Node,Depth,Value,Alpha,Beta\n"
straightPasses = 0

# return True if a position is in bound
# @param pos: array consisting of two numbers indicating its x and y position
def isInBound(pos):
    if max(pos) < 8 and min(pos) >= 0:
        return True
    return False


# return True if it's valid to expand this position, or False o.w.
# @param board is a two-dimensional list containing 0, 1 or 2 indicating the board states
# @param pos is position to be determined valid or not
# @param party indicates which kind of move is to judge, 1 -> O and 2 -> X
def isValidMove(board, pos, party):
    if not isInBound(pos):
        return False
    y = pos[0]
    x = pos[1]
    if board[y][x] != 0:
        return False
    opp = 3 - party
    # print "opp is " + str(opp)
    vectors = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
    for vec in vectors:
        # print "vec is " + str(vec)
        # dst = pos + vec
        dst = [pos[0]+vec[0], pos[1]+vec[1]]
        count = 0
        # print "dst is " + str(dst) + " dst[0] = " + str(dst[0]) + " dst[1] = " + str(dst[1])
        while isInBound(dst) and board[dst[0]][dst[1]] == opp:
            #print "dst is " + str(dst)
            # dst = dst + vec
            dst = [dst[0]+vec[0], dst[1]+vec[1]]
            count = count + 1
        if count > 0 and isInBound(dst) and board[dst[0]][dst[1]] == party:
            #print "board[" + str(dst[0]) + "][" + str(dst[1]) + "] = " + str(party)
            return True
    return False

# return true if the game is terminated, or false if not
def terminalTest(board):
    validMoveX = False
    validMoveO = False
    numX = 0
    numO = 0
    for y in xrange(0,8):
        for x in xrange(0,8):
            if board[y][x] == 1:
                numO = numO + 1
            elif board[y][x] == 2:
                numX = numX + 1
            else:
                # pos = list()
                # pos.append(y)
                # pos.append(x)
                pos = [y, x]
                if validMoveO == False and isValidMove(board,pos,1):
                    validMoveO = True
                if validMoveX == False and isValidMove(board,pos,2):
                    validMoveX = True
    if (validMoveX or validMoveO) and numO > 0 and numX > 0:
        return False
    return True

# calculate the utility value for a given state (board) and given side
def utility(board, side):
    value = 0
    weights = [
        [99, -8, 8, 6, 6, 8, -8, 99],
        [-8, -24, -4, -3, -3, -4, -24, -8],
        [8, -4, 7, 4, 4, 7, -4, 8],
        [6, -3, 4, 0, 0, 4, -3, 6],
        [6, -3, 4, 0, 0, 4, -3, 6],
        [8, -4, 7, 4, 4, 7, -4, 8],
        [-8, -24, -4, -3, -3, -4, -24, -8],
        [99, -8, 8, 6, 6, 8, -8, 99]
    ]
    opp = 3 - side
    for y in xrange(0, 8):
        for x in xrange(0, 8):
            if board[y][x] == side:
                value = value + weights[y][x]
            elif board[y][x] == opp:
                value = value - weights[y][x]
    return value

# get the valid actions for a certain board state and certain side
def getActions(board, side):
    result = []
    for y in xrange(0, 8):
        for x in xrange(0, 8):
            pos = [y, x]
            if isValidMove(board, pos, side):
                result.append(pos)
    return result

# update the board state after one action is taken
def updateState(board, action, side):
    if action[0] == -1 and action[1] == -1:
        return board
    newboard = copy.deepcopy(board)
    newboard[action[0]][action[1]] = side
    opp = 3 - side
    vectors = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
    for vec in vectors:
        count = 0
        dst = [action[0]+vec[0], action[1]+vec[1]]
        while isInBound(dst) and newboard[dst[0]][dst[1]] == opp:
            count = count + 1
            dst = [dst[0]+vec[0], dst[1]+vec[1]]
        if count > 0 and isInBound(dst) and newboard[dst[0]][dst[1]] == side:
            dst = [action[0] + vec[0], action[1] + vec[1]]
            for i in xrange(count):
                newboard[dst[0]][dst[1]] = side
                dst = [dst[0]+vec[0], dst[1]+vec[1]]
    return newboard

# update the traverse log with current status
def updateLog(name, depth, value, alpha, beta):
    global traverseLog
    info = name + "," + str(depth) + ","
    str_val = str(value)
    if value == inf:
        str_val = "Infinity"
    if value == -inf:
        str_val = "-Infinity"
    str_alpha = str(alpha)
    if alpha == inf:
        str_alpha = "Infinity"
    if alpha == -inf:
        str_alpha = "-Infinity"
    str_beta = str(beta)
    if beta == inf:
        str_beta = "Infinity"
    if beta == -inf:
        str_beta = "-Infinity"
    info = info + str_val + "," + str_alpha + "," + str_beta
    if debugMode:
        print info
    traverseLog = traverseLog + info + "\n"
    return info

# function get called by the Alpha-Beta Pruning
# maximize the score of side by choosing best move for this side
def maxvalue(board, alpha, beta, side, curDepth, name):
    global traverseLog
    global straightPasses
    if False:# debugMode:
        print "maxvalue input board:"
        for line in board:
            print line
    best_move = [-1, -1]
    if straightPasses == 2 or curDepth == search_depth:
        val = utility(board, side)
        info = updateLog(name, curDepth, val, alpha, beta)
        # print info
        straightPasses = 1
        return val, best_move
    val = -inf
    opp = 3 - side
    currActions = getActions(board, side)
    if len(currActions) == 0:
        currActions = [[-1, -1]]
        straightPasses = straightPasses + 1
    else:
        straightPasses = 0
    if debugMode:
        print currActions
    for action in currActions:
        info = updateLog(name, curDepth, val, alpha, beta)
        # print info
        if action == [-1, -1]:
            next_name = "pass"
        else:
            next_name = alphaNumericTable[action[1]] + str(action[0] + 1)
        # val = max(val, minvalue(updateState(board, action, side), alpha, beta, side, curDepth + 1, next_name))
        score, move = minvalue(updateState(board, action, side), alpha, beta, side, curDepth + 1, next_name)
        if score > val:
            #print "update: val from " + str(val) + " to " + str(score) + ", best move from " + str(
            #    best_move) + " to " + str(move)
            val = score
            best_move = action
        if val >= beta:
            info = updateLog(name, curDepth, val, alpha, beta)
            # print info
            return val, best_move
        alpha = max(alpha, val)
    info = updateLog(name, curDepth, val, alpha, beta)
    # print info
    return val, best_move

# minimize the score of side by choosing best move for opponent
def minvalue(board, alpha, beta, side, curDepth, name):
    global traverseLog
    global straightPasses
    if False: # debugMode:
        print "minvalue input board:"
        for line in board:
            print line
    best_move = [-1, -1]
    if straightPasses == 2 or curDepth == search_depth:
        val = utility(board, side)
        info = updateLog(name, curDepth, val, alpha, beta)
        # print info
        return val, best_move
    val = inf
    opp = 3 - side
    currActions = getActions(board, opp)
    if len(currActions) == 0:
        currActions = [[-1, -1]]
        straightPasses = straightPasses + 1
    else:
        straightPasses = 0
    if debugMode:
        print currActions
    for action in currActions:
        info = updateLog(name, curDepth, val, alpha, beta)
        # print info
        if action == [-1, -1]:
            next_name = "pass"
        else:
            next_name = alphaNumericTable[action[1]] + str(action[0] + 1)
        # val = min(val, maxvalue(updateState(board, action, opp), alpha, beta, side, curDepth + 1, next_name))
        score, move = maxvalue(updateState(board, action, opp), alpha, beta, side, curDepth + 1, next_name)
        if score < val:
            #print "update: val from " + str(val) + " to " + str(score) + ", best move from " + str(
            #    best_move) + " to " + str(move)
            val = score
            best_move = action
        if val <= alpha:
            info = updateLog(name, curDepth, val, alpha, beta)
            # print info
            return val, best_move
        beta = min(beta, val)
    info = updateLog(name, curDepth, val, alpha, beta)
    # print info
    return val, best_move

# legacy method, choose the best method with certain value
def bestAction(board, actions, val, side):
    if debugMode:
        print actions
    for move in actions:
        newBoard = updateState(board, move, side)
        score = utility(newBoard, side)
        if True:#debugMode:
            print "for " + str(move) + ", the score is " + str(score)
        if score == val:
            return move
    return [-1, -1]

# the method implementing Alpha-Beta Search
def AlphaBetaSearch(board, side, depth):
    actions = getActions(board, side)
    alpha = -inf # -1000000000 # -math.inf
    beta = inf # 1000000000 # math.inf
    best_move = [-1, -1]
    #print "Node,Depth,Value,Alpha,Beta"
    val, best_move = maxvalue(board, alpha, beta, side, depth, "root")
    if debugMode:
        print "maxvalue is " + str(val)
        print "actions are " + str(actions)
    #return bestAction(board, actions, val, side)
    return best_move

if __name__ == "__main__":
    #global traverseLog
    inputfilepath = "input.txt"
    outputfilepath = "output.txt"
    if len(sys.argv) == 3 and str(sys.argv[1]) == "-i":
        inputfilepath = str(sys.argv[2])
    debugMode = False
    if len(sys.argv) == 2 and str(sys.argv[1]) == "-d":
        debugMode = True

    init_board = list()
    board = list()
    with open(inputfilepath) as inputf:
        for i, line in enumerate(inputf):
            # print str(i) + " " + line
            if i == 0:
                player = str(line)[0]
            elif i == 1:
                search_depth = int(line)
            else:
                init_board.append(line)
                # board = board + str(line)
    if debugMode:
        print "Player is " + player
        print "depth is " + str(search_depth)
    # print "board is: \n" + board
    party_table = ['*', 'O', 'X']
    party = party_table.index(player)
    # print "party is " + str(party)
    for line in init_board:
        if debugMode:
            print line[:8]
        row = list()
        for i in xrange(0, 8):
            row.append(party_table.index(line[i]))
        # print str(row)
        board.append(row)

    if debugMode:
        for row in board:
            print row

    if debugMode:
        for y in xrange(0, 8):
            string = ""
            for x in xrange(0, 8):
                pos = [y, x]
                string = string + str(isValidMove(board, pos, 2)) + " "
                print string

    #print "Test AlphaBetaSearch: "
    tmpParty = party
    alphaNumericTable = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    step = AlphaBetaSearch(board, party, 0)
    #print alphaNumericTable[step[1]] + str(step[0] + 1)
    #print step
    next_board = updateState(board, step, tmpParty)

    with open(outputfilepath, 'w') as outputf:
        #outputf.write('Hello World!\n')
        for row in next_board:
            line = ""
            for pixel in row:
                line = line + party_table[pixel]
            #print line
            line = line + "\n"
            outputf.write(line)
        traverseLog = traverseLog[:len(traverseLog)-1]
        outputf.write(traverseLog)