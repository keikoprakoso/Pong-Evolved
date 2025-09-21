import numpy as np

def load_data(path):
    data = np.load(path)
    return data['states'], data['actions']

def split_data(states, actions, test_ratio=0.2):
    n = len(states)
    indices = np.random.permutation(n)
    test_size = int(n * test_ratio)
    test_indices = indices[:test_size]
    train_indices = indices[test_size:]
    return states[train_indices], actions[train_indices], states[test_indices], actions[test_indices]

def get_action_distribution(actions):
    unique, counts = np.unique(actions, return_counts=True)
    return dict(zip(unique, counts))