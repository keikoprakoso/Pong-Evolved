#pragma once

#include <SFML/Graphics.hpp>
#include <vector>
#include <string>
#include "Paddle.h"
#include "Ball.h"
#include "PowerUpManager.h"

class Game {
public:
    Game(bool serverMode = false);
    ~Game();
    void run();

private:
    void update(float dt);
    void render();
    void handleInput();
    void reset();
    void setBotAction(int action);
    std::string getStateJson();
    void serverLoop();
    void handleClient(int client_sock);

    sf::RenderWindow* window;
    Paddle playerPaddle, botPaddle;
    std::vector<Ball> balls;
    int playerScore, botScore;
    bool paused;
    sf::Clock clock;
    std::string title;
    PowerUpManager powerUpManager;
    bool serverMode;
    int botAction;
};