###########################################
# you need to implement five funcitons here
###########################################

import Queue as Q
import copy
import numpy as np

'''
class sudokuGame to initialise game setup
'''
class sudokuGame():
    def __init__(self, filePath):
        self.game = readPuzzle(filePath)
        self.n = self.game[0]
        self.m = self.game[1]
        self.k = self.game[2]
        self.board = self.game[3]
        self.blanks = []
        self.checkConsistency = 0
        self.domain = {}
    '''
    Check if num is a legal value for the given row.
    '''
    def checkRow(self, row, num):
        n = self.n
        for col in range(n):
            v = self.board[row][col]
            if num == v:
                return False
        return True

    '''
    Check if num is a legal value for the given column.
    '''
    def checkColumn(self, col, num):
        n = self.n
        for row in range(n):
            v = self.board[row][col]
            if num == v:
                return False
        return True

    '''
    Check if num is a legal value for the box (one of 9 boxes) containing given row/col
    '''
    def checkSquare(self, row, col, num):
        m = self.m
        k = self.k
        row = (row / m) * m
        col = (col / k) * k
        for r in range(m):
            for c in range(k):
                if self.board[row + r][col + c] == num:
                    return False
        return True

    '''
    Check if num is legal
    '''
    def isSafe(self, row, col, num):
        n = self.n
        m = self.m
        k = self.k
        return (self.checkRow(row, num) and self.checkColumn(col, num) and self.checkSquare(row, col, num))

    '''
    Check full board condition
    '''
    def isFullBoard(self):
        n = self.n
        for i in range(n):
            for j in range(n):
                if (self.board[i][j] == 0):
                    return False
        return True

    '''
    Check for blank positions in board
    '''
    def getBlankCell(self):
        n = self.n
        empty = []
        for i in range(n):
            for j in range(n):
                if (self.board[i][j] == 0):
                    empty.append((i, j))
        return empty

    '''
    Evaluate the domain of a blank box
    '''
    def getPossibleValues(self, box):
        n = self.n
        row = box[0]
        col = box[1]
        possibilities = []
        for num in range(1, n + 1):
            if self.isSafe(row, col, num):
                possibilities.append(num)
        return possibilities

    '''
    Evaluate domain of all blank box
    '''
    def getDomain(self):
        blanks = self.getBlankCell()
        for box in blanks:
            possibilities = self.getPossibleValues(box)
            self.domain[box]=possibilities
        return self.domain

    '''
    Evaluate dependent cells in a row
    '''
    def getDepRows(self,row):
        n = self.n
        depRows = []
        for col in range(n):
            if self.board[row][col]==0:
                depRows.append((row,col))
        return depRows

    '''
    Evaluate dependent cells in a column
    '''
    def getDepCols(self,col):
        n = self.n
        depCols = []
        for row in range(n):
            if self.board[row][col]==0:
                depCols.append((row,col))
        return depCols

    '''
    Evaluate dependent cells in a MxK grid
    '''
    def getDepSquare(self,row,col):
        depSqaure = []
        m = self.m
        k = self.k
        row = (row / m) * m
        col = (col / k) * k
        for r in range(m):
            for c in range(k):
                if self.board[row + r][col + c] == 0:
                    depSqaure.append((row+r,col+c))
        return depSqaure

    '''
    Evaluate all dependent cells for a given cell
    '''
    def getDependents(self,box):
        row = box[0]
        col = box[1]
        dependents = []
        depBox = self.getDepRows(row)+self.getDepCols(col)+self.getDepSquare(row,col)
        for dbox in depBox:
            if dbox not in dependents and dbox != (row, col):
                dependents.append(dbox)
        return dependents

    '''
    Remove inconsistencies while checking AC-3 contraint propagation
    '''
    def deleteInconsistencies(self, head, tail):
        remove = False
        headDomain=copy.deepcopy(self.domain[head])
        for box in headDomain:
            tailDomain=copy.deepcopy(self.domain[tail])
            if box in tailDomain:
                tailDomain.remove(box)
            if len(tailDomain)==0:
                self.domain[head].remove(box)
                remove = True
        return remove

    '''
    Calculate total conflicts for a board configuration
    '''
    def calculateConflictVal(self):
        n= self.n
        totalConflicts = 0
        self.checkConsistency += 1
        for row in range(n):
            for col in range(n):
                if((row,col) in self.blanks):
                    num = self.board[row][col]
                    totalConflicts += self.getconflicts(row,col,num)
        return totalConflicts

    '''
    Calculate conflicts for a particular box
    '''
    def getconflicts(self,row,col,num):
        return self.getRowConflicts(row,col,num)+ self.getColConflicts(row,col,num)+ self.getSquareConflicts(row,col,num)

    '''
    Calculate conflicts for a box in a row
    '''
    def getRowConflicts(self,row,col,num):
        n = self.n
        rc =0
        for c in range(n):
            if((row,c) != (row,col)):
                if(self.board[row][c] == num):
                    rc +=1
        return (rc)

    '''
    Calculate conflicts for a box in a column
    '''
    def getColConflicts(self,row,col,num):
        n = self.n
        cc =0
        for r in range(n):
            if((r,col) != (row,col)):
                if(self.board[r][col] == num):
                    cc +=1
        return (cc)

    '''
    Calculate conflicts for a box in a MxK grid
    '''
    def getSquareConflicts(self,row,col,num):
        m = self.m
        k = self.k
        row_border = (row / m) * m
        col_border = (col / k) * k
        sc =0
        for r in range(m):
            for c in range(k):
                if((row_border + r,col_border + c) != (row,col)):
                    if self.board[row_border + r][col_border + c] == num:
                        sc +=1
        return (sc)

'''
Read the game.txt file and initialize sudoku board
'''
def readPuzzle(filename):
    # Reading file
    fileHandle = open(filename, 'r')
    arr = fileHandle.readline().strip().split(',')
    N = int(arr[0])
    M = int(arr[1].strip(';'))
    K = int(arr[2].strip(';'))

    rawState = [[0 for x in range(N)] for x in range(N)]

    for i in range(N):
        rawState[i] = fileHandle.readline().strip().split(',')

    for i in range(N):
        rawState[i][N - 1] = rawState[i][N - 1].strip(';')

    # updating game state with all 0
    Sudoku = [[0 for x in range(N)] for x in range(N)]

    # check for dimension of given board
    if len(rawState) != N:
        print "Wrong gameState given, check txt file 2"
        exit(0)
    else:
        for i in range(N):
            if len(rawState[i]) != N:
                print "Wrong gameState given, check txt file"
                exit(0)

    # update peg and corner positions
    for i in range(N):
        for j in range(N):
            if rawState[i][j] == '-' or rawState[i][j] == '-;':
                Sudoku[i][j] = 0
            else:
                Sudoku[i][j] = int(rawState[i][j])

    return (N, M, K, Sudoku)

'''
Method implementing backtracking
'''
def solveBoardBacktrack(sudokuObject, index):
    if (sudokuObject.isFullBoard()):
        return True
    else:
        n = sudokuObject.n
        row = sudokuObject.blanks[index][0]
        col = sudokuObject.blanks[index][1]
        for num in range(1, n + 1):
            if (sudokuObject.isSafe(row, col, num)):
                sudokuObject.checkConsistency +=1
                sudokuObject.board[row][col] = num
                if (solveBoardBacktrack(sudokuObject, index + 1)):
                    return True
        '''trigger backtracking'''
        sudokuObject.board[row][col] = 0
        return False

'''
Returns the cell having least domain value
'''
def getMRVList(sudokuBoardObject):
    q = Q.PriorityQueue()
    for box in sudokuBoardObject.blanks:
        possibilities = sudokuBoardObject.getPossibleValues(box)
        q.put((len(possibilities), box))
    p,b = q.get()
    return (b)

'''
Method implementing backtracking + MRV
'''
def solveBoardBacktrackMRV(sudokuObject):
    n = sudokuObject.n
    if (sudokuObject.isFullBoard()):
        return True
    else:
        emptyBox = getMRVList(sudokuObject)
        row = emptyBox[0]
        col = emptyBox[1]
        for num in range(1, n + 1):
            if (sudokuObject.isSafe(row, col, num)):
                sudokuObject.checkConsistency +=1
                sudokuObject.blanks.remove(emptyBox)
                sudokuObject.board[row][col] = num
                if (solveBoardBacktrackMRV(sudokuObject)):
                    return True
                sudokuObject.blanks.append(emptyBox)
        '''trigger backtracking'''
        sudokuObject.board[row][col] = 0
    return False

'''
Returns True if value chosen for a cell is consistent with the dependents of that cell
'''
def isConsistent(sudokuObject ,box,num):
    dependents = sudokuObject.getDependents(box)
    for dbox in dependents:
        domainbox = sudokuObject.domain[dbox]
        if num in domainbox:
            sudokuObject.domain[dbox].remove(num)
            if len(sudokuObject.domain[dbox])==0:
                return False
    return True

'''
Method implementing backtracking + MRV + Forward checking
'''
def solveBoardBacktrackMRVfwd(sudokuObject):
    n = sudokuObject.n
    if (sudokuObject.isFullBoard()):
        return True
    else:
        emptyBox = getMRVList(sudokuObject)
        row = emptyBox[0]
        col = emptyBox[1]
        domain = copy.deepcopy(sudokuObject.domain[emptyBox])

        for num in domain:
            tempdomain = copy.deepcopy(sudokuObject.domain)
            '''
            check consistency
            '''
            c = isConsistent(sudokuObject,emptyBox,num)
            if(c==True):
                sudokuObject.checkConsistency +=1
                sudokuObject.blanks.remove(emptyBox)
                sudokuObject.board[row][col] = num
                if(solveBoardBacktrackMRVfwd(sudokuObject)):
                    return True
                sudokuObject.blanks.append(emptyBox)
                sudokuObject.domain=tempdomain
        '''
        trigerrs backtracking
        '''
        sudokuObject.board[row][col] = 0
    return False

'''
Method for constraint propagation
'''
def constraintPropagate(sudokuObject):
    sudokuObject.checkConsistency +=1
    q = Q.Queue()
    for emptybox in sudokuObject.blanks:
        dbox = sudokuObject.getDependents(emptybox)
        for box in dbox:
            q.put((emptybox,box))
    while not q.empty():
        arc=q.get()
        head=arc[0]
        tail=arc[1]
        if sudokuObject.deleteInconsistencies(head,tail):
            dbox_head = sudokuObject.getDependents(head)
            dbox_head.remove(tail)
            for box in dbox_head:
                q.put((box,head))

'''
Method implementing Backtracking + MRV + Constraint Propagation
'''
def solveBoardBacktrackMRVcp(sudokuObject):
    if (sudokuObject.isFullBoard()):
        return True
    else:
        emptyBox = getMRVList(sudokuObject)
        row = emptyBox[0]
        col = emptyBox[1]
        domain = copy.deepcopy(sudokuObject.domain[emptyBox])

        for num in domain:
            tempdomain = copy.deepcopy(sudokuObject.domain)
            sudokuObject.domain[emptyBox]=[num]
            constraintPropagate(sudokuObject)
            sudokuObject.board[row][col] = num
            sudokuObject.blanks.remove(emptyBox)
            if solveBoardBacktrackMRVcp(sudokuObject):
                return True
            '''
            trigerrs backtracking
            '''
            sudokuObject.domain=tempdomain
            sudokuObject.blanks.append(emptyBox)
            sudokuObject.board[row][col]=0
    return False

'''
Initialize full board with random values in Min-Conflicts
'''
def fillInitialBoard(sudokuObject):
    n = sudokuObject.n
    items = []
    row = 0
    while row < n:
        a = []
        for col in range(n):
            if(sudokuObject.board[row][col] != 0):
                a.append(sudokuObject.board[row][col])
        for i in range(1,n+1):
            if(i not in a):
                items.append(i)
        np.random.shuffle(items)
        for col in range(n):
            x = sudokuObject.board[row][col]
            if(x == 0):
                sudokuObject.board[row][col]=items.pop()
        row +=1
    return sudokuObject.board

'''
Calls solveBoardBacktrack to solve puzzle
'''
def backtracking(filename):
    ###
    # use backtracking to solve sudoku puzzle here,
    # return the solution in the form of list of
    # list as describe in the PDF with # of consistency
    # checks done
    ###
    sudokuObject = sudokuGame(filename)
    sudokuObject.blanks = sudokuObject.getBlankCell()
    if (solveBoardBacktrack(sudokuObject, 0)):
        return (sudokuObject.board, sudokuObject.checkConsistency)
    else:
        print("No Solution")
        return ([], 0)

'''
Calls solveBoardBacktrackMRV to solve puzzle
'''
def backtrackingMRV(filename):
    ###
    # use backtracking + MRV to solve sudoku puzzle here,
    # return the solution in the form of list of
    # list as describe in the PDF with # of consistency
    # checks done
    ###
    sudokuObject = sudokuGame(filename)
    sudokuObject.blanks = sudokuObject.getBlankCell()
    if (solveBoardBacktrackMRV(sudokuObject)):
        return (sudokuObject.board, sudokuObject.checkConsistency)
    else:
        print("No Solution")
        return ([], 0)

'''
Calls solveBoardBacktrackMRVfwd to solve puzzle
'''
def backtrackingMRVfwd(filename):
    ###
    # use backtracking +MRV + forward propogation
    # to solve sudoku puzzle here,
    # return the solution in the form of list of
    # list as describe in the PDF with # of consistency
    # checks done
    ###

    sudokuObject = sudokuGame(filename)
    sudokuObject.blanks = sudokuObject.getBlankCell()
    sudokuObject.domain = sudokuObject.getDomain()
    #print(initDomain)

    if (solveBoardBacktrackMRVfwd(sudokuObject)):
        return (sudokuObject.board, sudokuObject.checkConsistency)
    else:
        print("No Solution")
        return ([], 0)

'''
Calls solveBoardBacktrackMRVcp to solve puzzle
'''
def backtrackingMRVcp(filename):
    ###
    # use backtracking + MRV + cp to solve sudoku puzzle here,
    # return the solution in the form of list of
    # list as describe in the PDF with # of consistency
    # checks done
    ###

    sudokuObject = sudokuGame(filename)
    sudokuObject.blanks = sudokuObject.getBlankCell()
    sudokuObject.domain = sudokuObject.getDomain()
    #print(initDomain)

    if (solveBoardBacktrackMRVcp(sudokuObject)):
        return (sudokuObject.board, sudokuObject.checkConsistency)
    else:
        print("No Solution")
        return ([], 0)

'''
Method to implement minConflict to solve puzzle
Returns true if total conflicts of board is zero
'''
def minConflict(filename):
    ###
    # use minConflict to solve sudoku puzzle here,
    # return the solution in the form of list of
    # list as describe in the PDF with # of consistency
    # checks done
    ###

    sudokuObject = sudokuGame(filename)
    sudokuObject.blanks = sudokuObject.getBlankCell()
    le = len(sudokuObject.blanks)
    n =sudokuObject.n
    '''
    Iterates for loop = 100000 times
    '''
    loop =0
    sudokuObject.board = fillInitialBoard(sudokuObject)
    while (loop <= 100000):
        count=sudokuObject.calculateConflictVal()
        if count==0:
            return (sudokuObject.board,sudokuObject.checkConsistency)

        num = row = col = -1
        while sudokuObject.getconflicts(row,col,num) <= 0:
            '''
            get random empty cell
            '''
            index=np.random.randint(le-1)
            box=sudokuObject.blanks[index]
            row=box[0]
            col=box[1]
            num=sudokuObject.board[row][col]

        min=10000
        for c in range(n):
            if((row,c) in sudokuObject.blanks and (row,c)!=(row,col)):
                a = sudokuObject.board[row][c]
                sudokuObject.board[row][c] = num
                x=sudokuObject.calculateConflictVal()
                if x==0:
                    return (sudokuObject.board,sudokuObject.checkConsistency)
                elif(x<min):
                    min=x
                    minbox=(row,c)
                    sudokuObject.board[row][c] = a
                else:
                    sudokuObject.board[row][c] = a
        if min!=10000:
            sudokuObject.board[minbox[0]][minbox[1]],sudokuObject.board[row][col] = sudokuObject.board[row][col], sudokuObject.board[minbox[0]][minbox[1]]

        loop +=1
    return ([],0)