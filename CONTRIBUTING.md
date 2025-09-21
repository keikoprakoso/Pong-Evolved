# Contributing to Pong Evolved

Thank you for your interest in contributing to Pong Evolved! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/pong-evolved.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

### Prerequisites
- CMake 3.16+
- SFML 3.0+
- Python 3.9+
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/pong-evolved.git
cd pong-evolved

# Install Python dependencies
pip install -r requirements.txt

# Build the C++ game
./scripts/build.sh
```

## Code Style

### Python
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and small

### C++
- Follow Google C++ Style Guide
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions under 50 lines when possible

## Testing

### Running Tests
```bash
# Run unit tests
python -m pytest tests/unit/ -v

# Run integration tests
python -m pytest tests/integration/ -v

# Test complete pipeline
python examples/demo_ai.py --components all
```

### Writing Tests
- Write tests for new functionality
- Aim for good test coverage
- Use descriptive test names
- Test both success and failure cases

## Project Structure

```
src/
├── ai/           # AI components (models, agents, environments)
├── game/         # C++ game engine
└── utils/        # Utility functions

scripts/
├── training/     # Training scripts
├── evaluation/   # Evaluation and testing
└── data_collection/ # Data collection tools

tests/
├── unit/         # Unit tests
└── integration/  # Integration tests

config/           # Configuration files
examples/         # Example scripts and demos
```

## Areas for Contribution

### High Priority
- [ ] Real human data collection with keyboard input
- [ ] Web-based interface for training/evaluation
- [ ] Additional AI algorithms (PPO, A3C, SAC)
- [ ] Performance optimizations
- [ ] Better documentation and tutorials

### Medium Priority
- [ ] Multi-agent training
- [ ] Tournament mode
- [ ] Replay system
- [ ] Sound effects and music
- [ ] Mobile app version

### Low Priority
- [ ] Different game modes
- [ ] Customizable AI personalities
- [ ] Social features
- [ ] Analytics dashboard

## Bug Reports

When reporting bugs, please include:
- Operating system and version
- Python version
- Steps to reproduce the issue
- Expected vs actual behavior
- Error messages (if any)

## Feature Requests

When requesting features, please:
- Describe the feature clearly
- Explain why it would be useful
- Provide examples of how it would work
- Consider the impact on existing functionality

## Pull Request Guidelines

- Keep PRs focused and small
- Write clear commit messages
- Update documentation as needed
- Add tests for new functionality
- Ensure all tests pass
- Update CHANGELOG.md if applicable

## Code Review Process

- All PRs require review before merging
- Reviewers will check code quality, tests, and documentation
- Address feedback promptly
- Be respectful and constructive in discussions

## Release Process

- Version numbers follow semantic versioning (MAJOR.MINOR.PATCH)
- Releases are tagged in git
- Release notes are created for each version
- Documentation is updated for new features

## Questions?

Feel free to open an issue for questions or start a discussion in the GitHub Discussions section.

Thank you for contributing to Pong Evolved!
