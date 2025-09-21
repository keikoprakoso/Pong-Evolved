#pragma once

#include <SFML/Graphics.hpp>

class Ball {
public:
    Ball();
    void update(float dt);
    void bounceX();
    void bounceY();
    void draw(sf::RenderWindow& window);
    sf::FloatRect getBounds() const;
    sf::Vector2f getPosition() const;
    void reset();
    void setSpeedMultiplier(float mult);

public:
    sf::Vector2f velocity;
private:
    sf::CircleShape shape;
    sf::Vector2f initialPosition;
    float speedMultiplier;
};