from typing import *
import random
from colorama import init, Fore
init()

BOARD_SIZE = 14

class State(NamedTuple):
    turn: int
    board: int

def print_board(board: int):
    for i in range(0, BOARD_SIZE):
        print(i % 10, end="")
    print()

    for i in range(0, BOARD_SIZE):
        print(int(board & (1 << i) != 0), end="")
    print()

def possible_moves(board: int):
    for i in range(0, BOARD_SIZE):
        if board & (1 << i) == 0:
            yield i,
            if i < BOARD_SIZE - 1 and board & (1 << i + 1) == 0:
                yield i, i + 1
    

def apply_move(board: int, move: Union[Tuple[int], Tuple[int, int]]):
    for i in move:
        board |= 1 << i
    
    """ if board & 1:
        board >>= 1
        board |= 1 << BOARD_SIZE - 1 """
    
    return board

def possible_boards(board: int):
    for move in possible_moves(board):
        yield apply_move(board, move)

START = State(1, 0)

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

MY_TURN = 1

# last player to make a move loses

def print_state(state: State):
    print(state.turn, end=" ")
    print_board(state.board)

@memoize
def dfs(state: State):
    #print_state(state)
    if state.board == (1 << BOARD_SIZE) - 1:
        """ print(f"win? {state.turn == MY_TURN}", end=" ")
        print_state(state) """
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
    
    return not any_losable

print(dfs(State(2, 0b11111111111100))) # should be false
print("Can always win from start?", dfs(State(1, 0)))


""" for i in range(2, 50):
    BOARD_SIZE = i

    @memoize
    def dfs(state: State):
        #print_state(state)
        if state.board == (1 << BOARD_SIZE) - 1:
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
        
        return not any_losable

    print(f"{BOARD_SIZE} Can always win from start?", dfs(State(1, 0)))
 """


for i in range(BOARD_SIZE - 1, 0, -1):
    print(f"Can win with {BOARD_SIZE - i} blank?", dfs(State(1, (1 << i) - 1)))

def select_winning_move(board: int):
    turn = 2
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
        turn = 1
        print(Fore.BLUE, end="")
        print("COMPUTER:")
        board = computer_move(board)
        print_board(board)
        print(Fore.RESET, end="")

        turn = 2
        print("HUMAN:")
        board = human_move(board)
        
        print_board(board)
    
    if turn == 2:
        print("Computer wins!")
    else:
        print("Human wins!")


def human_start():
    board = 0b0000000000000
    while board != (1 << BOARD_SIZE) - 1:
        turn = 2
        print("HUMAN:")
        computer_move(board)
        print()
        board = human_move(board)
        print_board(board)

        if board == (1 << BOARD_SIZE) - 1:
            break
 
        print(Fore.BLUE, end="")
        print("COMPUTER:")
        turn = 1
        board = computer_move(board)

        print_board(board)
        print("\n")
        print(Fore.RESET, end="")
    
    if turn == 2:
        print("Computer wins!")
    else:
        print("Human wins!")


#computer_starts()
human_start()