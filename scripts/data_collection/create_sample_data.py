#!/usr/bin/env python3
"""
Create sample training data for testing purposes.
Generates synthetic human gameplay data.
"""

import numpy as np
import os

def create_sample_data(num_samples=1000, output_path='data/bc_data.npz'):
    """Create sample human gameplay data"""
    print(f"Creating {num_samples} samples of synthetic human gameplay data...")
    
    # Generate random states (14 features)
    states = np.random.randn(num_samples, 14).astype(np.float32)
    
    # Normalize states to reasonable ranges
    # Ball position (0-800, 0-600)
    states[:, 0] = np.clip(states[:, 0] * 100 + 400, 0, 800)  # ball x
    states[:, 1] = np.clip(states[:, 1] * 100 + 300, 0, 600)  # ball y
    # Ball velocity (-500 to 500)
    states[:, 2] = np.clip(states[:, 2] * 200, -500, 500)  # ball vx
    states[:, 3] = np.clip(states[:, 3] * 200, -500, 500)  # ball vy
    # Player paddle (0-800, 0-600)
    states[:, 4] = np.clip(states[:, 4] * 50 + 50, 0, 800)  # player x
    states[:, 5] = np.clip(states[:, 5] * 100 + 250, 0, 600)  # player y
    # Paddle dimensions
    states[:, 6] = np.clip(states[:, 6] * 10 + 20, 10, 50)  # player width
    states[:, 7] = np.clip(states[:, 7] * 50 + 100, 50, 200)  # player height
    # Bot paddle
    states[:, 8] = np.clip(states[:, 8] * 50 + 730, 0, 800)  # bot x
    states[:, 9] = np.clip(states[:, 9] * 100 + 250, 0, 600)  # bot y
    states[:, 10] = np.clip(states[:, 10] * 10 + 20, 10, 50)  # bot width
    states[:, 11] = np.clip(states[:, 11] * 50 + 100, 50, 200)  # bot height
    # Scores (0-20)
    states[:, 12] = np.clip(states[:, 12] * 5, 0, 20)  # player score
    states[:, 13] = np.clip(states[:, 13] * 5, 0, 20)  # bot score
    
    # Generate actions (0: down, 1: none, 2: up)
    # Bias toward no action (1) for more realistic human behavior
    action_probs = [0.2, 0.6, 0.2]  # 20% down, 60% none, 20% up
    actions = np.random.choice([0, 1, 2], size=num_samples, p=action_probs)
    
    # Generate rewards based on actions
    rewards = np.random.normal(0, 0.1, num_samples).astype(np.float32)
    
    # Generate next states (slightly modified current states)
    next_states = states + np.random.normal(0, 0.01, states.shape).astype(np.float32)
    next_states = np.clip(next_states, 0, 800)  # Keep in valid ranges
    
    # Generate done flags (mostly False)
    dones = np.random.choice([False, True], size=num_samples, p=[0.95, 0.05])
    
    # Save data
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    np.savez(output_path,
             states=states,
             actions=actions,
             rewards=rewards,
             next_states=next_states,
             dones=dones)
    
    print(f"Sample data saved to {output_path}")
    print(f"Action distribution: {np.bincount(actions)}")
    print(f"States shape: {states.shape}")
    print(f"Actions shape: {actions.shape}")
    
    return output_path

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Create sample training data')
    parser.add_argument('--samples', type=int, default=1000,
                       help='Number of samples to generate')
    parser.add_argument('--output', type=str, default='data/bc_data.npz',
                       help='Output file path')
    
    args = parser.parse_args()
    
    create_sample_data(args.samples, args.output)

if __name__ == '__main__':
    main()
