import socket
import json
import torch
import argparse
import os
import sys
import os
sys.path.append(os.path.dirname(__file__))
from model import DQN

class InferenceServer:
    def __init__(self, model_path, host='localhost', port=5001):
        self.model_path = model_path
        self.host = host
        self.port = port
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def load_model(self):
        """Load the trained model"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        print(f"Loading model from {self.model_path}")
        self.model = DQN().to(self.device)
        
        # Try to load as state dict first, then as full checkpoint
        try:
            checkpoint = torch.load(self.model_path, map_location=self.device)
            if 'policy_net' in checkpoint:
                # Full checkpoint
                self.model.load_state_dict(checkpoint['policy_net'])
            else:
                # Just state dict
                self.model.load_state_dict(checkpoint)
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
        
        self.model.eval()
        print("Model loaded successfully")
    
    def start_server(self):
        """Start the inference server"""
        if self.model is None:
            self.load_model()
        
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Low latency
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse
        
        try:
            server_sock.bind((self.host, self.port))
            server_sock.listen(1)
            print(f"Inference server listening on {self.host}:{self.port}")
            
            while True:
                print("Waiting for client connection...")
                client_sock, addr = server_sock.accept()
                print(f"Client connected from {addr}")
                
                try:
                    self.handle_client(client_sock)
                except Exception as e:
                    print(f"Error handling client: {e}")
                finally:
                    client_sock.close()
                    print("Client disconnected")
                    
        except KeyboardInterrupt:
            print("\nServer shutting down...")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            server_sock.close()
    
    def handle_client(self, client_sock):
        """Handle client requests"""
        buffer = ""
        
        while True:
            try:
                data = client_sock.recv(4096).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                
                # Process complete messages
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        response = self.process_message(line.strip())
                        if response:
                            client_sock.send((response + '\n').encode('utf-8'))
                            
            except Exception as e:
                print(f"Error handling client request: {e}")
                break
    
    def process_message(self, message):
        """Process a single message from client"""
        try:
            msg = json.loads(message)
            
            if 'state' in msg:
                # Inference request
                state = msg['state']
                if len(state) != 14:
                    return json.dumps({'error': 'Invalid state size'})
                
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                
                with torch.no_grad():
                    action_probs = self.model(state_tensor)
                    action = action_probs.argmax().item()
                
                return json.dumps({'action': action})
            
            elif 'ping' in msg:
                # Health check
                return json.dumps({'pong': True})
            
            else:
                return json.dumps({'error': 'Unknown message type'})
                
        except json.JSONDecodeError:
            return json.dumps({'error': 'Invalid JSON'})
        except Exception as e:
            return json.dumps({'error': str(e)})

def main():
    parser = argparse.ArgumentParser(description='AI Inference Server for Pong')
    parser.add_argument('--model', type=str, default='../../models/dqn_model.pth',
                       help='Path to trained model')
    parser.add_argument('--host', type=str, default='localhost',
                       help='Server host')
    parser.add_argument('--port', type=int, default=5001,
                       help='Server port')
    
    args = parser.parse_args()
    
    server = InferenceServer(args.model, args.host, args.port)
    server.start_server()

if __name__ == '__main__':
    main()