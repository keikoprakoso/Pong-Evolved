#include "Paddle.h"

Paddle::Paddle(bool isPlayer) {
    shape.setSize(sf::Vector2f(20, 100));
    shape.setFillColor(sf::Color::White);
    speed = 600.0f; // Speed in pixels/second
    originalSize = shape.getSize();  // Added: Store original size
    extended = false;  // Added: Initialize extended flag
    extendTimeLeft = 0.0f;  // Added: Initialize time left
    if (isPlayer) {
        initialPosition = sf::Vector2f(10, 250);
    } else {
        initialPosition = sf::Vector2f(770, 250);
    }
    shape.setPosition(initialPosition);
}

void Paddle::moveUp(float dt) {
    // Fix: Previously, amount was dt, but moved by dt only, not speed * dt.
    // Now correctly moves by speed * dt for visible movement.
    shape.move({0, -speed * dt});
    // Clamp to top of screen
    if (shape.getPosition().y < 0) {
        shape.setPosition({shape.getPosition().x, 0});
    }
}

void Paddle::moveDown(float dt) {
    // Fix: Same as moveUp, now correctly moves by speed * dt.
    shape.move({0, speed * dt});
    // Clamp to bottom of screen
    if (shape.getPosition().y + shape.getSize().y > 600) {
        shape.setPosition({shape.getPosition().x, 600 - shape.getSize().y});
    }
}

void Paddle::draw(sf::RenderWindow& window) {
    window.draw(shape);
}

sf::FloatRect Paddle::getBounds() const {
    return shape.getGlobalBounds();
}

sf::Vector2f Paddle::getPosition() const {
    // Return center position
    return shape.getPosition() + sf::Vector2f(shape.getSize().x / 2, shape.getSize().y / 2);
}

void Paddle::reset() {
    shape.setPosition(initialPosition);
}

void Paddle::extend(float duration) {
    if (!extended) {
        extended = true;
        extendTimeLeft = duration;
        shape.setSize({originalSize.x * 2, originalSize.y});
    }
}