# This is a very simple implementation of the UCT Monte Carlo Tree Search algorithm in Python 2.7.
# The function UCT(rootstate, itermax, verbose = False) is towards the bottom of the code.
# It aims to have the clearest and simplest possible code, and for the sake of clarity, the code
# is orders of magnitude less efficient than it could be made, particularly by using a
# state.GetRandomMove() or state.DoRandomRollout() function.
#
# Example GameState classes for Nim, OXO and Othello are included to give some idea of how you
# can write your own GameState use UCT in your 2-player game. Change the game to be played in
# the UCTPlayGame() function at the bottom of the code.
#
# Written by Peter Cowling, Ed Powley, Daniel Whitehouse (University of York, UK) September 2012.
#
# Licence is granted to freely use and distribute for any sensible/legal purpose so long as this comment
# remains in any distributed code.
#
# For more information about Monte Carlo Tree Search check out our web site at www.mcts.ai

from math import *
import pickle
import random
import time
from copy import deepcopy


board_val = {} # store calculated block heuristics
randTable = [[[[long(0) for l in xrange(2)] for k in xrange(2)] for j in xrange(9)] for i in xrange(9)] # random strings for hash components
boardHash = long(0)

def block_score(board, board_num, block_num, ply):
    b1 = block_num/3
    b2 = block_num%3

    # We won the small board
    if board.small_boards_status[board_num][b1][b2] == ply:
        return 600
    # We lost or drew the small board. Put it as 0 instead of a negative value
    # as we are going to subtract our attack score from opponent's attack score anyways
    elif board.small_boards_status[board_num][b1][b2] == conj(ply) or board.small_boards_status[board_num][b1][b2] == 'd':
        return 0
    # Small board in progress
    else:
        def convert2num(flag):
            if flag == ply:
                return 1
            elif flag == '-':
                return 0
            else:
                return -2

        # Find out if each of the lines(horizontal, vertical & diagonal) are 1-attack
        # or 2-attack or none. If it is 1-attack, val is 2. If it is 2-attack, val is 1.
        # Else val is <= 0
        lines = [ 0, 0, 0, 0, 0, 0, 0, 0 ]
        lines[0] = convert2num(board.big_boards_status[board_num][3*b1][3*b2]) +\
                   convert2num(board.big_boards_status[board_num][3*b1][3*b2+1]) +\
                   convert2num(board.big_boards_status[board_num][3*b1][3*b2+2])
        lines[1] = convert2num(board.big_boards_status[board_num][3*b1+1][3*b2]) +\
                   convert2num(board.big_boards_status[board_num][3*b1+1][3*b2+1]) +\
                   convert2num(board.big_boards_status[board_num][3*b1+1][3*b2+2])
        lines[2] = convert2num(board.big_boards_status[board_num][3*b1+2][3*b2]) +\
                   convert2num(board.big_boards_status[board_num][3*b1+2][3*b2+1]) +\
                   convert2num(board.big_boards_status[board_num][3*b1+2][3*b2+2])
        lines[3] = convert2num(board.big_boards_status[board_num][3*b1][3*b2]) +\
                   convert2num(board.big_boards_status[board_num][3*b1+1][3*b2]) +\
                   convert2num(board.big_boards_status[board_num][3*b1+2][3*b2])
        lines[4] = convert2num(board.big_boards_status[board_num][3*b1][3*b2+1]) +\
                   convert2num(board.big_boards_status[board_num][3*b1+1][3*b2+1]) +\
                   convert2num(board.big_boards_status[board_num][3*b1+2][3*b2+1])
        lines[5] = convert2num(board.big_boards_status[board_num][3*b1][3*b2+2]) +\
                   convert2num(board.big_boards_status[board_num][3*b1+1][3*b2+2]) +\
                   convert2num(board.big_boards_status[board_num][3*b1+2][3*b2+2])
        lines[6] = convert2num(board.big_boards_status[board_num][3*b1][3*b2]) +\
                   convert2num(board.big_boards_status[board_num][3*b1+1][3*b2+1]) +\
                   convert2num(board.big_boards_status[board_num][3*b1+2][3*b2+2])
        lines[7] = convert2num(board.big_boards_status[board_num][3*b1][3*b2+2]) +\
                   convert2num(board.big_boards_status[board_num][3*b1+1][3*b2+1]) +\
                   convert2num(board.big_boards_status[board_num][3*b1+2][3*b2])

        # Take weighted sum of number of 1 attacks and 2 attacks to get the block score
        two_attacks = 0
        one_attacks = 0
        for i in range(0, 8):
            if lines[i] == 1:
                two_attacks += 1
            elif lines[i] == 2:
                one_attacks += 1
        my_block_score = 100 * one_attacks + 10 * (two_attacks)
        return my_block_score

# Calculate game score for heuristic
def game_score(board, board_num, ply):
    # Get the block scores to use them as probabilites.
    # Should we normalise with self.score_block?
    my_block1 = block_score(board, board_num, 0, ply)
    my_block2 = block_score(board, board_num, 1, ply)
    my_block3 = block_score(board, board_num, 2, ply)
    my_block4 = block_score(board, board_num, 3, ply)
    my_block5 = block_score(board, board_num, 4, ply)
    my_block6 = block_score(board, board_num, 5, ply)
    my_block7 = block_score(board, board_num, 6, ply)
    my_block8 = block_score(board, board_num, 7, ply)
    my_block9 = block_score(board, board_num, 8, ply)

    # Multiply the block probabilites to get the line probabilites
    line_score = 0
    line_score += my_block1 * my_block2 * my_block3
    line_score += my_block1 * my_block4 * my_block7
    line_score += my_block1 * my_block5 * my_block9
    line_score += my_block2 * my_block5 * my_block8
    line_score += my_block3 * my_block5 * my_block7
    line_score += my_block3 * my_block6 * my_block9
    line_score += my_block4 * my_block5 * my_block6
    line_score += my_block7 * my_block8 * my_block9

    return line_score

# Heuristic function
def heuristic(board, my_flag):
    # Get attack score for us and opponent by summing up block scores
    opp_flag = conj(my_flag)

    my_attack_score = 0
    my_attack_score += 4*(block_score(board, 0, 0, my_flag) + block_score(board, 1, 0, my_flag))
    my_attack_score += 6*(block_score(board, 0, 1, my_flag) + block_score(board, 1, 1, my_flag))
    my_attack_score += 4*(block_score(board, 0, 2, my_flag) + block_score(board, 1, 2, my_flag))
    my_attack_score += 6*(block_score(board, 0, 3, my_flag) + block_score(board, 1, 3, my_flag))
    my_attack_score += 3*(block_score(board, 0, 4, my_flag) + block_score(board, 1, 4, my_flag))
    my_attack_score += 6*(block_score(board, 0, 5, my_flag) + block_score(board, 1, 5, my_flag))
    my_attack_score += 4*(block_score(board, 0, 6, my_flag) + block_score(board, 1, 6, my_flag))
    my_attack_score += 6*(block_score(board, 0, 7, my_flag) + block_score(board, 1, 7, my_flag))
    my_attack_score += 4*(block_score(board, 0, 8, my_flag) + block_score(board, 1, 8, my_flag))

    opp_attack_score = 0
    opp_attack_score += 4*(block_score(board, 0, 0, opp_flag) + block_score(board, 1, 0, opp_flag))
    opp_attack_score += 6*(block_score(board, 0, 1, opp_flag) + block_score(board, 1, 1, opp_flag))
    opp_attack_score += 4*(block_score(board, 0, 2, opp_flag) + block_score(board, 1, 2, opp_flag))
    opp_attack_score += 6*(block_score(board, 0, 3, opp_flag) + block_score(board, 1, 3, opp_flag))
    opp_attack_score += 3*(block_score(board, 0, 4, opp_flag) + block_score(board, 1, 4, opp_flag))
    opp_attack_score += 6*(block_score(board, 0, 5, opp_flag) + block_score(board, 1, 5, opp_flag))
    opp_attack_score += 4*(block_score(board, 0, 6, opp_flag) + block_score(board, 1, 6, opp_flag))
    opp_attack_score += 6*(block_score(board, 0, 7, opp_flag) + block_score(board, 1, 7, opp_flag))
    opp_attack_score += 4*(block_score(board, 0, 8, opp_flag) + block_score(board, 1, 8, opp_flag))


    # Get game score from game_score function
    my_game_score = game_score(board, 0, my_flag) + game_score(board, 1, my_flag)
    opp_game_score = game_score(board, 0, opp_flag) + game_score(board, 1, opp_flag)

    # Take weighted sum of attack score(how good the board is if we draw the game)
    # and game score(how good the board is for winning the game) to get the heuristic
    #h = self.attack_weight * (my_attack_score - opp_attack_score) + self.game_weight * (my_game_score - opp_game_score)
    #return h
    return (my_attack_score, my_game_score, opp_attack_score, opp_game_score)


def hash_init():
    for i in xrange(9):
        for j in xrange(9):
            for k in xrange(2):
                for l in xrange(2):
                    randTable[i][j][k][l] = long(random.randint(1, 2**64))


def addMovetoHash(cell, player):
    x = cell[0]
    y = cell[1]
    z = cell[2]
    # player -> 0: opponent, 1: us
    boardHash ^= randTable[x][y][z][player]

def conj(playerjm):
    if playerjm == 'x':
        return 'o'
    else:
        return 'x'


def print_board(big_boards_status, small_boards_status):
	# for printing the state of the board
	print '================BigBoard State================'
	for i in range(9):
		if i%3 == 0:
			print
		for k in range(2):
			for j in range(9):
				if j%3 == 0:
					print "",
				print big_boards_status[k][i][j],
			if k==0:
				print "   ",
		print
	print

	print '==============SmallBoards States=============='
	for i in range(3):
		for k in range(2):
			for j in range(3):
				print small_boards_status[k][i][j],
			if k==0:
				print "  ",
		print
	print '=============================================='
	print
	print


class BigBoard:

    def __init__(self):
		# big_boards_status is the game board
		# small_boards_status shows which small_boards have been won/drawn and by which player
        self.big_boards_status = ([['-' for i in range(9)] for j in range(9)], [['-' for i in range(9)] for j in range(9)])
        self.small_boards_status = ([['-' for i in range(3)] for j in range(3)], [['-' for i in range(3)] for j in range(3)])
        self.playerJustMoved = 'x'
        self.inrow = False

    def Clone(self):
        st = BigBoard()
        st.playerJustMoved = self.playerJustMoved
        st.big_boards_status = deepcopy(self.big_boards_status)
        st.small_boards_status = deepcopy(self.small_boards_status)
        return st


    def GetMoves(self, old_move):
		#returns the valid cells allowed given the last move and the current board state
		allowed_cells = []
		allowed_small_board = [old_move[1]%3, old_move[2]%3]
		#checks if the move is a free move or not based on the rules

		if old_move == (-1,-1,-1) or (self.small_boards_status[0][allowed_small_board[0]][allowed_small_board[1]] != '-' and self.small_boards_status[1][allowed_small_board[0]][allowed_small_board[1]] != '-'):
			for k in range(2):
				for i in range(9):
					for j in range(9):
						if self.big_boards_status[k][i][j] == '-' and self.small_boards_status[k][i/3][j/3] == '-':
							allowed_cells.append((k,i,j))

		else:
			for k in range(2):
				if self.small_boards_status[k][allowed_small_board[0]][allowed_small_board[1]] == "-":
					for i in range(3*allowed_small_board[0], 3*allowed_small_board[0]+3):
						for j in range(3*allowed_small_board[1], 3*allowed_small_board[1]+3):
							if self.big_boards_status[k][i][j] == '-':
								allowed_cells.append((k,i,j))

		return allowed_cells

    def GetResult(self, playerjm):
		#checks if the game is over(won or drawn) and returns the player who have won the game or the player who has higher small_boards in case of a draw

        cntx = 0
        cnto = 0
        cntd = 0

        for k in xrange(2):
            bs = self.small_boards_status[k]
            for i in xrange(3):
                row = bs[i]
                col = [x[i] for x in bs]
				#print row,col
				#checking if i'th row or i'th column has been won or not
                if (row[0] == playerjm) and (row.count(row[0]) == 3):
					return 1.0
                elif (row[0] == conj(playerjm)) and (row.count(row[0]) == 3):
					return 0.0

                if (col[0] == playerjm) and (col.count(col[0]) == 3):
					return 1.0
                elif (col[0] == conj(playerjm)) and (col.count(col[0]) == 3):
					return 0.0

            #check diagonals
            if(bs[0][0] == bs[1][1] == bs[2][2]) and bs[0][0] == playerjm:
                return 1.0
            elif(bs[0][0] == bs[1][1] == bs[2][2]) and bs[0][0] == conj(playerjm):
                return 0.0

            if(bs[0][2] == bs[1][1] == bs[2][0]) and bs[0][2] == playerjm:
                return 1.0
            elif(bs[0][2] == bs[1][1] == bs[2][0]) and bs[0][2] == conj(playerjm):
                return 0.0

        if cntx+cnto+cntd == 18:							#if game is drawn
			return 0.5
        else:
            return -1.0


    # changed update
    def DoMove(self, new_move, prev, set = 0):
		#updating the game board and small_board status as per the move that has been passed in the arguements
        ply = self.playerJustMoved

        if set == 1:
            print ply

        self.big_boards_status[new_move[0]][new_move[1]][new_move[2]] = ply

        x = new_move[1]/3
        y = new_move[2]/3
        k = new_move[0]
        fl = 0

		#checking if a small_board has been won or drawn or not after the current move
        bs = self.big_boards_status[k]
        for i in range(3):
			#checking for horizontal pattern(i'th row)
            if (bs[3*x+i][3*y] == bs[3*x+i][3*y+1] == bs[3*x+i][3*y+2]) and (bs[3*x+i][3*y] == ply):
                self.small_boards_status[k][x][y] = ply
                if prev:
                    self.playerJustMoved = conj(self.playerJustMoved)
                if set == 1:
                    print "1"
                return True
                #return 'SUCCESSFUL', True
			#checking for vertical pattern(i'th column)
            if (bs[3*x][3*y+i] == bs[3*x+1][3*y+i] == bs[3*x+2][3*y+i]) and (bs[3*x][3*y+i] == ply):
                self.small_boards_status[k][x][y] = ply
                if prev:
                    self.playerJustMoved = conj(self.playerJustMoved)
                if set == 1:
                    print "2"
                return True
                #return 'SUCCESSFUL', True
		#checking for diagonal patterns
		#diagonal 1
        if (bs[3*x][3*y] == bs[3*x+1][3*y+1] == bs[3*x+2][3*y+2]) and (bs[3*x][3*y] == ply):
            self.small_boards_status[k][x][y] = ply
            if prev:
                self.playerJustMoved = conj(self.playerJustMoved)
            if set == 1:
                print "3"
            return True
            #return 'SUCCESSFUL', True
		#diagonal 2
        if (bs[3*x][3*y+2] == bs[3*x+1][3*y+1] == bs[3*x+2][3*y]) and (bs[3*x][3*y+2] == ply):
            self.small_boards_status[k][x][y] = ply
            if prev:
                self.playerJustMoved = conj(self.playerJustMoved)
            if set == 1:
                print "1"
            return True
            #return 'SUCCESSFUL', True
		#checking if a small_board has any more cells left or has it been drawn
        for i in range(3):
            for j in range(3):
                if bs[3*x+i][3*y+j] =='-':
                    self.playerJustMoved = conj(self.playerJustMoved)
					#return 'SUCCESSFUL', False
                    #print(self.playerJustMoved)
                    #print(self.playerJustMoved)
                    return False


        self.small_boards_status[k][x][y] = 'd'
        #print(self.playerJustMoved)
        if set == 1:
            print "yes"
        self.playerJustMoved = conj(self.playerJustMoved)
        return False
        #print(self.playerJustMoved)
		#return 'SUCCESSFUL', False

class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """
    def __init__(self, old_move, move = None, parent = None, state = None):
        self.move = move # the move that got us to this node - "None" for the root node
        self.parentNode = parent # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.state = state
        self.untriedMoves = state.GetMoves(old_move) # future child nodes
        self.playerJustMoved = state.playerJustMoved # the only part of the state that the Node needs later
        self.hash = 0

    def UCTSelectChild(self):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        s = sorted(self.childNodes, key = lambda c: c.wins/c.visits + sqrt(2*log(self.visits)/c.visits))[-1]
        return s

    def AddChild(self, las, m, s):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        n = Node(las, move = m, parent = self, state = s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n

    def Update(self, result):
        """ Update this node - one additional visit and result additional wins. result must be from the viewpoint of playerJustmoved.
        """
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(self.untriedMoves) + "]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
             s += c.TreeToString(indent+1)
        return s

    def IndentString(self,indent):
        s = "\n"
        for i in range (1,indent+1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
             s += str(c) + "\n"
        return s


def UCT(las, rootstate, itermax, verbose = False):
    """ Conduct a UCT search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
        Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""

    rootnode = Node(las, state = rootstate)

    prev = False
    old_move = (-1, -1, -1)
    for i in range(itermax):
        node = rootnode
        state = rootstate.Clone()

        # Select
        while node.untriedMoves == [] and node.childNodes != []: # node is fully expanded and non-terminal
            node = node.UCTSelectChild()
            ret = state.DoMove(node.move, prev)
            if prev and ret:
                prev = False
            else:
                prev = ret

        # Expand
        if node.untriedMoves != []: # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untriedMoves)
        #    _, val = state.DoMove(m, state.playerJustMoved)
        #    if not val:
        #        state.playerJustmoved = conj(state.playerJustMoved)
            ret = state.DoMove(m,prev)
            old_move = m
            if prev and ret:
                prev = False
            else:
                prev = ret
            node = node.AddChild(old_move, m,state) # add child and descend tree


        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while state.GetMoves(old_move) != []: # while state is non-terminal
            #state.DoMove(random.choice(state.GetMoves()))
            m = random.choice(state.GetMoves(old_move))
            ret = state.DoMove(m,prev)
            old_move = m
            if prev and ret:
                prev = False
            else:
                prev = ret


        # Backpropagate
        while node != None: # backpropagate from the expanded node and work back to the root node
            node.Update(state.GetResult(node.playerJustMoved)) # state is terminal. Update node with result from POV of node.playerJustMoved
            #print(node.state)
            #print_board(node.state.big_boards_status)
            if node.playerJustMoved == 'x' and node.parentNode is not None:
                node.hash = node.parentNode.hash ^ randTable[node.move[2]][node.move[1]][node.move[0]][0]
            elif node.parentNode is not None:
                node.hash = node.parentNode.hash ^ randTable[node.move[2]][node.move[1]][node.move[0]][1]

            if node.parentNode is not None:
                if node.hash not in board_val:
                    val = heuristic(node.state, node.playerJustMoved)
                    board_val[node.hash] = [node.wins, node.visits, val[0], val[1], val[2], val[3]]
                else:
                    board_val[node.hash][0] += node.wins
                    #print(node.hash, board_val[node.hash])
                    board_val[node.hash][1] += node.visits
                #print(board_val)
            #dict.append((node.hash, ()))
            #print(node.move)

            node = node.parentNode

    # Output some information about the tree - can be omitted
    #if (verbose): print rootnode.TreeToString(0)
    #else: print rootnode.ChildrenToString()

    return sorted(rootnode.childNodes, key = lambda c: c.visits)[-1].move # return the move that was most visited

def UCTPlayGame():
    """ Play a sample game between two UCT players where each player gets a different number
        of UCT iterations (= simulations = tree nodes).
    """
    # state = OthelloState(4) # uncomment to play Othello on a square board of the given size
    #state = OXOState() # uncomment to play OXO
    #state = NimState(15) # uncomment to play Nim with the given number of starting chips
    state = BigBoard()
    prev = False
    old_move = (-1, -1, -1)
    while (state.GetResult(state.playerJustMoved) == -1.0):
        #print str(state)
        #time.sleep(1)
        print_board(state.big_boards_status,state.small_boards_status)
        if state.playerJustMoved == 'x':
            #state.inrow = False
            m = UCT(old_move, rootstate = state, itermax = 100000,verbose = False) # play with values for itermax and verbose = True
        else:
            m = UCT(old_move, rootstate = state, itermax = 100000,verbose = False)
            #state.inrow = False
        #print board_val
        print "Best Move: " + str(m) + "\n"
        #print prev
        ret = state.DoMove(m,prev, set = 1)
        #print ret
        old_move = m
        if prev and ret:
            prev = False
        else:
            prev = ret
        #print prev

    if state.GetResult(state.playerJustMoved) == 1.0:
        print "Player " + str(state.playerJustMoved) + " wins!"
    elif state.GetResult(state.playerJustMoved) == 0.0:
        print "Player " + str(conj(state.playerJustMoved)) + " wins!"
    else: print "Nobody wins!"
    print_board(state.big_boards_status,state.small_boards_status)


if __name__ == "__main__":
    """ Play a single game to the end using UCT for both players.
    """

    hash_init()
    #print randTable

    UCTPlayGame()

    #print board_val
    pickle_file = open("clt.pickle", "wb")
    pickle.dump(board_val, pickle_file)
    pickle_file.close()

    pickle_file = open("clt.pickle", "rb")
    arr = pickle.load(pickle_file)
    pickle_file.close()
    print arr
