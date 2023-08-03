from typing import *
import random
from colorama import init, Fore
import math
init()

BOARD_SIZE = 14

class State(NamedTuple):
    turn: bool
    board: int

def print_board(board: int):
    t = board
    i = 0
    while t:
        print(i % 10, end="")
        i += 1
        t >>= 1
    print()

    t = board
    while t:
        print(t & 1, end="")
        t >>= 1
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
    

def apply_move(board: int, move: Union[Tuple[int], Tuple[int, int]]):
    for i in move:
        board ^= 1 << i
    
    while board and board & 1 == 0:
        board >>= 1
    
    return board

def possible_boards(board: int):
    for move in possible_moves(board):
        yield apply_move(board, move)

START = State(True, (1 << BOARD_SIZE) - 1)

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

@memoize
def dfs(state: State):
    #print_state(state)
    if state.board == 0:
        #print(f"win? {state.turn == MY_TURN}", end=" ")
        #print_state(state)
        return state.turn == MY_TURN # if its our turn on full board, we won
    
    any_losable = False
    for new_board in possible_boards(state.board):
        winnable = dfs(State(not state.turn, new_board))
        # if it's my turn and there's a branch which wins
        if state.turn == MY_TURN and winnable:
            return True
        else:
            if not winnable:
                any_losable = True
            
            if state.turn != MY_TURN and any_losable:
                return False
    
    #print("illegal", any_losable)
    return not any_losable

print(dfs(State(True, 0b11))) # should be true
print(dfs(State(True, 0b111))) # should be true
print("4 winnable?", dfs(State(1, 0b1111))) # should be false
print("Can always win from start?", dfs(State(True, (1 << BOARD_SIZE) - 1)))

import time
for i in range(2, 50):
    BOARD_SIZE = i

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
    can_win = dfs(State(True, (1 << BOARD_SIZE) - 1))
    e = time.time()
    print(f"{BOARD_SIZE} Can always win from start? {can_win} {round(e - s, 2)}s")

 


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