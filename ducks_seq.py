from typing import *
import random
from colorama import init, Fore
import math
init()

BOARD_SIZE = 14
temp_large = 128
NBITS = math.ceil(math.log2(128))

class State(NamedTuple):
    turn: bool
    board: int

def select(board: int, group_size: int):
    mask = ((1 << NBITS) - 1)
    return (board >> NBITS * (group_size - 1)) & mask

def set(board: int, group_size: int, count: int):
    mask = select(board, group_size) << NBITS * (group_size - 1)
    board ^= mask
    board |= count << NBITS * (group_size - 1)
    return board

def print_board(board: int):
    for i in range(1, BOARD_SIZE + 1):
        v = select(board, i)
        if v:
            print(("#"*i + " ")*v, end="")
        
    print()

def possible_moves(board: int):
    t = board
    i = 0
    while t:
        if t & 1:
            yield i,
            if t & 0b10:
                yield i, i + 1
        t >>= 1
        i += 1

def generate_boards(board: int):
    for size in range(1, BOARD_SIZE + 1):
        count = select(board, size)
        if count:
            """
            size 5
            01234
            partition   4
                    0 #----
                    1 -#--- 3
                    2 --#-- 2
                    3 ---#- (duplicate)
                    4 ----# (duplicate)
            
            """
            for partition in range(math.ceil(size / 2)):
                new_board = set(board, size, count - 1)
                if size > 1:
                    new_board = set(new_board, size - 1 - partition, select(new_board, size - 1 - partition) + 1)
                if partition > 0:
                    new_board = set(new_board, partition, select(new_board, partition) + 1)
                
                yield new_board
                # TODO: width 2 partitions
            
            """
            size 5
            01234
            partition   
                    0 ##---
                    1 -##--
                    2 --##- (duplicate)
                    3 ---## (duplicate)
                    4 ----# (impossible)
            
            """
            #print("s", size)

            # parititions with width 2:
            for partition in range(math.ceil((size - 1) / 2)):
                #print("p", partition)
                new_board = set(board, size, count - 1)
                if size > 2:
                    new_board = set(new_board, size - 2 - partition, select(new_board, size - 2 - partition) + 1)
                if partition > 0:
                    new_board = set(new_board, partition, select(new_board, partition) + 1)
                
                yield new_board


board = set(0, 5, 1)
print_board(board)
for possible in generate_boards(board):
    print_board(possible)


#exit()
    

""" def apply_move(board: int, move: Union[Tuple[int], Tuple[int, int]]):
    for i in move:
        board ^= 1 << i
    
    while board and board & 1 == 0:
        board >>= 1
    
    return board

def possible_boards(board: int):
    for move in possible_moves(board):
        yield apply_move(board, move) """

START = State(True, 0)

states = {START}

#for move in possible_moves(START.board):
#    print(move)

print(len(states))

"""

TODO: instead of constructing sets, use them to find unique, then construct a graph
 - this problem will be solved by traversing the graph of possible games
 - minimax algorithm at play?
 - branches with false end are wins

"""

""" while True:
    new_states = set()
    for state in states:
        for new_board in possible_boards(state.board):
            new_states.add(State(not state.turn, new_board))
    
    print(len(new_states))
    if len(new_states) == 1:
        break

    states = new_states """

def memoize(func):
    memo = {}
    def newfunc(*args):
        if args in memo:
            return memo[args]
    
        result = func(*args)
        memo[args] = result
        return result

    return newfunc

MY_TURN = True

# last player to make a move loses

def print_state(state: State):
    print(state.turn, end=" ")
    print_board(state.board)


memo = {}
def dfs(state: State):
    ones = select(state.board, 1)
    state = State(state.turn, set(state.board, 1, ones % 2))
    
    if state in memo:
        return memo[state]
    #ones = select(state.board, 1)
    #print("ones", ones)
    #state = State(state.turn, set(state.board, 1, ones % 2))
    #if ones % 2 == 1:
    #    print(state.turn, ones)
    #state = State(state.turn ^ (ones % 2 == 1), set(state.board, 1, 0))
    #if ones % 2 == 1:
    #    state.turn = not state.turn # odd number of 1s flips turn

    #print_state(state)
    if state.board == 0:
        #print(f"win? {state.turn == MY_TURN}", end=" ")
        #print_state(state)
        memo[state] = state.turn == MY_TURN
        return state.turn == MY_TURN # if its our turn on full board, we won
    
    any_losable = False
    for new_board in generate_boards(state.board):
        new_state = State(not state.turn, new_board)
        """ turn = not state.turn
        if ones % 2 == 1:
            turn = not turn
        new_state = State(turn, set(new_board, 1, 0))
        print("t:")
        print_board(state.board)
        print_board(new_board)
        print_board(new_state.board)
        print(state.turn, "->", new_state.turn) """
        winnable = dfs(new_state)
        # if it's my turn and there's a branch which wins
        if state.turn == MY_TURN and winnable:
            memo[state] = True
            return True
        else:
            if not winnable:
                any_losable = True
            
            if state.turn != MY_TURN and any_losable:
                memo[state] = False
                return False
    
    #print("illegal", any_losable)
    memo[state] = not any_losable
    return not any_losable

#print(dfs(State(True, set(0, 2, 1)))) # should be true
#print(dfs(State(True, set(0, 3, 1)))) # should be true
print("4 winnable?", dfs(State(True, set(0, 4, 1)))) # should be false
print("5 winnable?", dfs(State(True, set(0, 5, 1)))) # should be false
#print("Can always win from start?", dfs(State(True, set(0, BOARD_SIZE, 1))))
#exit()

import time
for i in range(2, 50):
    BOARD_SIZE = i
    #NBITS = math.ceil(math.log2(32))

    """ @memoize
    def dfs(state: State):
        #print_state(state)
        if state.board == 0:
            return state.turn == MY_TURN # if its our turn on full board, we won
        
        any_losable = False
        for new_board in possible_boards(state.board):
            winnable = dfs(State(1 if state.turn == 2 else 2, new_board))
            # if it's my turn and there's a branch which wins
            if state.turn == MY_TURN and winnable:
                return True
            else:
                if not winnable:
                    any_losable = True
                
                if state.turn != MY_TURN and any_losable:
                    return False
        
        return not any_losable """
    
    s = time.time()
    can_win = dfs(State(True, set(0, BOARD_SIZE, 1)))
    e = time.time()
    print(f"{BOARD_SIZE} Can always win from start? {can_win} {round(e - s, 2)}s")
    print("ST ", BOARD_SIZE)
    for board in generate_boards(set(0, BOARD_SIZE, 1)):
        if dfs(State(False, board)):
            print("   ", end="")
            for i in range(1, BOARD_SIZE + 1):
                v = select(board, i)
                if v:
                    print(" ".join([str(i)] * v), end=" ")
            print()

 


for i in range(BOARD_SIZE - 1, 0, -1):
    print(f"Can win with {BOARD_SIZE - i} blank?", dfs(State(True, (1 << i) - 1)))

def select_winning_move(board: int):
    turn = False
    winning_moves = []
    losing_moves = []
    for move in possible_moves(board):
        new_board = apply_move(board, move)
        win_guaranteed = dfs(State(turn, new_board))
        if win_guaranteed:
            winning_moves.append(move)
        else:
            losing_moves.append(move)

    print("Winning moves:", len(winning_moves))
    print("    ", "  ".join(str(move) for move in winning_moves))
    print("Losing moves:", len(losing_moves))
    if winning_moves:
        return random.choice(winning_moves)
    
    return random.choice(losing_moves)


def computer_move(board: int):
    # computer is turn 1
    move = select_winning_move(board)
    print(move)
    board = apply_move(board, move)
    return board

def human_move(board: int):
    human_move = ()
    while len(human_move) == 0 or len(human_move) > 2 or (len(human_move) == 2 and abs(human_move[0] - human_move[1]) != 1) or any((board & (1 << move) != 0 or move < 0 or move > BOARD_SIZE - 1 for move in human_move)):
        human_move = tuple(int(n) for n in input("> ").split(","))

    print(human_move)
    board = apply_move(board, human_move)
    return board

def computer_starts():
    board = 0
    while board != (1 << BOARD_SIZE) - 1:
        turn = True
        print(Fore.BLUE, end="")
        print("COMPUTER:")
        board = computer_move(board)
        print_board(board)
        print(Fore.RESET, end="")

        turn = False
        print("HUMAN:")
        board = human_move(board)
        
        print_board(board)
    
    if turn == True:
        print("Computer wins!")
    else:
        print("Human wins!")


def human_start():
    board = 0b0000000000000
    while board != (1 << BOARD_SIZE) - 1:
        turn = True
        print("HUMAN:")
        computer_move(board)
        print()
        board = human_move(board)
        print_board(board)

        if board == (1 << BOARD_SIZE) - 1:
            break
 
        print(Fore.BLUE, end="")
        print("COMPUTER:")
        turn = False
        board = computer_move(board)

        print_board(board)
        print("\n")
        print(Fore.RESET, end="")
    
    if turn == True:
        print("Computer wins!")
    else:
        print("Human wins!")


#computer_starts()
human_start()

# TODO: store sequence of streaks instead of bitfield