import argparse
import yaml
import torch
import numpy as np
import random
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ai.pong_env import PongEnv
from ai.agent import DQNAgent
from train_loop import train_agent, Logger

def main():
    parser = argparse.ArgumentParser(description='Train DQN for Pong')
    parser.add_argument('--config', type=str, default='../../config/ai/train_config.yaml', help='Config file path')
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    # Set deterministic seeds
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)

    env = PongEnv()
    state_size = 14
    action_size = 3
    agent = DQNAgent(state_size, action_size, config)
    logger = Logger()
    train_agent(agent, env, config, logger)
    env.close()

if __name__ == '__main__':
    main()