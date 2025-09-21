#pragma once

#include "PowerUp.h"
#include "Paddle.h"
#include "Ball.h"
#include <vector>
#include <map>

struct ActiveEffect {
    PowerUpType type;
    float timeLeft;
};

class PowerUpManager {
public:
    PowerUpManager();
    void update(float dt, const std::vector<Ball>& balls, Paddle& playerPaddle, std::vector<Ball>& ballsRef);
    void draw(sf::RenderWindow& window);
    const std::vector<ActiveEffect>& getActiveEffects() const;

private:
    void spawnPowerUp(PowerUpType type);
    void applyEffect(PowerUpType type, Paddle& playerPaddle, std::vector<Ball>& balls);
    void revertEffect(PowerUpType type, Paddle& playerPaddle, std::vector<Ball>& balls);

    std::vector<PowerUp> powerUps;
    std::vector<ActiveEffect> activeEffects;
    std::map<PowerUpType, float> spawnTimers;
    std::map<PowerUpType, float> durations;
    std::map<PowerUpType, float> spawnIntervals;
};