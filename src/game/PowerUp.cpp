#include "PowerUp.h"

PowerUp::PowerUp(PowerUpType type, sf::Vector2f position) : type(type), velocity({0, 100}) {
    shape.setRadius(15);
    shape.setPosition(position);
    switch (type) {
        case PowerUpType::ExtendPaddle:
            shape.setFillColor(sf::Color::Green);
            break;
        case PowerUpType::SplitBall:
            shape.setFillColor(sf::Color::Blue);
            break;
        case PowerUpType::SlowMotion:
            shape.setFillColor(sf::Color::Yellow);
            break;
    }
}

void PowerUp::update(float dt) {
    shape.move(velocity * dt);
}

void PowerUp::draw(sf::RenderWindow& window) {
    window.draw(shape);
}

sf::FloatRect PowerUp::getBounds() const {
    return shape.getGlobalBounds();
}

PowerUpType PowerUp::getType() const {
    return type;
}