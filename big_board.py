class BigBoard:

    def __init__(self):
		# big_boards_status is the game board
		# small_boards_status shows which small_boards have been won/drawn and by which player
        self.big_boards_status = ([['-' for i in range(9)] for j in range(9)], [['-' for i in range(9)] for j in range(9)])
        self.small_boards_status = ([['-' for i in range(3)] for j in range(3)], [['-' for i in range(3)] for j in range(3)])
        self.old_move = (-1, -1, -1)

	def GetResult(self, playerjm):
		#checks if the game is over(won or drawn) and returns the player who have won the game or the player who has higher small_boards in case of a draw

		cntx = 0
		cnto = 0
		cntd = 0

        for k in xrange(2):
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


    # changed update
	def DoMove(self, new_move, ply):
		#updating the game board and small_board status as per the move that has been passed in the arguements
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
				return 'SUCCESSFUL', True
			#checking for vertical pattern(i'th column)
			if (bs[3*x][3*y+i] == bs[3*x+1][3*y+i] == bs[3*x+2][3*y+i]) and (bs[3*x][3*y+i] == ply):
				self.small_boards_status[k][x][y] = ply
				return 'SUCCESSFUL', True
		#checking for diagonal patterns
		#diagonal 1
		if (bs[3*x][3*y] == bs[3*x+1][3*y+1] == bs[3*x+2][3*y+2]) and (bs[3*x][3*y] == ply):
			self.small_boards_status[k][x][y] = ply
			return 'SUCCESSFUL', True
		#diagonal 2
		if (bs[3*x][3*y+2] == bs[3*x+1][3*y+1] == bs[3*x+2][3*y]) and (bs[3*x][3*y+2] == ply):
			self.small_boards_status[k][x][y] = ply
			return 'SUCCESSFUL', True
		#checking if a small_board has any more cells left or has it been drawn
		for i in range(3):
			for j in range(3):
				if bs[3*x+i][3*y+j] =='-':
					return 'SUCCESSFUL', False
		self.small_boards_status[k][x][y] = 'd'
		return 'SUCCESSFUL', False

	def __repr__(self):
		# for printing the state of the board
		print '================BigBoard State================'
		for i in range(9):
			if i%3 == 0:
				print
			for k in range(2):
				for j in range(9):
					if j%3 == 0:
						print "",
					print self.big_boards_status[k][i][j],
				if k==0:
					print "   ",
			print
		print

		print '==============SmallBoards States=============='
		for i in range(3):
			for k in range(2):
				for j in range(3):
					print self.small_boards_status[k][i][j],
				if k==0:
					print "  ",
			print
		print '=============================================='
		print
		print
