#!/usr/bin/env python3
"""
Hybrid training script for Pong Evolved.
Combines Behavioral Cloning pretraining with Deep Q-Learning fine-tuning.
"""

import argparse
import yaml
import torch
import numpy as np
import random
import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ai.pong_env import PongEnv
from ai.agent import DQNAgent
from train_loop import train_agent, Logger
from ai.model import DQN

class HybridTrainer:
    def __init__(self, config):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
    def load_bc_model(self, bc_model_path):
        """Load pretrained behavioral cloning model"""
        if not os.path.exists(bc_model_path):
            raise FileNotFoundError(f"BC model not found: {bc_model_path}")
        
        print(f"Loading BC model from {bc_model_path}")
        bc_state_dict = torch.load(bc_model_path, map_location=self.device)
        
        # Create DQN model and load BC weights
        dqn_model = DQN().to(self.device)
        dqn_model.load_state_dict(bc_state_dict)
        
        print("BC model loaded successfully")
        return dqn_model
    
    def initialize_agent_with_bc(self, state_size, action_size, bc_model_path):
        """Initialize DQN agent with BC pretrained weights"""
        # Load BC model
        bc_model = self.load_bc_model(bc_model_path)
        
        # Create agent
        agent = DQNAgent(state_size, action_size, self.config)
        
        # Copy BC weights to policy network
        agent.policy_net.load_state_dict(bc_model.state_dict())
        agent.target_net.load_state_dict(bc_model.state_dict())
        
        # Use lower learning rate for fine-tuning
        hybrid_lr = self.config.get('hybrid_lr', 0.00001)
        agent.optimizer = torch.optim.Adam(agent.policy_net.parameters(), lr=hybrid_lr)
        
        # Start with lower epsilon since we have good initial policy
        agent.epsilon = 0.3  # Start with some exploration
        
        print(f"Agent initialized with BC weights, using hybrid LR: {hybrid_lr}")
        return agent
    
    def train_hybrid(self, agent, env, config, logger):
        """Train agent with hybrid approach"""
        print("Starting hybrid training (BC pretraining + RL fine-tuning)...")
        
        # Ensure checkpoints directory exists
        os.makedirs('checkpoints', exist_ok=True)
        
        # Phase 1: BC pretraining (already done, but we can do some warm-up)
        print("Phase 1: BC warm-up (using pretrained weights)")
        warmup_episodes = config.get('bc_warmup_episodes', 50)
        
        for episode in range(warmup_episodes):
            obs = env.reset()
            state = env._flatten_obs(obs)
            total_reward = 0
            
            for step in range(config['max_steps_per_episode']):
                action = agent.select_action(state)
                obs, reward, done, _ = env.step(action)
                next_state = env._flatten_obs(obs)
                
                # Use BC-style learning (supervised learning on actions)
                loss = agent.update(state, action, reward, next_state, done)
                
                state = next_state
                total_reward += reward
                
                if done:
                    break
            
            logger.log(episode, total_reward, agent.epsilon, None)
            if episode % 10 == 0:
                print(f"BC Warm-up Episode {episode}, Reward: {total_reward:.2f}")
        
        # Phase 2: RL fine-tuning
        print("Phase 2: RL fine-tuning")
        rl_episodes = config['max_episodes'] - warmup_episodes
        
        for episode in range(warmup_episodes, config['max_episodes']):
            obs = env.reset()
            state = env._flatten_obs(obs)
            total_reward = 0
            last_loss = None
            
            for step in range(config['max_steps_per_episode']):
                action = agent.select_action(state)
                obs, reward, done, _ = env.step(action)
                next_state = env._flatten_obs(obs)
                
                loss = agent.update(state, action, reward, next_state, done)
                if loss is not None:
                    last_loss = loss
                
                state = next_state
                total_reward += reward
                
                if done:
                    break
            
            logger.log(episode, total_reward, agent.epsilon, last_loss)
            
            if episode % 50 == 0:
                print(f"RL Episode {episode}, Reward: {total_reward:.2f}, "
                      f"Epsilon: {agent.epsilon:.3f}, Loss: {last_loss:.4f}")
            
            # Save checkpoint
            if episode % 100 == 0:
                agent.save_checkpoint(f"checkpoints/hybrid_episode_{episode}.pth")
        
        # Save final model
        agent.save_checkpoint(config['model_save_path'])
        print("Hybrid training completed!")

def main():
    parser = argparse.ArgumentParser(description='Hybrid training (BC + RL) for Pong')
    parser.add_argument('--config', type=str, default='../../config/ai/train_config.yaml', 
                       help='Config file path')
    parser.add_argument('--bc-model', type=str, default='../../models/bc_model.pth',
                       help='Path to BC pretrained model')
    parser.add_argument('--output-model', type=str, default='../../models/hybrid_model.pth',
                       help='Path to save hybrid model')
    
    args = parser.parse_args()
    
    # Load config
    with open(args.config) as f:
        config = yaml.safe_load(f)
    
    # Override model save path
    config['model_save_path'] = args.output_model
    
    # Set deterministic seeds
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)
    
    # Initialize trainer
    trainer = HybridTrainer(config)
    
    try:
        # Initialize environment
        env = PongEnv()
        state_size = 14
        action_size = 3
        
        # Initialize agent with BC weights
        agent = trainer.initialize_agent_with_bc(state_size, action_size, args.bc_model)
        
        # Initialize logger
        logger = Logger()
        
        # Train with hybrid approach
        trainer.train_hybrid(agent, env, config, logger)
        
        # Plot results
        logger.plot()
        
        print("Hybrid training completed successfully!")
        
    except Exception as e:
        print(f"Error during hybrid training: {e}")
        return 1
    finally:
        env.close()
    
    return 0

if __name__ == '__main__':
    exit(main())