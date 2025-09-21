import torch
import torch.optim as optim
import numpy as np
import os
from .model import DQN
from .replay_buffer import ReplayBuffer

class DQNAgent:
    def __init__(self, state_size, action_size, config):
        self.state_size = state_size
        self.action_size = action_size
        self.policy_net = DQN(state_size, action_size)
        self.target_net = DQN(state_size, action_size)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=config['learning_rate'])
        self.buffer = ReplayBuffer(config['buffer_size'])
        self.gamma = config['gamma']
        self.epsilon = config['epsilon_start']
        self.epsilon_end = config['epsilon_end']
        self.epsilon_decay = config['epsilon_decay']
        self.target_update_freq = config['target_update_freq']
        self.batch_size = config['batch_size']
        self.steps = 0

    def select_action(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.action_size)
        else:
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0)
                return self.policy_net(state_tensor).argmax().item()

    def update(self, state, action, reward, next_state, done):
        self.buffer.push(state, action, reward, next_state, done)
        loss = None
        if len(self.buffer) >= self.batch_size:
            loss = self._train_step()
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
        self.steps += 1
        if self.steps % self.target_update_freq == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
        return loss

    def _train_step(self):
        states, actions, rewards, next_states, dones = self.buffer.sample(self.batch_size)
        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)
        q_values = self.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        with torch.no_grad():
            next_q_values = self.target_net(next_states).max(1)[0]
        target = rewards + self.gamma * next_q_values * (1 - dones)
        loss = torch.nn.functional.mse_loss(q_values, target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def save_checkpoint(self, path):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            torch.save({
                'policy_net': self.policy_net.state_dict(),
                'target_net': self.target_net.state_dict(),
                'optimizer': self.optimizer.state_dict(),
                'epsilon': self.epsilon,
                'steps': self.steps
            }, path)
            print(f"Checkpoint saved to {path}")
        except Exception as e:
            print(f"Error saving checkpoint: {e}")

    def load_checkpoint(self, path):
        try:
            if not os.path.exists(path):
                print(f"Checkpoint file {path} not found")
                return
            checkpoint = torch.load(path)
            self.policy_net.load_state_dict(checkpoint['policy_net'])
            self.target_net.load_state_dict(checkpoint['target_net'])
            self.optimizer.load_state_dict(checkpoint['optimizer'])
            self.epsilon = checkpoint['epsilon']
            self.steps = checkpoint['steps']
            print(f"Checkpoint loaded from {path}")
        except Exception as e:
            print(f"Error loading checkpoint: {e}")