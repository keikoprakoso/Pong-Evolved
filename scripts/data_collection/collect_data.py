#!/usr/bin/env python3
"""
Human data collection script for Pong Evolved.
Collects state-action pairs from human gameplay for behavioral cloning.
"""

import argparse
import json
import numpy as np
import os
import time
import socket
from collections import deque

class HumanDataCollector:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.sock = None
        self.data = []
        self.last_scores = {'player': 0, 'bot': 0}
        
    def connect(self):
        """Connect to the game server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print(f"Connected to game server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect to game server: {e}")
            print("Make sure the game is running in server mode: ./build/pong_evolved --server")
            return False
    
    def disconnect(self):
        """Disconnect from the game server"""
        if self.sock:
            self.sock.close()
            self.sock = None
    
    def get_state(self):
        """Get current game state"""
        try:
            buffer = ""
            while not buffer.endswith('\n'):
                data = self.sock.recv(4096).decode('utf-8')
                if not data:
                    raise ConnectionError("Connection lost")
                buffer += data
            msg = json.loads(buffer.strip())
            return msg['data']
        except Exception as e:
            print(f"Error receiving state: {e}")
            return None
    
    def send_action(self, action):
        """Send action to game server"""
        try:
            action_msg = {
                'type': 'action',
                'data': {'action': action, 'timestamp': time.time()}
            }
            self.sock.send((json.dumps(action_msg) + '\n').encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error sending action: {e}")
            return False
    
    def flatten_state(self, state):
        """Convert state to flat array for training"""
        if not state['balls']:
            ball = {'x': 400, 'y': 300, 'vx': 0, 'vy': 0}
        else:
            ball = state['balls'][0]
        
        player = state['player_paddle']
        bot = state['bot_paddle']
        scores = state['scores']
        
        return np.array([
            ball['x'], ball['y'], ball['vx'], ball['vy'],
            player['x'], player['y'], player['width'], player['height'],
            bot['x'], bot['y'], bot['width'], bot['height'],
            scores['player'], scores['bot']
        ], dtype=np.float32)
    
    def collect_data(self, max_samples=10000, save_interval=1000):
        """Collect human gameplay data"""
        print("Starting data collection...")
        print("Controls:")
        print("  W/Up Arrow: Move paddle up")
        print("  S/Down Arrow: Move paddle down")
        print("  Space: No action")
        print("  Q: Quit and save data")
        print("  R: Reset game")
        print()
        
        sample_count = 0
        game_count = 0
        
        while sample_count < max_samples:
            state = self.get_state()
            if state is None:
                print("Failed to get state, retrying...")
                time.sleep(0.1)
                continue
            
            # Get human input
            action = self.get_human_input()
            if action == 'quit':
                break
            elif action == 'reset':
                self.send_action(0)  # Send reset action
                game_count += 1
                print(f"Game {game_count} reset")
                continue
            
            # Convert action to numeric
            if action == 'up':
                action_val = 1
            elif action == 'down':
                action_val = -1
            else:  # no action
                action_val = 0
            
            # Send action and get next state
            if self.send_action(action_val):
                next_state = self.get_state()
                if next_state is None:
                    continue
                
                # Calculate reward
                reward = (next_state['scores']['player'] - self.last_scores['player']) - \
                        (next_state['scores']['bot'] - self.last_scores['bot'])
                self.last_scores = next_state['scores']
                
                # Store data
                flat_state = self.flatten_state(state)
                flat_next_state = self.flatten_state(next_state)
                
                self.data.append({
                    'state': flat_state,
                    'action': action_val + 1,  # Convert to 0-2 range
                    'reward': reward,
                    'next_state': flat_next_state,
                    'done': False
                })
                
                sample_count += 1
                
                if sample_count % 100 == 0:
                    print(f"Collected {sample_count} samples")
                
                # Save periodically
                if sample_count % save_interval == 0:
                    self.save_data(f"data/bc_data_partial_{sample_count}.npz")
            
            time.sleep(0.016)  # ~60 FPS
        
        print(f"Data collection complete! Collected {sample_count} samples from {game_count} games")
        return sample_count
    
    def get_human_input(self):
        """Get human input (simplified for demo - in real implementation, use keyboard input)"""
        # This is a simplified version. In a real implementation, you'd use:
        # - pygame for keyboard input
        # - or a GUI interface
        # - or read from a file with recorded inputs
        
        # For now, return random actions as a placeholder
        import random
        actions = ['up', 'down', 'none', 'none', 'none']  # Bias toward no action
        return random.choice(actions)
    
    def save_data(self, filename):
        """Save collected data to file"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Convert to numpy arrays
        states = np.array([d['state'] for d in self.data])
        actions = np.array([d['action'] for d in self.data])
        rewards = np.array([d['reward'] for d in self.data])
        next_states = np.array([d['next_state'] for d in self.data])
        dones = np.array([d['done'] for d in self.data])
        
        np.savez(filename,
                states=states,
                actions=actions,
                rewards=rewards,
                next_states=next_states,
                dones=dones)
        
        print(f"Data saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Collect human gameplay data for behavioral cloning')
    parser.add_argument('--host', type=str, default='localhost', help='Game server host')
    parser.add_argument('--port', type=int, default=5000, help='Game server port')
    parser.add_argument('--max-samples', type=int, default=10000, help='Maximum samples to collect')
    parser.add_argument('--output', type=str, default='../../data/bc_data.npz', help='Output file path')
    
    args = parser.parse_args()
    
    collector = HumanDataCollector(args.host, args.port)
    
    if not collector.connect():
        return 1
    
    try:
        samples = collector.collect_data(args.max_samples)
        collector.save_data(args.output)
        print(f"Successfully collected {samples} samples")
    except KeyboardInterrupt:
        print("\nData collection interrupted by user")
        collector.save_data(args.output)
    except Exception as e:
        print(f"Error during data collection: {e}")
        return 1
    finally:
        collector.disconnect()
    
    return 0

if __name__ == '__main__':
    exit(main())