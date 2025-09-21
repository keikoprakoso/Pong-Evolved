import socket
import json
import time
import random

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('localhost', 6000))
        print("Connected to server")
        buffer = ""
        while True:
            try:
                data = s.recv(4096).decode('utf-8')
                if data:
                    buffer += data
                    messages = buffer.split('\n')
                    buffer = messages[-1]  # Keep incomplete message
                    for msg in messages[:-1]:
                        if msg:
                            state = json.loads(msg)
                            if state.get('type') == 'state':
                                # Simulate AI: random action
                                action_val = random.choice([-1, 0, 1])
                                response = {
                                    'type': 'action',
                                    'data': {'action': action_val, 'timestamp': time.time()}
                                }
                                s.send((json.dumps(response) + '\n').encode('utf-8'))
                                print(f"Sent action: {action_val}")
            except BlockingIOError:
                pass  # No data available
            time.sleep(0.01)  # Prevent busy loop
    except Exception as e:
        print(f"Error: {e}")
    finally:
        s.close()

if __name__ == '__main__':
    main()