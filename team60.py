from copy import deepcopy
from time import time
from random import randint

class Team60:

    def __init__(self):
        self.my_flag = 'x'
        self.opp_flag = 'o'
        self.start_time = 0
        self.first = True
        self.draw_utility = 0
        self.win_utility = long(10 ** 18)
        self.lose_utility = long(-1 * (10 ** 18))

        # Heuristic and alpha beta hashing
        self.heuristic_store = {}
        self.block_store = {}
        self.ab_store = {}
        self.bit_string = [ [ [ [ long(0) for k in range(2) ] for j in range(9) ] for i in range(9) ] for y in range(2) ]
        self.board_hash = long(0)
        self.block_hash = [ [ [ long(0) for j in range(3) ] for i in range(3) ] for y in range(2) ]
        self.init_hash()
        self.count = 0
        self.turns = 0

        # Heuristic weights
        self.score_block = 1000.0
        self.score1 = 100.0
        self.score2 = 10.0
        self.c1 =  3.77497239 * (10 ** 4)
        self.c2 =  8.20172422
        self.c3 =  0.496289110
        self.c4 =  -9.94908108 / (10 ** 6)
        self.c5 =  5.71747239 / (10 ** 10)

        # old weights
        # self.attack_weight = 0.5
        # self.attack_weight = 16865
        self.attack_weight = 37729
        # self.game_weight = 1 / (55.0 ** 2)
        # self.game_weight = 7.8552
        self.game_weight = 8.2034

    # Give each position and player pair a random bit string
    def init_hash(self):
        for y in range(2):
            for i in range(9):
                for j in range(9):
                    for k in range(2):
                        self.bit_string[y][i][j][k] = long(randint(1, 2**64))

    # Add/remove action to board and block hashes
    def add_to_hash(self, action, ply):
        x = action[0]
        y = action[1]
        z = action[2]
        self.board_hash ^= self.bit_string[x][y][z][ply]
        self.block_hash[x][y/3][z/3] ^= self.bit_string[x][y][z][ply]

    # Each time move is called, calculate the board and block hashes
    def calculate_hashes(self, board):
        self.board_hash = long(0)
        self.block_hash = [ [ [ long(0) for j in range(3) ] for i in range(3) ] for y in range(2) ]

        for i in range(2):
            for j in range(9):
                for k in range(9):
                    if board.big_boards_status[i][j][k] == self.my_flag:
                        self.board_hash ^= self.bit_string[i][j][k][0]
                        self.block_hash[i][j/3][k/3] ^= self.bit_string[i][j][k][0]
                    elif board.big_boards_status[i][j][k] == self.opp_flag:
                        self.board_hash ^= self.bit_string[i][j][k][1]
                        self.block_hash[i][j/3][k/3] ^= self.bit_string[i][j][k][1]

    # Get the opposite flag
    def opposite_flag(self, flag):
        if flag == 'x':
            return 'o'
        else:
            return 'x'

    # Convenient board update function. Taken from simulator
    def update(self, board, old_move, new_move, ply):
        board.big_boards_status[new_move[0]][new_move[1]][new_move[2]] = ply
        x = new_move[1]/3
        y = new_move[2]/3
        k = new_move[0]

        bs = board.big_boards_status[k]
        if (bs[3*x][3*y] == bs[3*x][3*y+1] == bs[3*x][3*y+2]) and (bs[3*x][3*y] == ply):
            board.small_boards_status[k][x][y] = ply
            return True
        if (bs[3*x][3*y] == bs[3*x+1][3*y] == bs[3*x+2][3*y]) and (bs[3*x][3*y] == ply):
            board.small_boards_status[k][x][y] = ply
            return True
        if (bs[3*x+1][3*y] == bs[3*x+1][3*y+1] == bs[3*x+1][3*y+2]) and (bs[3*x+1][3*y] == ply):
            board.small_boards_status[k][x][y] = ply
            return True
        if (bs[3*x][3*y+1] == bs[3*x+1][3*y+1] == bs[3*x+2][3*y+1]) and (bs[3*x][3*y+1] == ply):
            board.small_boards_status[k][x][y] = ply
            return True
        if (bs[3*x+2][3*y] == bs[3*x+2][3*y+1] == bs[3*x+2][3*y+2]) and (bs[3*x+2][3*y] == ply):
            board.small_boards_status[k][x][y] = ply
            return True
        if (bs[3*x][3*y+2] == bs[3*x+1][3*y+2] == bs[3*x+2][3*y+2]) and (bs[3*x][3*y+2] == ply):
            board.small_boards_status[k][x][y] = ply
            return True

        if (bs[3*x][3*y] == bs[3*x+1][3*y+1] == bs[3*x+2][3*y+2]) and (bs[3*x][3*y] == ply):
            board.small_boards_status[k][x][y] = ply
            return True
        if (bs[3*x][3*y+2] == bs[3*x+1][3*y+1] == bs[3*x+2][3*y]) and (bs[3*x][3*y+2] == ply):
            board.small_boards_status[k][x][y] = ply
            return True

        if bs[3*x][3*y] =='-':
            return False
        if bs[3*x][3*y+1] =='-':
            return False
        if bs[3*x][3*y+2] =='-':
            return False
        if bs[3*x+1][3*y] =='-':
            return False
        if bs[3*x+1][3*y+1] =='-':
            return False
        if bs[3*x+1][3*y+2] =='-':
            return False
        if bs[3*x+2][3*y] =='-':
            return False
        if bs[3*x+2][3*y+1] =='-':
            return False
        if bs[3*x+2][3*y+2] =='-':
            return False
        board.small_boards_status[k][x][y] = 'd'
        return False

    # Calculate block score for heuristic
    def block_score(self, board, board_num, block_num, ply):
        b1 = block_num/3
        b2 = block_num%3

        # Return stored value if it already exists
        if (self.block_hash[board_num][b1][b2], ply) in self.block_store:
            return self.block_store[(self.block_hash[board_num][b1][b2], ply)]

        # We won the small board
        if board.small_boards_status[board_num][b1][b2] == ply:
            return self.score_block

        # We lost or drew the small board. Put it as 0 instead of a negative value
        # as we are going to subtract our attack score from opponent's attack score anyways
        elif board.small_boards_status[board_num][b1][b2] == self.opposite_flag(ply) or board.small_boards_status[board_num][b1][b2] == 'd':
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
            if lines[0] == 1:
                two_attacks += 1.0
            elif lines[0] == 2:
                one_attacks += 1.0
            if lines[1] == 1:
                two_attacks += 1.0
            elif lines[1] == 2:
                one_attacks += 1.0
            if lines[2] == 1:
                two_attacks += 1.0
            elif lines[2] == 2:
                one_attacks += 1.0
            if lines[3] == 1:
                two_attacks += 1.0
            elif lines[3] == 2:
                one_attacks += 1.0
            if lines[4] == 1:
                two_attacks += 1.0
            elif lines[4] == 2:
                one_attacks += 1.0
            if lines[5] == 1:
                two_attacks += 1.0
            elif lines[5] == 2:
                one_attacks += 1.0
            if lines[6] == 1:
                two_attacks += 1.0
            elif lines[6] == 2:
                one_attacks += 1.0
            if lines[7] == 1:
                two_attacks += 1.0
            elif lines[7] == 2:
                one_attacks += 1.0
            my_block_score = self.score1 * one_attacks + self.score2 * two_attacks
            self.block_store[(self.block_hash[board_num][b1][b2], ply)] = my_block_score
            return my_block_score

    # Calculate game score for heuristic
    def game_score(self, board, board_num, ply):
        # Get the block scores to use them as probabilites.
        my_block1 = self.block_score(board, board_num, 0, ply)
        my_block2 = self.block_score(board, board_num, 1, ply)
        my_block3 = self.block_score(board, board_num, 2, ply)
        my_block4 = self.block_score(board, board_num, 3, ply)
        my_block5 = self.block_score(board, board_num, 4, ply)
        my_block6 = self.block_score(board, board_num, 5, ply)
        my_block7 = self.block_score(board, board_num, 6, ply)
        my_block8 = self.block_score(board, board_num, 7, ply)
        my_block9 = self.block_score(board, board_num, 8, ply)

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
    def heuristic(self, board):
        if time() - self.start_time >= 21:
            return -1

        # Return stored value if it already exists
        if self.board_hash in self.heuristic_store:
            return self.heuristic_store[self.board_hash]

        # Get attack score for us and opponent by summing up block scores
        my_attack_score = 0
        my_attack_score += 4*(self.block_score(board, 0, 0, self.my_flag) + self.block_score(board, 1, 0, self.my_flag))
        my_attack_score += 6*(self.block_score(board, 0, 1, self.my_flag) + self.block_score(board, 1, 1, self.my_flag))
        my_attack_score += 4*(self.block_score(board, 0, 2, self.my_flag) + self.block_score(board, 1, 2, self.my_flag))
        my_attack_score += 6*(self.block_score(board, 0, 3, self.my_flag) + self.block_score(board, 1, 3, self.my_flag))
        my_attack_score += 3*(self.block_score(board, 0, 4, self.my_flag) + self.block_score(board, 1, 4, self.my_flag))
        my_attack_score += 6*(self.block_score(board, 0, 5, self.my_flag) + self.block_score(board, 1, 5, self.my_flag))
        my_attack_score += 4*(self.block_score(board, 0, 6, self.my_flag) + self.block_score(board, 1, 6, self.my_flag))
        my_attack_score += 6*(self.block_score(board, 0, 7, self.my_flag) + self.block_score(board, 1, 7, self.my_flag))
        my_attack_score += 4*(self.block_score(board, 0, 8, self.my_flag) + self.block_score(board, 1, 8, self.my_flag))

        if time() - self.start_time >= 21:
            return -1

        opp_attack_score = 0
        opp_attack_score += 4*(self.block_score(board, 0, 0, self.opp_flag) + self.block_score(board, 1, 0, self.opp_flag))
        opp_attack_score += 6*(self.block_score(board, 0, 1, self.opp_flag) + self.block_score(board, 1, 1, self.opp_flag))
        opp_attack_score += 4*(self.block_score(board, 0, 2, self.opp_flag) + self.block_score(board, 1, 2, self.opp_flag))
        opp_attack_score += 6*(self.block_score(board, 0, 3, self.opp_flag) + self.block_score(board, 1, 3, self.opp_flag))
        opp_attack_score += 3*(self.block_score(board, 0, 4, self.opp_flag) + self.block_score(board, 1, 4, self.opp_flag))
        opp_attack_score += 6*(self.block_score(board, 0, 5, self.opp_flag) + self.block_score(board, 1, 5, self.opp_flag))
        opp_attack_score += 4*(self.block_score(board, 0, 6, self.opp_flag) + self.block_score(board, 1, 6, self.opp_flag))
        opp_attack_score += 6*(self.block_score(board, 0, 7, self.opp_flag) + self.block_score(board, 1, 7, self.opp_flag))
        opp_attack_score += 4*(self.block_score(board, 0, 8, self.opp_flag) + self.block_score(board, 1, 8, self.opp_flag))

        if time() - self.start_time >= 21:
            return -1

        # Get game score from game_score function
        my_game_score = self.game_score(board, 0, self.my_flag) + self.game_score(board, 1, self.my_flag)
        if time() - self.start_time >= 21:
            return -1
        opp_game_score = self.game_score(board, 0, self.opp_flag) + self.game_score(board, 1, self.opp_flag)

        # Take weighted sum of attack score(how good the board is if we draw the game)
        # and game score(how good the board is for winning the game) to get the heuristic
        h = self.attack_weight * (my_attack_score - opp_attack_score) + self.game_weight * (my_game_score - opp_game_score)
        # x1 = my_attack_score - opp_attack_score
        # x2 = my_game_score - opp_game_score
        # h = self.c1 * x1 +  self.c2 * x2 +  self.c3 *  (x1 ** 2) + self.c4 * x1 * x2 + self.c5 *  (x2 ** 2)
        self.heuristic_store[self.board_hash] = h
        return h

    # Max player step of alpha beta search
    def max_value(self, board, alpha, beta, depth, old_move, bonus):
        self.count += 1
        if time() - self.start_time >= 21:
            return -1, (-1, -1, -1)

        # Return stored value if it already exists
        if (self.board_hash, old_move[1]%3, old_move[2]%3, 0) in self.ab_store:
            return self.ab_store[(self.board_hash, old_move[1]%3, old_move[2]%3, 0)]

        # Cutoff check: max depth or terminal state
        terminal_check = board.find_terminal_state()
        if time() - self.start_time >= 21:
            return -1, (-1, -1, -1)
        if terminal_check[1] == 'WON':
            if terminal_check[0] == self.my_flag:
                return self.win_utility, (-1, -1, -1)
            else:
                return self.lose_utility, (-1, -1, -1)
        elif terminal_check[1] == 'DRAW':
            return self.draw_utility, (-1, -1, -1)
        if depth == 0:
            return self.heuristic(board), (-1, -1, -1)

        best_utility = float("-inf")
        best_action = (-1, -1, -1)
        # Iterate through all possible actions
        for action in board.find_valid_move_cells(old_move):
            if time() - self.start_time >= 21:
                return -1, (-1, -1, -1)

            self.add_to_hash(action, 0)
            # Bonus move. Only if we won a small board and previous move was not our move
            if self.update(board, old_move, action, self.my_flag) and not bonus:
                utility, _ = self.max_value(board, alpha, beta, depth-1, action, True)
            else:
                utility, _ = self.min_value(board, alpha, beta, depth-1, action, False)

            if time() - self.start_time >= 21:
                return -1, (-1, -1, -1)

            # Undo board changes for the next iteration. This is an optimization
            board.big_boards_status[action[0]][action[1]][action[2]] = '-'
            board.small_boards_status[action[0]][action[1]/3][action[2]/3] = '-'
            self.add_to_hash(action, 0)

            # Bookkeeping
            if utility > best_utility:
                best_utility = utility
                best_action = action
            if best_utility >= beta:
                self.ab_store[(self.board_hash, old_move[1]%3, old_move[2]%3, 0)] = (best_utility, best_action)
                return best_utility, best_action
            alpha = max(alpha, best_utility)

        self.ab_store[(self.board_hash, old_move[1]%3, old_move[2]%3, 0)] = (best_utility, best_action)
        return best_utility, best_action

    # Min player step of alpha beta search
    def min_value(self, board, alpha, beta, depth, old_move, bonus):
        self.count += 1
        if time() - self.start_time >= 21:
            return -1, (-1, -1, -1)

        # Return stored value if it already exists
        if (self.board_hash, old_move[1]%3, old_move[2]%3, 1) in self.ab_store:
            return self.ab_store[(self.board_hash, old_move[1]%3, old_move[2]%3, 1)]

        # Cutoff check: max depth or terminal state
        terminal_check = board.find_terminal_state()
        if time() - self.start_time >= 21:
            return -1, (-1, -1, -1)
        if terminal_check[1] == 'WON':
            if terminal_check[0] == self.my_flag:
                return self.win_utility, (-1, -1, -1)
            else:
                return self.lose_utility, (-1, -1, -1)
        elif terminal_check[1] == 'DRAW':
            return self.draw_utility, (-1, -1, -1)
        if depth == 0:
            return self.heuristic(board), (-1, -1, -1)

        best_utility = float("inf")
        best_action = (-1, -1, -1)
        # Iterate through all possible actions
        for action in board.find_valid_move_cells(old_move):
            if time() - self.start_time >= 21:
                return -1, (-1, -1, -1)

            self.add_to_hash(action, 1)
            # Bonus move. Only if we won a small board and previous move was not our move
            if self.update(board, old_move, action, self.opp_flag) and not bonus:
                utility, _ = self.min_value(board, alpha, beta, depth-1, action, True)
            else:
                utility, _ = self.max_value(board, alpha, beta, depth-1, action, False)

            if time() - self.start_time >= 21:
                return float("-inf"), (-1, -1, -1)

            # Undo board changes for the next iteration. This is an optimization
            board.big_boards_status[action[0]][action[1]][action[2]] = '-'
            board.small_boards_status[action[0]][action[1]/3][action[2]/3] = '-'
            self.add_to_hash(action, 1)

            # Bookkeeping
            if utility < best_utility:
                best_utility = utility
                best_action = action
            if best_utility <= alpha:
                self.ab_store[(self.board_hash, old_move[1]%3, old_move[2]%3, 1)] = (best_utility, best_action)
                return best_utility, best_action
            beta = min(beta, best_utility)

        self.ab_store[(self.board_hash, old_move[1]%3, old_move[2]%3, 1)] = (best_utility, best_action)
        return best_utility, best_action

    # Alpha beta search
    def alpha_beta_search(self, board, depth, old_move):
        # If previous move was also ours(current move is a bonus move)
        if board.big_boards_status[old_move[0]][old_move[1]][old_move[2]] == self.my_flag:
            utility, action = self.max_value(board, float("-inf"), float("inf"), depth, old_move, True)
        else:
            utility, action = self.max_value(board, float("-inf"), float("inf"), depth, old_move, False)
        return utility, action

    # Returns the bot's move given board state
    def move(self, board, old_move, flag):
        # Note down the start time
        self.start_time = time()
        self.count = 0
        self.turns += 1
        # Note down our and our opponent's flags the first time this function is called
        if self.first:
            self.my_flag = flag
            self.opp_flag = self.opposite_flag(self.my_flag)
            self.first = False

        # Deepcopy the board so that we can update it
        board_copy = deepcopy(board)
        self.calculate_hashes(board_copy)
        self.ab_store = {}
        if self.turns % 20 == 0:
            self.heuristic_store = {}

        # Iterative deepening alpha beta search
        best_action = board_copy.find_valid_move_cells(old_move)[0]
        best_utility = float("-inf")
        depth = 3
        while True:
            utility, action = self.alpha_beta_search(board_copy, depth, old_move)
            # print utility, action
            # If alpha beta search was cut off due to time limit
            if time() - self.start_time >= 21:
                break
            best_action = action
            best_utility = utility
            if best_utility == self.win_utility:
                break
            depth += 2
            self.ab_store = {}

        # print "Bot 1", self.count
        return best_action
