#!/usr/bin/env python3
"""
Demo script showcasing the AI components of Pong Evolved.
Demonstrates the complete AI pipeline from data collection to inference.
"""

import argparse
import os
import sys
import subprocess
import time
import numpy as np

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from scripts.data_collection.create_sample_data import create_sample_data

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print('='*50)
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("SUCCESS!")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("FAILED!")
        print("Error:", e.stderr)
        return False

def check_file_exists(path, description):
    """Check if a file exists"""
    if os.path.exists(path):
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description}: {path} (NOT FOUND)")
        return False

def demo_data_creation():
    """Demo data creation"""
    print("\n" + "="*60)
    print("DEMO: Creating Sample Training Data")
    print("="*60)
    
    # Create sample data
    data_path = create_sample_data(1000, 'data/bc_data.npz')
    
    # Verify data was created
    if check_file_exists(data_path, "Sample training data"):
        data = np.load(data_path)
        print(f"  - Samples: {len(data['states'])}")
        print(f"  - State shape: {data['states'].shape}")
        print(f"  - Action distribution: {np.bincount(data['actions'])}")
        return True
    return False

def demo_bc_training():
    """Demo behavioral cloning training"""
    print("\n" + "="*60)
    print("DEMO: Behavioral Cloning Training")
    print("="*60)
    
    cmd = "python3 scripts/training/train_bc.py --data data/bc_data.npz --model models/bc_model.pth --epochs 20"
    return run_command(cmd, "Behavioral Cloning Training")

def demo_dqn_training():
    """Demo DQN training"""
    print("\n" + "="*60)
    print("DEMO: Deep Q-Network Training")
    print("="*60)
    
    cmd = "python3 scripts/training/train_dqn.py --config config/ai/train_config.yaml"
    return run_command(cmd, "DQN Training")

def demo_hybrid_training():
    """Demo hybrid training"""
    print("\n" + "="*60)
    print("DEMO: Hybrid Training (BC + RL)")
    print("="*60)
    
    cmd = "python3 scripts/training/hybrid_train.py --bc-model models/bc_model.pth --output-model models/hybrid_model.pth"
    return run_command(cmd, "Hybrid Training")

def demo_evaluation():
    """Demo model evaluation"""
    print("\n" + "="*60)
    print("DEMO: Model Evaluation")
    print("="*60)
    
    # Check if models exist
    models = [
        ('models/bc_model.pth', 'BC Model'),
        ('models/dqn_model.pth', 'DQN Model'),
        ('models/hybrid_model.pth', 'Hybrid Model')
    ]
    
    for model_path, model_name in models:
        if os.path.exists(model_path):
            print(f"\nEvaluating {model_name}...")
            cmd = f"python3 scripts/evaluation/evaluate_agent.py --model {model_path} --episodes 10"
            run_command(cmd, f"{model_name} Evaluation")
        else:
            print(f"Skipping {model_name} evaluation (model not found)")

def demo_inference_server():
    """Demo inference server"""
    print("\n" + "="*60)
    print("DEMO: Inference Server")
    print("="*60)
    
    # Check if any model exists
    models = ['models/bc_model.pth', 'models/dqn_model.pth', 'models/hybrid_model.pth']
    model_path = None
    
    for model in models:
        if os.path.exists(model):
            model_path = model
            break
    
    if model_path:
        print(f"Starting inference server with model: {model_path}")
        print("Note: This will start a server that runs indefinitely.")
        print("Press Ctrl+C to stop the server.")
        
        cmd = f"python3 src/ai/inference_server.py --model {model_path}"
        return run_command(cmd, "Inference Server")
    else:
        print("No trained models found. Skipping inference server demo.")
        return False

def demo_load_testing():
    """Demo load testing"""
    print("\n" + "="*60)
    print("DEMO: Load Testing")
    print("="*60)
    
    cmd = "python3 scripts/evaluation/load_test.py --test health"
    return run_command(cmd, "Load Testing")

def main():
    parser = argparse.ArgumentParser(description='Demo AI components of Pong Evolved')
    parser.add_argument('--components', nargs='+', 
                       choices=['data', 'bc', 'dqn', 'hybrid', 'eval', 'inference', 'load', 'all'],
                       default=['all'], help='Components to demo')
    
    args = parser.parse_args()
    
    if 'all' in args.components:
        components = ['data', 'bc', 'dqn', 'hybrid', 'eval', 'inference', 'load']
    else:
        components = args.components
    
    print("PONG EVOLVED - AI COMPONENTS DEMO")
    print("="*60)
    print("This demo showcases the AI components of Pong Evolved.")
    print("Make sure you have:")
    print("1. Python dependencies installed (pip install -r requirements.txt)")
    print("2. The C++ game built (cd cpp && ./build.sh)")
    print("3. The game running in server mode (./build/pong_evolved --server)")
    print()
    
    # Check prerequisites
    print("Checking prerequisites...")
    if not check_file_exists('requirements.txt', 'Requirements file'):
        print("Please run this script from the project root directory.")
        return 1
    
    if not check_file_exists('build/pong_evolved', 'C++ game executable'):
        print("Please build the C++ game first: ./scripts/build.sh")
        return 1
    
    # Run demos
    results = {}
    
    if 'data' in components:
        results['data'] = demo_data_creation()
    
    if 'bc' in components:
        results['bc'] = demo_bc_training()
    
    if 'dqn' in components:
        results['dqn'] = demo_dqn_training()
    
    if 'hybrid' in components:
        results['hybrid'] = demo_hybrid_training()
    
    if 'eval' in components:
        demo_evaluation()
        results['eval'] = True
    
    if 'inference' in components:
        results['inference'] = demo_inference_server()
    
    if 'load' in components:
        results['load'] = demo_load_testing()
    
    # Summary
    print("\n" + "="*60)
    print("DEMO SUMMARY")
    print("="*60)
    
    for component, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{component.upper()}: {status}")
    
    print("\nDemo completed!")
    print("For more information, see the README.md file.")
    
    return 0

if __name__ == '__main__':
    exit(main())
