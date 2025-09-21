import pytest
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ai.pong_env import PongEnv

def test_env_reset():
    env = PongEnv()
    obs = env.reset()
    assert len(obs) == 12
    env.close()

def test_env_step():
    env = PongEnv()
    env.reset()
    obs, reward, done, _ = env.step(0)
    assert len(obs) == 12
    assert isinstance(reward, (int, float))
    assert isinstance(done, bool)
    env.close()