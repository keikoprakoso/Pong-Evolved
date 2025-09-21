#include "Game.h"
#include <cmath>
#include <iostream>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>

const float fixedDt = 1.0f / 60.0f;

Game::Game(bool sm) : window(nullptr), playerPaddle(true), botPaddle(false), playerScore(0), botScore(0), paused(false), serverMode(sm), botAction(1) {
    // Constructor: initialize window, paddles, balls, scores, paused state
    balls.emplace_back();  // Start with one ball
    if (!serverMode) {
        window = new sf::RenderWindow(sf::VideoMode({800, 600}), "Pong Evolved");
    }
    title = "Pong Evolved";
}

Game::~Game() {
    if (window) delete window;
}

void Game::run() {
    if (!serverMode) {
        // Windowed mode
        while (window->isOpen()) {
            handleInput();
            if (!paused) {
                float dt = clock.restart().asSeconds();
                static float accumulator = 0.0f;
                accumulator += dt;
                while (accumulator >= fixedDt) {
                    update(fixedDt);
                    accumulator -= fixedDt;
                }
            } else {
                clock.restart();
            }
            render();
        }
    } else {
        // Server mode
        serverLoop();
    }
}

void Game::handleInput() {
    if (!window) return;
    // Handle window events and pause key
    while (auto event = window->pollEvent()) {
        if (event->is<sf::Event::Closed>()) {
            window->close();
        }
        if (event->is<sf::Event::KeyPressed>()) {
            auto keyEvent = event->getIf<sf::Event::KeyPressed>();
            if (keyEvent->code == sf::Keyboard::Key::P) {
                paused = !paused;
            }
        }
    }
}

void Game::update(float dt) {
    // Update game state: paddles, ball, collisions, scoring
    // Player paddle movement
    if (sf::Keyboard::isKeyPressed(sf::Keyboard::Key::W) || sf::Keyboard::isKeyPressed(sf::Keyboard::Key::Up)) {
        playerPaddle.moveUp(dt);
    }
    if (sf::Keyboard::isKeyPressed(sf::Keyboard::Key::S) || sf::Keyboard::isKeyPressed(sf::Keyboard::Key::Down)) {
        playerPaddle.moveDown(dt);
    }

    if (!serverMode && !balls.empty()) {
        // Internal bot logic
        float ballY = balls[0].getPosition().y;
        float botY = botPaddle.getPosition().y;
        float diff = ballY - botY;
        float maxSpeed = 400.0f;
        if (std::abs(diff) > 10.0f) {
            float moveAmount = std::min(maxSpeed * dt, std::abs(diff));
            if (diff > 0) {
                botPaddle.shape.move({0, moveAmount});
                if (botPaddle.shape.getPosition().y + botPaddle.shape.getSize().y > 600) {
                    botPaddle.shape.setPosition({botPaddle.shape.getPosition().x, 600 - botPaddle.shape.getSize().y});
                }
            } else {
                botPaddle.shape.move({0, -moveAmount});
                if (botPaddle.shape.getPosition().y < 0) {
                    botPaddle.shape.setPosition({botPaddle.shape.getPosition().x, 0});
                }
            }
        }
    } else {
        // Use botAction from AI
        if (botAction == -1) {
            botPaddle.moveDown(dt);
        } else if (botAction == 1) {
            botPaddle.moveUp(dt);
        }
    }

    // Update ball physics
    for (auto& ball : balls) {
        ball.update(dt);
    }

    // Paddle collisions
    for (auto& ball : balls) {
        if (ball.getBounds().findIntersection(playerPaddle.getBounds())) {
            ball.bounceX();
        }
        if (ball.getBounds().findIntersection(botPaddle.getBounds())) {
            ball.bounceX();
        }
    }

    // Paddle extend update
    if (playerPaddle.extended) {
        playerPaddle.extendTimeLeft -= dt;
        if (playerPaddle.extendTimeLeft <= 0) {
            playerPaddle.extended = false;
            playerPaddle.shape.setSize(playerPaddle.originalSize);
        }
    }

    // Power-up manager update
    powerUpManager.update(dt, balls, playerPaddle, balls);

    // Scoring and reset
    for (auto& ball : balls) {
        if (ball.getPosition().x < 0) {
            botScore++;
            reset();
            break;
        } else if (ball.getPosition().x > 800) {
            playerScore++;
            reset();
            break;
        }
    }
}

void Game::render() {
    if (!window) return;
    // Render game objects
    window->clear(sf::Color::Black);
    playerPaddle.draw(*window);
    botPaddle.draw(*window);
    for (auto& ball : balls) {
        ball.draw(*window);
    }
    powerUpManager.draw(*window);
    // UI indicators for active power-ups
    int y = 10;
    for (const auto& effect : powerUpManager.getActiveEffects()) {
        sf::RectangleShape indicator({20, 20});
        if (effect.type == PowerUpType::ExtendPaddle) {
            indicator.setFillColor(sf::Color::Green);
        } else if (effect.type == PowerUpType::SlowMotion) {
            indicator.setFillColor(sf::Color::Yellow);
        }
        indicator.setPosition({760.0f, static_cast<float>(y)});
        window->draw(indicator);
        y += 25;
    }
    // HUD for scores skipped (no assets)
    // Fix: Check if window has focus; if not, update title to prompt user to click for controls
    if (!window->hasFocus()) {
        window->setTitle(title + " - Click to focus for controls");
    } else {
        window->setTitle(title);
    }
    window->display();
}

void Game::reset() {
    // Reset positions after scoring
    balls.clear();
    balls.emplace_back();  // Reset to one ball
    playerPaddle.reset();
    botPaddle.reset();
    // Output scores to console (since no HUD assets)
    std::cout << "Score: Player " << playerScore << " - Bot " << botScore << std::endl;
}

void Game::setBotAction(int action) {
    botAction = action;
}

std::string Game::getStateJson() {
    std::string stateJson = "{";
    stateJson += "\"balls\":[";
    for (size_t i = 0; i < balls.size(); ++i) {
        auto& ball = balls[i];
        sf::Vector2f pos = ball.getPosition();
        stateJson += "{\"x\":" + std::to_string(pos.x) + ",\"y\":" + std::to_string(pos.y) + ",\"vx\":" + std::to_string(ball.velocity.x) + ",\"vy\":" + std::to_string(ball.velocity.y) + "}";
        if (i < balls.size() - 1) stateJson += ",";
    }
    stateJson += "],";
    sf::Vector2f ppos = playerPaddle.getPosition();
    stateJson += "\"player_paddle\":{\"x\":" + std::to_string(ppos.x) + ",\"y\":" + std::to_string(ppos.y) + ",\"width\":" + std::to_string(playerPaddle.shape.getSize().x) + ",\"height\":" + std::to_string(playerPaddle.shape.getSize().y) + "},";
    sf::Vector2f bpos = botPaddle.getPosition();
    stateJson += "\"bot_paddle\":{\"x\":" + std::to_string(bpos.x) + ",\"y\":" + std::to_string(bpos.y) + ",\"width\":" + std::to_string(botPaddle.shape.getSize().x) + ",\"height\":" + std::to_string(botPaddle.shape.getSize().y) + "},";
    stateJson += "\"scores\":{\"player\":" + std::to_string(playerScore) + ",\"bot\":" + std::to_string(botScore) + "},";
    stateJson += "\"power_ups\":[],";
    stateJson += "\"active_effects\":[]";
    stateJson += "}";

    // Wrap in message format expected by Python client
    std::string messageJson = "{\"data\":" + stateJson + "}";
    return messageJson;
}

void Game::serverLoop() {
    int server_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (server_sock == -1) {
        std::cerr << "Failed to create socket\n";
        return;
    }
    sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(6000);
    addr.sin_addr.s_addr = INADDR_ANY;
    if (bind(server_sock, (sockaddr*)&addr, sizeof(addr)) == -1) {
        std::cerr << "Bind failed\n";
        close(server_sock);
        return;
    }
    if (listen(server_sock, 1) == -1) {
        std::cerr << "Listen failed\n";
        close(server_sock);
        return;
    }
    std::cout << "Server started, waiting for clients on port 6000...\n";
    while (true) {
        sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        int client_sock = accept(server_sock, (sockaddr*)&client_addr, &client_len);
        if (client_sock == -1) {
            std::cerr << "Accept failed\n";
            continue;
        }
        std::cout << "Client connected.\n";
        handleClient(client_sock);
        close(client_sock);
        std::cout << "Client disconnected, waiting for next client...\n";
    }
    close(server_sock);
}

void Game::handleClient(int client_sock) {
    float accumulator = 0.0f;
    while (true) {
        std::string state = getStateJson();
        ssize_t sent = send(client_sock, (state + "\n").c_str(), state.size() + 1, 0);
        if (sent == -1) {
            std::cerr << "Send failed\n";
            break;
        }
        char buffer[4096];
        int len = recv(client_sock, buffer, sizeof(buffer) - 1, 0);
        if (len > 0) {
            buffer[len] = '\0';
            std::string msg(buffer);
            size_t pos = msg.find("\"action\":");
            if (pos != std::string::npos) {
                size_t start = pos + 10;
                size_t end = msg.find_first_of(",}", start);
                try {
                    int action = std::stoi(msg.substr(start, end - start));
                    setBotAction(action);
                } catch (const std::exception& e) {
                    std::cerr << "Invalid action JSON: " << e.what() << "\n";
                }
            }
        } else if (len == 0) {
            // Client disconnected
            break;
        } else {
            std::cerr << "Recv error\n";
            break;
        }
        float dt = clock.restart().asSeconds();
        accumulator += dt;
        while (accumulator >= fixedDt) {
            update(fixedDt);
            accumulator -= fixedDt;
        }
        usleep(16000);
    }
}