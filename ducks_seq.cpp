#include <stdio.h>
#include <math.h>
#include <stdint.h>
#include <unordered_map>
#include <chrono>
#include "robin_hood.h"

namespace Game {
    static uint64_t BOARD_SIZE;
    static uint64_t NBITS = 8;

struct State {
    uint8_t turn;
    union {
        uint64_t board[8];
        uint8_t board8[64];
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
            b.board[7] == o.b.board[7]);
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
            b.board[7]
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

// https://stackoverflow.com/questions/19195183/how-to-properly-hash-the-custom-struct
template <class T>
inline void hash_combine(std::size_t & s, const T & v)
{
  std::hash<T> h;
  s^= h(v) + 0x9e3779b9 + (s<< 6) + (s>> 2);
}

struct hash_fn {
    size_t operator()(const State &state) const {
        std::size_t res = 0;
        hash_combine(res, state.turn & 1);
        hash_combine(res, state.b.board[0]);
        hash_combine(res, state.b.board[1]);
        hash_combine(res, state.b.board[2]);
        hash_combine(res, state.b.board[3]);
        hash_combine(res, state.b.board[4]);
        hash_combine(res, state.b.board[5]);
        hash_combine(res, state.b.board[6]);
        hash_combine(res, state.b.board[7]);
        hash_combine(res, state.b.board[8]);
        hash_combine(res, state.b.board[9]); // TODO: is this good enough?
        return res;
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
    robin_hood::unordered_flat_map<State, bool, hash_fn> cache = robin_hood::unordered_flat_map<State, bool, hash_fn>(4000000ULL);

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
        
        cache[state] = !any_losable;
        return !any_losable;
    }
};

}

int main() {
    Game::search s;
    for (uint64_t w = 1; w <= 64; w++) {
        Game::BOARD_SIZE = w;
        Game::State state = {true, {0, 0, 0, 0, 0, 0, 0, 0}};
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