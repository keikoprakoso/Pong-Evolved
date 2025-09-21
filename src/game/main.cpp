#include "Game.h"
#include <cstring>

int main(int argc, char* argv[]) {
    bool server = false;
    for (int i = 1; i < argc; ++i) {
        if (std::strcmp(argv[i], "--server") == 0) {
            server = true;
        }
    }
    Game game(server);
    game.run();
    return 0;
}