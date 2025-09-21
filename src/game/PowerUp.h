#pragma once

#include <SFML/Graphics.hpp>

enum class PowerUpType { ExtendPaddle, SplitBall, SlowMotion };

class PowerUp {
public:
    PowerUp(PowerUpType type, sf::Vector2f position);
    void update(float dt);
    void draw(sf::RenderWindow& window);
    sf::FloatRect getBounds() const;
    PowerUpType getType() const;

private:
    PowerUpType type;
    sf::CircleShape shape;
    sf::Vector2f velocity;
};