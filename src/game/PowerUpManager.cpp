#include "PowerUpManager.h"
#include <cstdlib>

PowerUpManager::PowerUpManager() {
    // Hardcode config values
    durations[PowerUpType::ExtendPaddle] = 10.0f;
    durations[PowerUpType::SplitBall] = 0.0f;
    durations[PowerUpType::SlowMotion] = 8.0f;
    spawnIntervals[PowerUpType::ExtendPaddle] = 15.0f;
    spawnIntervals[PowerUpType::SplitBall] = 20.0f;
    spawnIntervals[PowerUpType::SlowMotion] = 25.0f;
    // Start timers
    spawnTimers = spawnIntervals;
}

void PowerUpManager::update(float dt, const std::vector<Ball>& balls, Paddle& playerPaddle, std::vector<Ball>& ballsRef) {
    // Update spawn timers
    for (auto& pair : spawnTimers) {
        pair.second -= dt;
        if (pair.second <= 0) {
            spawnPowerUp(pair.first);
            pair.second = spawnIntervals[pair.first];
        }
    }
    // Update powerUps
    for (auto it = powerUps.begin(); it != powerUps.end(); ) {
        it->update(dt);
        if (it->getBounds().position.y > 600) {
            it = powerUps.erase(it);
        } else {
            ++it;
        }
    }
    // Check collisions with balls
    for (auto it = powerUps.begin(); it != powerUps.end(); ) {
        bool collided = false;
        for (const auto& ball : balls) {
            if (it->getBounds().findIntersection(ball.getBounds())) {
                applyEffect(it->getType(), playerPaddle, ballsRef);
                collided = true;
                break;
            }
        }
        if (collided) {
            it = powerUps.erase(it);
        } else {
            ++it;
        }
    }
    // Update active effects
    for (auto it = activeEffects.begin(); it != activeEffects.end(); ) {
        it->timeLeft -= dt;
        if (it->timeLeft <= 0) {
            revertEffect(it->type, playerPaddle, ballsRef);
            it = activeEffects.erase(it);
        } else {
            ++it;
        }
    }
}

void PowerUpManager::draw(sf::RenderWindow& window) {
    for (auto& pu : powerUps) {
        pu.draw(window);
    }
}

void PowerUpManager::spawnPowerUp(PowerUpType type) {
    float x = static_cast<float>(std::rand() % 800);
    sf::Vector2f pos(x, 0);
    powerUps.emplace_back(type, pos);
}

void PowerUpManager::applyEffect(PowerUpType type, Paddle& playerPaddle, std::vector<Ball>& balls) {
    switch (type) {
        case PowerUpType::ExtendPaddle:
            playerPaddle.extend(durations[type]);
            activeEffects.push_back({type, durations[type]});
            break;
        case PowerUpType::SplitBall:
            balls.emplace_back(); // Spawn extra ball
            break;
        case PowerUpType::SlowMotion:
            for (auto& ball : balls) {
                ball.setSpeedMultiplier(0.5f);
            }
            activeEffects.push_back({type, durations[type]});
            break;
    }
}

void PowerUpManager::revertEffect(PowerUpType type, Paddle& playerPaddle, std::vector<Ball>& balls) {
    switch (type) {
        case PowerUpType::ExtendPaddle:
            // Revert handled in Paddle
            break;
        case PowerUpType::SlowMotion:
            for (auto& ball : balls) {
                ball.setSpeedMultiplier(1.0f);
            }
            break;
        case PowerUpType::SplitBall:
            // No revert
            break;
    }
}

const std::vector<ActiveEffect>& PowerUpManager::getActiveEffects() const {
    return activeEffects;
}