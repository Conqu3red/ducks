#include <stdio.h>
#include <math.h>
#include <stdint.h>
#include <unordered_map>
#include <chrono>

namespace Game {
    static uint64_t BOARD_SIZE;
    static uint64_t NBITS = 8;

struct State {
    uint8_t turn;
    union {
        uint64_t board[10];
        uint8_t board8[80];
    } b;

    bool operator==(const State &o) const {
        return turn == o.turn && (
            b.board[0] == o.b.board[0] &&
            b.board[1] == o.b.board[1] &&
            b.board[2] == o.b.board[2] &&
            b.board[3] == o.b.board[3] &&
            b.board[4] == o.b.board[4] &&
            b.board[5] == o.b.board[5] &&
            b.board[6] == o.b.board[6] &&
            b.board[7] == o.b.board[7] &&
            b.board[8] == o.b.board[8] &&
            b.board[9] == o.b.board[9]);
    }

    bool zero() const {
        return (
            b.board[0] |
            b.board[1] |
            b.board[2] |
            b.board[3] |
            b.board[4] |
            b.board[5] |
            b.board[6] |
            b.board[7] |
            b.board[8] |
            b.board[9]
        ) == 0;
    }

    uint8_t select(uint64_t group_size) {
        return b.board8[group_size - 1];
    }

    void set(uint64_t group_size, uint8_t count) {
        b.board8[group_size - 1] = count;
    }

    void print() {
        for (uint64_t i = 1; i <= BOARD_SIZE; i++) {
            auto v = select(i);
            if (v > 0) {
                for (uint64_t j = 0; j < v; j++) {
                    for (uint64_t k = 0; k < i; k++) {
                        printf("-");
                    }
                    printf("#");
                }
            }
        }
        printf("\n");
    }
};

struct hash_fn {
    size_t operator()(const State &state) const {
        return (state.turn & 1)
            ^ state.b.board[0] << 1
            ^ state.b.board[1] << 1
            ^ state.b.board[2] << 1
            ^ state.b.board[3] << 1
            ^ state.b.board[4] << 1
            ^ state.b.board[5] << 1
            ^ state.b.board[6] << 1
            ^ state.b.board[7] << 1
            ^ state.b.board[8] << 1
            ^ state.b.board[9] << 1; // TODO: is this good enough?
    }
};

/* uint8_t select(uint8_t board[64], uint64_t group_size) {
    return board[group_size - 1];
}

void set(uint8_t board[64], uint64_t group_size, uint8_t count) {
    board[group_size - 1] = count;
}

void print_board(uint8_t board[64]) {
    for (uint64_t i = 1; i <= BOARD_SIZE; i++) {
        auto v = select(board, i);
        if (v > 0) {
            for (uint64_t j = 0; j < v; j++) {
                for (uint64_t k = 0; k < i; k++) {
                    printf("-");
                }
                printf("#");
            }
        }
    }
    printf("\n");
} */


struct search {
    std::unordered_map<State, bool, hash_fn> cache = {};

    bool MY_TURN = true;

    bool guarantee_win(State state) {
        auto ones = state.select(1);
        state.set(1, ones % 2);

        auto cached = cache.find(state);
        if (cached != cache.end()) {
            //printf("cached\n");
            //return std::get<1>(*cached);
            return cache[state];
        }

        /* print_board(state.board);
        printf("\n"); */

        if (state.zero()) return state.turn == MY_TURN;

        bool any_losable = false;

        for (uint64_t size = 1; size <= BOARD_SIZE; size++) {
            auto count = state.select(size);
            if (count > 0) {
                for (uint64_t cut_width = 1; cut_width <= 2; cut_width++) {
                    for (uint64_t partition = 0; partition < ceil((size - cut_width + 1) / 2.0); partition++) {
                        
                        // 1-wide partitions
                        auto new_state = state;
                        new_state.turn = !state.turn;
                        new_state.set(size, count - 1);
                        if (size > cut_width) new_state.set(size - cut_width - partition, new_state.select(size - cut_width - partition) + 1);
                        if (partition > 0) new_state.set(partition, new_state.select(partition) + 1);
                    
                        bool guaranteed = guarantee_win(new_state);
                        if (state.turn == MY_TURN && guaranteed) {
                            cache[state] = true;
                            return true;
                        }
                        if (state.turn != MY_TURN && !guaranteed) {
                            cache[state] = false;
                            return false;
                        }
                        if (!guaranteed) any_losable = true;
                    }
                }
            }    
        }

        /*
        uint64_t temp_board = state.board;
        uint32_t i = 0;
        while (temp_board) {
            if (temp_board & 1) {
                uint64_t b = state.board ^ (1 << i);
                while (b && !(b & 1)) b >>= 1;

                State new_state = {!state.turn, b};
                
                bool guaranteed = guarantee_win(new_state);
                if (state.turn == MY_TURN && guaranteed) {
                    cache[state] = true;
                    return true;
                }
                if (state.turn != MY_TURN && !guaranteed) {
                    cache[state] = false;
                    return false;
                }
                if (!guaranteed) any_losable = true;
                // Case if adjacent is also set
                if (temp_board & 0b10) {
                    b = (state.board ^ (1 << i)) ^ (1 << (i + 1));
                    while (b && !(b & 1)) b >>= 1;
                    new_state = {!state.turn, b};
                    bool guaranteed2 = guarantee_win(new_state);

                    if (state.turn == MY_TURN && guaranteed2) {
                        cache[state] = true;
                        return true;
                    }
                    if (state.turn != MY_TURN && !guaranteed2) {
                        cache[state] = false;
                        return false;
                    }
                    if (!guaranteed2) any_losable = true;
                }
            }
            temp_board >>= 1;
            i++;
        }
        */

        cache[state] = !any_losable;
        return !any_losable;
    }
};

}

int main() {
    Game::search s;
    for (uint64_t w = 1; w <= 80; w++) {
        Game::BOARD_SIZE = w;
        Game::State state = {true, {0, 0, 0, 0, 0, 0, 0, 0, 0, 0}};
        state.set(w, 1);
        //state.print();
        //break;

        auto start = std::chrono::high_resolution_clock::now();
        bool result = s.guarantee_win(state);
        auto end = std::chrono::high_resolution_clock::now();

        auto ms_int = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

        printf("can guarantee win with %d? %d in %dms   (cache:%d)\n", w, result, ms_int, s.cache.size());
    }

    return 0;
}