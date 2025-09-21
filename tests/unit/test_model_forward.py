import torch
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ai.model import DQN

def test_model_forward():
    model = DQN(12, 3)
    state = torch.randn(1, 12)
    output = model(state)
    assert output.shape == (1, 3)
    assert torch.all(torch.isfinite(output))