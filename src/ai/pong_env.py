import gymnasium as gym
import socket
import json
import time
import numpy as np

class PongEnv(gym.Env):
    def __init__(self, mode='socket', host='localhost', port=6000):
        super().__init__()
        self.action_space = gym.spaces.Discrete(3)  # 0: down (-1), 1: none (0), 2: up (1)
        self.observation_space = gym.spaces.Dict({
            'balls': gym.spaces.Sequence(gym.spaces.Dict({
                'x': gym.spaces.Box(low=0, high=800, shape=()),
                'y': gym.spaces.Box(low=0, high=600, shape=()),
                'vx': gym.spaces.Box(low=-500, high=500, shape=()),
                'vy': gym.spaces.Box(low=-500, high=500, shape=()),
            })),
            'player_paddle': gym.spaces.Dict({
                'x': gym.spaces.Box(low=0, high=800, shape=()),
                'y': gym.spaces.Box(low=0, high=600, shape=()),
                'width': gym.spaces.Box(low=0, high=100, shape=()),
                'height': gym.spaces.Box(low=0, high=200, shape=()),
            }),
            'bot_paddle': gym.spaces.Dict({
                'x': gym.spaces.Box(low=0, high=800, shape=()),
                'y': gym.spaces.Box(low=0, high=600, shape=()),
                'width': gym.spaces.Box(low=0, high=100, shape=()),
                'height': gym.spaces.Box(low=0, high=200, shape=()),
            }),
            'scores': gym.spaces.Dict({
                'player': gym.spaces.Discrete(100),
                'bot': gym.spaces.Discrete(100),
            }),
            'power_ups': gym.spaces.Sequence(gym.spaces.Dict({
                'type': gym.spaces.Discrete(3),
                'x': gym.spaces.Box(low=0, high=800, shape=()),
                'y': gym.spaces.Box(low=0, high=600, shape=()),
            })),
            'active_effects': gym.spaces.Sequence(gym.spaces.Dict({
                'type': gym.spaces.Discrete(3),
                'time_left': gym.spaces.Box(low=0, high=20, shape=()),
            })),
        })
        self.mode = mode
        self.host = host
        self.port = port
        self.sock = None
        self.last_scores = {'player': 0, 'bot': 0}

    def reset(self):
        if self.sock:
            self.sock.close()
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            # Get initial state
            state = self._recv_state()
            self.last_scores = state['scores']
            return state
        except Exception as e:
            print(f"Failed to connect to game server at {self.host}:{self.port}")
            print(f"Error: {e}")
            print("Make sure the game is running in server mode: ./build/pong_evolved --server")
            raise

    def step(self, action):
        try:
            action_val = action - 1  # 0->-1, 1->0, 2->1
            action_msg = {
                'type': 'action',
                'data': {'action': action_val, 'timestamp': time.time()}
            }
            self.sock.send((json.dumps(action_msg) + '\n').encode('utf-8'))
            # Receive new state
            state = self._recv_state()
            # Reward based on score change
            reward = (state['scores']['player'] - self.last_scores['player']) - (state['scores']['bot'] - self.last_scores['bot'])
            self.last_scores = state['scores']
            done = False
            return state, reward, done, {}
        except Exception as e:
            print(f"Error in step: {e}")
            # Return a default state if connection fails
            return self._get_default_state(), 0, True, {}

    def render(self, mode='human'):
        pass  # No rendering

    def close(self):
        if self.sock:
            self.sock.close()

    def _recv_state(self):
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
            raise

    def _get_default_state(self):
        """Return a default state when connection fails"""
        return {
            'balls': [{'x': 400, 'y': 300, 'vx': 0, 'vy': 0}],
            'player_paddle': {'x': 50, 'y': 250, 'width': 20, 'height': 100},
            'bot_paddle': {'x': 730, 'y': 250, 'width': 20, 'height': 100},
            'scores': {'player': 0, 'bot': 0},
            'power_ups': [],
            'active_effects': []
        }

    def _flatten_obs(self, obs):
        if not obs['balls']:
            # Default values if no balls
            ball = {'x': 400, 'y': 300, 'vx': 0, 'vy': 0}
        else:
            ball = obs['balls'][0]
        player = obs['player_paddle']
        bot = obs['bot_paddle']
        scores = obs['scores']
        return np.array([
            ball['x'], ball['y'], ball['vx'], ball['vy'],
            player['x'], player['y'], player['width'], player['height'],
            bot['x'], bot['y'], bot['width'], bot['height'],
            scores['player'], scores['bot']
        ], dtype=np.float32)