#!/usr/bin/env python3
"""
Evaluation script for trained RL agents.
Tests agent performance against the game environment.
"""

import argparse
import torch
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ai.pong_env import PongEnv
from ai.model import DQN

class AgentEvaluator:
    def __init__(self, model_path, device=None):
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        self.model = None
        
    def load_model(self):
        """Load the trained model"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        print(f"Loading model from {self.model_path}")
        self.model = DQN().to(self.device)
        
        # Try to load as state dict first, then as full checkpoint
        try:
            checkpoint = torch.load(self.model_path, map_location=self.device)
            if 'policy_net' in checkpoint:
                # Full checkpoint
                self.model.load_state_dict(checkpoint['policy_net'])
            else:
                # Just state dict
                self.model.load_state_dict(checkpoint)
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
        
        self.model.eval()
        print("Model loaded successfully")
    
    def evaluate_episode(self, env, max_steps=1000, render=False):
        """Evaluate agent for one episode"""
        obs = env.reset()
        state = env._flatten_obs(obs)
        
        total_reward = 0
        steps = 0
        done = False
        
        while not done and steps < max_steps:
            # Get action from model
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                action = self.model(state_tensor).argmax().item()
            
            # Take action
            obs, reward, done, _ = env.step(action)
            next_state = env._flatten_obs(obs)
            
            total_reward += reward
            state = next_state
            steps += 1
            
            if render:
                print(f"Step {steps}: Action {action}, Reward {reward:.2f}, Total {total_reward:.2f}")
        
        return total_reward, steps
    
    def evaluate(self, num_episodes=100, max_steps=1000, render=False):
        """Evaluate agent over multiple episodes"""
        if self.model is None:
            self.load_model()
        
        print(f"Evaluating agent over {num_episodes} episodes...")
        
        env = PongEnv()
        rewards = []
        steps = []
        
        try:
            for episode in range(num_episodes):
                reward, step_count = self.evaluate_episode(env, max_steps, render)
                rewards.append(reward)
                steps.append(step_count)
                
                if episode % 10 == 0:
                    print(f"Episode {episode}: Reward {reward:.2f}, Steps {step_count}")
            
            # Calculate statistics
            mean_reward = np.mean(rewards)
            std_reward = np.std(rewards)
            mean_steps = np.mean(steps)
            std_steps = np.std(steps)
            
            print(f"\nEvaluation Results:")
            print(f"Mean Reward: {mean_reward:.2f} ± {std_reward:.2f}")
            print(f"Mean Steps: {mean_steps:.2f} ± {std_steps:.2f}")
            print(f"Max Reward: {np.max(rewards):.2f}")
            print(f"Min Reward: {np.min(rewards):.2f}")
            
            return {
                'rewards': rewards,
                'steps': steps,
                'mean_reward': mean_reward,
                'std_reward': std_reward,
                'mean_steps': mean_steps,
                'std_steps': std_steps
            }
            
        except Exception as e:
            print(f"Error during evaluation: {e}")
            return None
        finally:
            env.close()
    
    def plot_results(self, results, save_path=None):
        """Plot evaluation results"""
        if results is None:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Reward distribution
        ax1.hist(results['rewards'], bins=20, alpha=0.7, edgecolor='black')
        ax1.axvline(results['mean_reward'], color='red', linestyle='--', 
                    label=f'Mean: {results["mean_reward"]:.2f}')
        ax1.set_xlabel('Total Reward')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Reward Distribution')
        ax1.legend()
        
        # Steps distribution
        ax2.hist(results['steps'], bins=20, alpha=0.7, edgecolor='black')
        ax2.axvline(results['mean_steps'], color='red', linestyle='--',
                    label=f'Mean: {results["mean_steps"]:.2f}')
        ax2.set_xlabel('Steps per Episode')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Steps Distribution')
        ax2.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            print(f"Plot saved to {save_path}")
        
        plt.show()

def main():
    parser = argparse.ArgumentParser(description='Evaluate trained RL agent')
    parser.add_argument('--model', type=str, required=True,
                       help='Path to trained model')
    parser.add_argument('--episodes', type=int, default=100,
                       help='Number of episodes to evaluate')
    parser.add_argument('--max-steps', type=int, default=1000,
                       help='Maximum steps per episode')
    parser.add_argument('--render', action='store_true',
                       help='Render episodes (print step-by-step)')
    parser.add_argument('--plot', type=str, default='../../results/evaluation_results.png',
                       help='Path to save evaluation plot')
    
    args = parser.parse_args()
    
    # Initialize evaluator
    evaluator = AgentEvaluator(args.model)
    
    try:
        # Evaluate agent
        results = evaluator.evaluate(
            num_episodes=args.episodes,
            max_steps=args.max_steps,
            render=args.render
        )
        
        if results:
            # Plot results
            evaluator.plot_results(results, args.plot)
            
            # Save results
            results_path = args.plot.replace('.png', '_data.npz')
            np.savez(results_path,
                    rewards=results['rewards'],
                    steps=results['steps'],
                    mean_reward=results['mean_reward'],
                    std_reward=results['std_reward'],
                    mean_steps=results['mean_steps'],
                    std_steps=results['std_steps'])
            print(f"Results saved to {results_path}")
        
    except Exception as e:
        print(f"Error during evaluation: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())