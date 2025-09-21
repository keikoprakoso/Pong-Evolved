import yaml
import torch
import numpy as np
import random
from pong_env import PongEnv
from agent import DQNAgent

def demo():
    with open('config/train_config.yaml') as f:
        config = yaml.safe_load(f)

    # Set deterministic seeds
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)

    env = PongEnv()
    state_size = 12
    action_size = 3
    agent = DQNAgent(state_size, action_size, config)

    obs = env.reset()
    state = env._flatten_obs(obs)
    total_steps = 0

    while total_steps < 1000:
        action = agent.select_action(state)  # Random initially
        obs, reward, done, _ = env.step(action)
        next_state = env._flatten_obs(obs)
        agent.update(state, action, reward, next_state, done)
        state = next_state
        total_steps += 1
        if done:
            obs = env.reset()
            state = env._flatten_obs(obs)

    agent.save_checkpoint('demo_checkpoint.pth')
    env.close()
    print("Demo: 1000 steps completed, checkpoint saved.")

if __name__ == '__main__':
    demo()