# Pong Evolved

A sophisticated AI-driven Pong game combining Imitation Learning and Deep Reinforcement Learning using C++/SFML and Python/PyTorch.

## Features

- **C++ Game Engine**: Real-time graphics and physics with SFML
- **Python AI Pipeline**: Complete ML training and inference system
- **Hybrid AI Approach**: Behavioral Cloning + Deep Q-Learning
- **Real-time Inference**: TCP socket communication between game and AI
- **Data Collection**: Human gameplay data collection for imitation learning
- **Evaluation Tools**: Comprehensive model evaluation and visualization
- **Load Testing**: Performance testing for production deployment

## Project Structure

```
Pong Evolved/
├── src/                          # Source code
│   ├── ai/                       # AI components
│   │   ├── __init__.py
│   │   ├── model.py              # DQN neural network
│   │   ├── agent.py              # DQN agent implementation
│   │   ├── pong_env.py           # Gym environment wrapper
│   │   ├── replay_buffer.py      # Experience replay buffer
│   │   └── inference_server.py   # Real-time inference server
│   ├── game/                     # C++ game engine
│   │   ├── __init__.py
│   │   ├── main.cpp              # Game entry point
│   │   ├── Game.cpp/.h           # Main game class
│   │   ├── Paddle.cpp/.h         # Paddle implementation
│   │   ├── Ball.cpp/.h           # Ball physics
│   │   ├── PowerUp.cpp/.h        # Power-up system
│   │   ├── PowerUpManager.cpp/.h # Power-up management
│   │   └── AIClient.cpp/.h       # AI communication
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── data_utils.py          # Data processing utilities
│       └── visualize.py          # Visualization tools
├── scripts/                       # Executable scripts
│   ├── build.sh                  # Build script
│   ├── training/                 # Training scripts
│   │   ├── train_dqn.py          # DQN training
│   │   ├── train_bc.py           # Behavioral cloning
│   │   └── hybrid_train.py       # Hybrid training
│   ├── evaluation/               # Evaluation scripts
│   │   ├── evaluate_agent.py     # Agent evaluation
│   │   ├── evaluate_bc.py        # BC model evaluation
│   │   └── load_test.py          # Load testing
│   └── data_collection/          # Data collection
│       ├── collect_data.py       # Human data collection
│       └── create_sample_data.py # Sample data generation
├── config/                        # Configuration files
│   ├── ai/                       # AI configuration
│   │   └── train_config.yaml     # Training parameters
│   └── game/                     # Game configuration
│       └── powerups.json         # Power-up settings
├── tests/                         # Test suite
│   ├── unit/                     # Unit tests
│   │   ├── test_env_connection.py
│   │   └── test_model_forward.py
│   └── integration/              # Integration tests
│       └── test_ai_client.py
├── examples/                      # Example scripts
│   ├── demo_ai.py                # AI pipeline demo
│   ├── demo_pong.py              # Game demo
│   └── demo_train.py             # Training demo
├── data/                          # Training data
├── models/                        # Trained models
├── results/                       # Evaluation results
├── logs/                          # Training logs
├── checkpoints/                   # Training checkpoints
├── build/                         # Build artifacts
├── docs/                          # Documentation
├── requirements.txt               # Python dependencies
├── CMakeLists.txt                 # CMake configuration
├── Dockerfile                     # Docker configuration
└── README.md                      # This file
```

## Quick Start

### Prerequisites

- **CMake 3.16+**
- **SFML 3.0+**
- **Python 3.9+** with PyTorch
- **macOS**: `brew install cmake sfml python@3.9`
- **Linux**: `sudo apt install cmake libsfml-dev python3 python3-pip`

### Installation

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd Pong-Evolved
   pip install -r requirements.txt
   ```

2. **Build the game**:
   ```bash
   ./scripts/build.sh
   ```

3. **Run the game**:
   ```bash
   # Windowed mode
   ./build/pong_evolved
   
   # Server mode (for AI)
   ./build/pong_evolved --server
   ```

## AI Training Pipeline

### 1. Data Collection
```bash
# Collect human gameplay data
python scripts/data_collection/collect_data.py --output data/human_data.npz

# Or create sample data for testing
python scripts/data_collection/create_sample_data.py --samples 1000
```

### 2. Behavioral Cloning
```bash
# Train BC model on human data
python scripts/training/train_bc.py --data data/human_data.npz --model models/bc_model.pth
```

### 3. Deep Q-Learning
```bash
# Train DQN from scratch
python scripts/training/train_dqn.py --config config/ai/train_config.yaml
```

### 4. Hybrid Training
```bash
# Combine BC + RL
python scripts/training/hybrid_train.py --bc-model models/bc_model.pth --output-model models/hybrid_model.pth
```

## Evaluation

```bash
# Evaluate trained models
python scripts/evaluation/evaluate_agent.py --model models/dqn_model.pth --episodes 100
python scripts/evaluation/evaluate_bc.py --model models/bc_model.pth --episodes 100

# Load testing
python scripts/evaluation/load_test.py --test all
```

## Inference

```bash
# Start inference server
python src/ai/inference_server.py --model models/dqn_model.pth --port 5001

# Test inference
python scripts/evaluation/load_test.py --test health
```

## Game Controls

- **W/Up Arrow**: Move paddle up
- **S/Down Arrow**: Move paddle down
- **P**: Pause game
- **Q**: Quit

## Testing

```bash
# Run unit tests
python -m pytest tests/unit/ -v

# Run integration tests
python -m pytest tests/integration/ -v
```

## Demo

```bash
# Run complete AI pipeline demo
python examples/demo_ai.py --components all
```

## Docker

```bash
# Build Docker image
docker build -t pong-evolved .

# Run container
docker run -p 5000:5000 -p 5001:5001 pong-evolved
```

## Configuration

### Training Configuration (`config/ai/train_config.yaml`)
```yaml
learning_rate: 0.0001
batch_size: 64
buffer_size: 100000
gamma: 0.99
epsilon_start: 1.0
epsilon_end: 0.01
epsilon_decay: 0.995
target_update_freq: 10
max_episodes: 1000
max_steps_per_episode: 1000
```

### Game Configuration (`config/game/powerups.json`)
```json
{
  "ExtendPaddle": {
    "duration": 10.0,
    "spawnInterval": 15.0
  },
  "SplitBall": {
    "duration": 0.0,
    "spawnInterval": 20.0
  },
  "SlowMotion": {
    "duration": 8.0,
    "spawnInterval": 25.0
  }
}
```

## Troubleshooting

- **Build fails**: Ensure SFML installed correctly
- **Server not connecting**: Check ports 5000/5001 are free
- **AI not responding**: Verify model files exist
- **Window not focused**: Click window for keyboard input
- **M2 issues**: Use MPS backend for PyTorch GPU

## Architecture

- **C++**: Game loop, physics, rendering, AI communication
- **Python**: AI training, inference, data processing, evaluation
- **Communication**: JSON over TCP sockets (port 5000 for game, 5001 for inference)
- **Data Flow**: Human data → BC training → Hybrid training → Evaluation → Inference

## Performance

- **Training**: ~1000 episodes for convergence
- **Inference**: <10ms latency
- **Throughput**: 100+ requests/second
- **Memory**: <1GB for training, <100MB for inference

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation in `docs/`

---

**Pong Evolved** - Where classic gaming meets modern AI!