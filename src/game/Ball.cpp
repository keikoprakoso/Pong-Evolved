#include "Ball.h"
#include <cstdlib>
#include <cmath>

Ball::Ball() {
    shape.setRadius(10);
    shape.setFillColor(sf::Color::White);
    initialPosition = sf::Vector2f(400, 300);
    shape.setPosition(initialPosition - sf::Vector2f(10, 10)); // Position at top-left for shape
    speedMultiplier = 1.0f;  // Added: Initialize speed multiplier
    // Deterministic random seed
    std::srand(42);
    // Random initial direction
    float angle = (std::rand() % 360) * 3.14159f / 180.0f;
    float speed = 300.0f;
    velocity = sf::Vector2f(std::cos(angle) * speed, std::sin(angle) * speed);
}

void Ball::update(float dt) {
    shape.move(velocity * dt * speedMultiplier);
    // Bounce off top and bottom walls
    if (shape.getPosition().y <= 0) {
        bounceY();
        shape.setPosition({shape.getPosition().x, 0});
    } else if (shape.getPosition().y + 20 >= 600) {
        bounceY();
        shape.setPosition({shape.getPosition().x, 580});
    }
}

void Ball::bounceX() {
    velocity.x = -velocity.x;
}

void Ball::bounceY() {
    velocity.y = -velocity.y;
}

void Ball::draw(sf::RenderWindow& window) {
    window.draw(shape);
}

sf::FloatRect Ball::getBounds() const {
    return shape.getGlobalBounds();
}

sf::Vector2f Ball::getPosition() const {
    return shape.getPosition() + sf::Vector2f(10, 10); // Return center position
}

void Ball::reset() {
    shape.setPosition(initialPosition - sf::Vector2f(10, 10));
    speedMultiplier = 1.0f;  // Reset speed multiplier
    // Reseed for deterministic behavior on reset
    std::srand(42);
    float angle = (std::rand() % 360) * 3.14159f / 180.0f;
    float speed = 300.0f;
    velocity = sf::Vector2f(std::cos(angle) * speed, std::sin(angle) * speed);
}

void Ball::setSpeedMultiplier(float mult) {
    speedMultiplier = mult;
}