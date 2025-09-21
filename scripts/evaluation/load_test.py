#!/usr/bin/env python3
"""
Load testing script for the inference server.
Tests server performance under various loads.
"""

import argparse
import socket
import json
import time
import threading
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

class LoadTester:
    def __init__(self, host='localhost', port=5001):
        self.host = host
        self.port = port
        
    def create_test_state(self):
        """Create a random test state"""
        return np.random.randn(14).tolist()
    
    def send_request(self, state):
        """Send a single inference request"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5 second timeout
            sock.connect((self.host, self.port))
            
            # Send request
            request = json.dumps({'state': state}) + '\n'
            sock.send(request.encode('utf-8'))
            
            # Receive response
            response = sock.recv(4096).decode('utf-8')
            sock.close()
            
            # Parse response
            result = json.loads(response.strip())
            return result
            
        except Exception as e:
            return {'error': str(e)}
    
    def test_single_request(self):
        """Test a single request"""
        print("Testing single request...")
        state = self.create_test_state()
        
        start_time = time.time()
        result = self.send_request(state)
        end_time = time.time()
        
        latency = end_time - start_time
        
        if 'error' in result:
            print(f"Error: {result['error']}")
            return False
        else:
            print(f"Success! Action: {result['action']}, Latency: {latency:.3f}s")
            return True
    
    def test_concurrent_requests(self, num_requests=10, max_workers=5):
        """Test concurrent requests"""
        print(f"Testing {num_requests} concurrent requests with {max_workers} workers...")
        
        states = [self.create_test_state() for _ in range(num_requests)]
        results = []
        latencies = []
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.send_request, state) for state in states]
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                
                if 'error' not in result:
                    latencies.append(time.time() - start_time)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful = sum(1 for r in results if 'error' not in r)
        failed = len(results) - successful
        
        print(f"Results:")
        print(f"  Successful: {successful}/{num_requests}")
        print(f"  Failed: {failed}/{num_requests}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Requests/second: {num_requests/total_time:.2f}")
        
        if latencies:
            print(f"  Average latency: {np.mean(latencies):.3f}s")
            print(f"  Min latency: {np.min(latencies):.3f}s")
            print(f"  Max latency: {np.max(latencies):.3f}s")
        
        return successful, failed
    
    def test_sustained_load(self, duration=30, requests_per_second=5):
        """Test sustained load over time"""
        print(f"Testing sustained load: {requests_per_second} req/s for {duration}s...")
        
        start_time = time.time()
        results = []
        
        while time.time() - start_time < duration:
            batch_start = time.time()
            
            # Send batch of requests
            for _ in range(requests_per_second):
                state = self.create_test_state()
                result = self.send_request(state)
                results.append(result)
            
            # Wait for next second
            batch_time = time.time() - batch_start
            if batch_time < 1.0:
                time.sleep(1.0 - batch_time)
        
        # Analyze results
        successful = sum(1 for r in results if 'error' not in r)
        failed = len(results) - successful
        
        print(f"Sustained load results:")
        print(f"  Total requests: {len(results)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Success rate: {successful/len(results)*100:.1f}%")
        
        return successful, failed
    
    def test_server_health(self):
        """Test server health with ping"""
        print("Testing server health...")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.host, self.port))
            
            # Send ping
            request = json.dumps({'ping': True}) + '\n'
            sock.send(request.encode('utf-8'))
            
            # Receive response
            response = sock.recv(4096).decode('utf-8')
            sock.close()
            
            result = json.loads(response.strip())
            
            if result.get('pong'):
                print("Server is healthy!")
                return True
            else:
                print("Server health check failed")
                return False
                
        except Exception as e:
            print(f"Server health check error: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Load test inference server')
    parser.add_argument('--host', type=str, default='localhost',
                       help='Server host')
    parser.add_argument('--port', type=int, default=5001,
                       help='Server port')
    parser.add_argument('--test', type=str, choices=['single', 'concurrent', 'sustained', 'health', 'all'],
                       default='all', help='Test type to run')
    parser.add_argument('--requests', type=int, default=10,
                       help='Number of requests for concurrent test')
    parser.add_argument('--workers', type=int, default=5,
                       help='Number of worker threads')
    parser.add_argument('--duration', type=int, default=30,
                       help='Duration for sustained test (seconds)')
    parser.add_argument('--rps', type=int, default=5,
                       help='Requests per second for sustained test')
    
    args = parser.parse_args()
    
    tester = LoadTester(args.host, args.port)
    
    if args.test == 'single' or args.test == 'all':
        tester.test_single_request()
        print()
    
    if args.test == 'concurrent' or args.test == 'all':
        tester.test_concurrent_requests(args.requests, args.workers)
        print()
    
    if args.test == 'sustained' or args.test == 'all':
        tester.test_sustained_load(args.duration, args.rps)
        print()
    
    if args.test == 'health' or args.test == 'all':
        tester.test_server_health()

if __name__ == '__main__':
    main()