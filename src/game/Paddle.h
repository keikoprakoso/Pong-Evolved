#pragma once

#include <SFML/Graphics.hpp>

class Paddle {
public:
    Paddle(bool isPlayer);
    void moveUp(float amount);
    void moveDown(float amount);
    void draw(sf::RenderWindow& window);
    sf::FloatRect getBounds() const;
    sf::Vector2f getPosition() const;
    void reset();
    void extend(float duration);

public:
    sf::RectangleShape shape;
    bool extended;
    float extendTimeLeft;
    sf::Vector2f originalSize;
private:
    float speed;
    sf::Vector2f initialPosition;
};