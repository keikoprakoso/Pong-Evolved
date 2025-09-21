#!/bin/bash

# Build script for Pong Evolved
echo "Building Pong Evolved..."

# Create build directory
mkdir -p build
cd build

# Configure with CMake
echo "Configuring with CMake..."
cmake ..

# Build the project
echo "Building project..."
make

echo "Build complete! Executable: build/pong_evolved"