import matplotlib.pyplot as plt
import os

class Logger:
    def __init__(self):
        self.episodes = []
        self.rewards = []
        self.epsilons = []
        self.losses = []

    def log(self, episode, reward, epsilon, loss=None):
        self.episodes.append(episode)
        self.rewards.append(reward)
        self.epsilons.append(epsilon)
        if loss is not None:
            self.losses.append(loss)

    def plot(self):
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 2, 1)
        plt.plot(self.episodes, self.rewards)
        plt.title('Total Reward per Episode')
        plt.xlabel('Episode')
        plt.ylabel('Reward')
        plt.subplot(2, 2, 2)
        plt.plot(self.episodes, self.epsilons)
        plt.title('Epsilon Decay')
        plt.xlabel('Episode')
        plt.ylabel('Epsilon')
        plt.subplot(2, 2, 3)
        if self.losses:
            plt.plot(range(len(self.losses)), self.losses)
            plt.title('Training Loss')
            plt.xlabel('Update Step')
            plt.ylabel('Loss')
        plt.tight_layout()
        plt.savefig('training_plot.png')
        plt.show()

def train_agent(agent, env, config, logger):
    # Ensure checkpoints directory exists
    os.makedirs('checkpoints', exist_ok=True)
    for episode in range(config['max_episodes']):
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
        print(f"Episode {episode}, Total Reward {total_reward}, Epsilon {agent.epsilon}, Loss {last_loss}")
        if episode % 100 == 0:
            agent.save_checkpoint(f"checkpoints/episode_{episode}.pth")
    agent.save_checkpoint(config['model_save_path'])
    logger.plot()