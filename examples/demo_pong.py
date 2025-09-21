import gymnasium as gym
from pong_env import PongEnv

env = PongEnv()

obs = env.reset()

print("Initial state:", obs)

for i in range(100):

    action = env.action_space.sample()

    obs, reward, done, info = env.step(action)

    print(f"Step {i}: Action {action}, Reward {reward}, Scores {obs['scores']}")

env.close()