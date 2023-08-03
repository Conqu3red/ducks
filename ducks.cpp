#include <stdio.h>
#include <stdint.h>
#include <unordered_map>
#include <chrono>

struct State {
    uint8_t turn;
    uint64_t board;

    bool operator==(const State &o) const {
        return turn == o.turn && board == o.board;
    }
};

struct hash_fn {
    size_t operator()(const State &state) const {
        return (state.board << 1) ^ (state.turn & 1);
    }
};

void print_board(uint64_t board) {
    uint64_t b = board;
    uint64_t i = 0;
    while (b) {
        printf("%d", i % 10);
        b >>= 1;
        i++;
    }
    printf("\n");
    while (board) {
        printf("%d", board & 1);
        board >>= 1;
    }
    printf("\n");
}


struct search {
    std::unordered_map<State, bool, hash_fn> cache = {};

    bool MY_TURN = true;

    bool guarantee_win(State state) {
        auto cached = cache.find(state);
        if (cached != cache.end()) {
            //printf("cached\n");
            //return std::get<1>(*cached);
            return cache[state];
        }

        /* print_board(state.board);
        printf("\n"); */

        if (state.board == 0) return state.turn == MY_TURN;

        bool any_losable = false;
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

        cache[state] = !any_losable;
        return !any_losable;
    }
};


int main() {
    search s;
    for (uint64_t w = 0; w < 50; w++) {
        State state = {true, (1ULL << w) - 1};

        auto start = std::chrono::high_resolution_clock::now();
        bool result = s.guarantee_win(state);
        auto end = std::chrono::high_resolution_clock::now();

        auto ms_int = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

        printf("can guarantee win with %d? %d in %dms   (cache:%d)\n", w, result, ms_int, s.cache.size());
    }

    return 0;
}