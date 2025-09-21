cmake_minimum_required(VERSION 3.16)
project(PongEvolved VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find SFML
find_package(SFML 3 COMPONENTS Graphics Window System REQUIRED)

# Add executable
add_executable(pong_evolved
    src/game/main.cpp
    src/game/Game.cpp
    src/game/Paddle.cpp
    src/game/Ball.cpp
    src/game/PowerUp.cpp
    src/game/PowerUpManager.cpp
    src/game/AIClient.cpp
)

# Link SFML
target_link_libraries(pong_evolved SFML::Graphics SFML::Window SFML::System)

# Include directories
target_include_directories(pong_evolved PRIVATE src/game)
