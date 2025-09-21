#!/usr/bin/env python3
"""
Behavioral Cloning training script for Pong Evolved.
Trains a neural network to imitate human gameplay.
"""

import argparse
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt
import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ai.model import DQN

class BCNetwork(nn.Module):
    """Behavioral Cloning Network - same architecture as DQN"""
    def __init__(self, input_size=14, output_size=3):
        super(BCNetwork, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, output_size)
        )
    
    def forward(self, x):
        return self.net(x)

class BCTrainer:
    def __init__(self, config):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Initialize model
        self.model = BCNetwork().to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=config['learning_rate'])
        self.criterion = nn.CrossEntropyLoss()
        
        # Training history
        self.train_losses = []
        self.val_losses = []
        
    def load_data(self, data_path):
        """Load human gameplay data"""
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data file not found: {data_path}")
        
        print(f"Loading data from {data_path}")
        data = np.load(data_path)
        
        states = data['states']
        actions = data['actions']
        
        print(f"Loaded {len(states)} samples")
        print(f"Action distribution: {np.bincount(actions)}")
        
        return states, actions
    
    def prepare_data(self, states, actions, val_split=0.2):
        """Prepare data for training"""
        # Convert to tensors
        states_tensor = torch.FloatTensor(states)
        actions_tensor = torch.LongTensor(actions)
        
        # Create dataset
        dataset = TensorDataset(states_tensor, actions_tensor)
        
        # Split into train/validation
        val_size = int(len(dataset) * val_split)
        train_size = len(dataset) - val_size
        
        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size]
        )
        
        # Create data loaders
        train_loader = DataLoader(
            train_dataset, 
            batch_size=self.config['batch_size'], 
            shuffle=True
        )
        val_loader = DataLoader(
            val_dataset, 
            batch_size=self.config['batch_size'], 
            shuffle=False
        )
        
        return train_loader, val_loader
    
    def train_epoch(self, train_loader):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        
        for states, actions in train_loader:
            states = states.to(self.device)
            actions = actions.to(self.device)
            
            # Forward pass
            outputs = self.model(states)
            loss = self.criterion(outputs, actions)
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(train_loader)
    
    def validate(self, val_loader):
        """Validate the model"""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for states, actions in val_loader:
                states = states.to(self.device)
                actions = actions.to(self.device)
                
                outputs = self.model(states)
                loss = self.criterion(outputs, actions)
                
                total_loss += loss.item()
                
                # Calculate accuracy
                _, predicted = torch.max(outputs.data, 1)
                total += actions.size(0)
                correct += (predicted == actions).sum().item()
        
        avg_loss = total_loss / len(val_loader)
        accuracy = 100 * correct / total
        
        return avg_loss, accuracy
    
    def train(self, train_loader, val_loader, epochs=100):
        """Train the behavioral cloning model"""
        print("Starting behavioral cloning training...")
        
        best_val_loss = float('inf')
        patience = 10
        patience_counter = 0
        
        for epoch in range(epochs):
            # Train
            train_loss = self.train_epoch(train_loader)
            
            # Validate
            val_loss, val_accuracy = self.validate(val_loader)
            
            # Store history
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            
            # Print progress
            if epoch % 10 == 0:
                print(f"Epoch {epoch:3d}: Train Loss: {train_loss:.4f}, "
                      f"Val Loss: {val_loss:.4f}, Val Acc: {val_accuracy:.2f}%")
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model
                self.save_model(self.config['model_save_path'])
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"Early stopping at epoch {epoch}")
                    break
        
        print(f"Training completed! Best validation loss: {best_val_loss:.4f}")
        return best_val_loss
    
    def save_model(self, path):
        """Save the trained model"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save(self.model.state_dict(), path)
        print(f"Model saved to {path}")
    
    def load_model(self, path):
        """Load a trained model"""
        if os.path.exists(path):
            self.model.load_state_dict(torch.load(path, map_location=self.device))
            print(f"Model loaded from {path}")
        else:
            print(f"Model file not found: {path}")
    
    def plot_training(self):
        """Plot training history"""
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 2, 1)
        plt.plot(self.train_losses, label='Train Loss')
        plt.plot(self.val_losses, label='Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.title('Training History')
        
        plt.subplot(1, 2, 2)
        plt.plot(self.val_losses)
        plt.xlabel('Epoch')
        plt.ylabel('Validation Loss')
        plt.title('Validation Loss')
        
        plt.tight_layout()
        plt.savefig('bc_training_plot.png')
        plt.show()

def main():
    parser = argparse.ArgumentParser(description='Train Behavioral Cloning model')
    parser.add_argument('--data', type=str, default='../../data/bc_data.npz', 
                       help='Path to human gameplay data')
    parser.add_argument('--model', type=str, default='../../models/bc_model.pth',
                       help='Path to save trained model')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=64,
                       help='Batch size for training')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                       help='Learning rate')
    parser.add_argument('--val-split', type=float, default=0.2,
                       help='Validation split ratio')
    
    args = parser.parse_args()
    
    # Create config
    config = {
        'batch_size': args.batch_size,
        'learning_rate': args.learning_rate,
        'model_save_path': args.model,
        'epochs': args.epochs
    }
    
    # Initialize trainer
    trainer = BCTrainer(config)
    
    try:
        # Load data
        states, actions = trainer.load_data(args.data)
        
        # Prepare data
        train_loader, val_loader = trainer.prepare_data(states, actions, args.val_split)
        
        # Train model
        best_loss = trainer.train(train_loader, val_loader, args.epochs)
        
        # Plot results
        trainer.plot_training()
        
        print(f"Training completed successfully!")
        print(f"Best validation loss: {best_loss:.4f}")
        print(f"Model saved to: {args.model}")
        
    except Exception as e:
        print(f"Error during training: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())