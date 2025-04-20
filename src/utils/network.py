# filepath: /Users/chiragvijayvergiya/Desktop/chirag/dc-p/parallel-web-scraper/src/utils/network.py
import socket
import threading
import pickle
import time

class MessageServer:
    """Simple server for task distribution"""
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.running = False
        
    # Update the start method in MessageServer
    def start(self):
        try:
            # Allow port reuse to avoid "address already in use" errors
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            print(f"Server started on {self.host}:{self.port}")
        
            # Accept connections in a separate thread
            threading.Thread(target=self._accept_connections, daemon=True).start()
            return True
        except Exception as e:
            print(f"Error starting server: {e}")
            return False
        
    def _accept_connections(self):
        while self.running:
            try:
                client, address = self.socket.accept()
                print(f"New connection from {address}")
                self.clients.append(client)
                
                # Start a thread to handle this client
                threading.Thread(target=self._handle_client, 
                                args=(client, address), daemon=True).start()
            except:
                if self.running:
                    print("Error accepting connection")
        
    def _handle_client(self, client, address):
        while self.running:
            try:
                # Receive message length first
                length_data = client.recv(4)
                if not length_data:
                    break
                    
                message_length = int.from_bytes(length_data, byteorder='big')
                
                # Receive message data
                message_data = b""
                while len(message_data) < message_length:
                    chunk = client.recv(min(1024, message_length - len(message_data)))
                    if not chunk:
                        raise RuntimeError("Socket connection broken")
                    message_data += chunk
                
                # Deserialize message
                message = pickle.loads(message_data)
                
                # Process message (override in subclass)
                response = self.process_message(message, client)
                
                # Send response if any
                if response:
                    self.send_message(client, response)
                    
            except Exception as e:
                print(f"Error handling client {address}: {e}")
                break
                
        # Remove client when done
        if client in self.clients:
            self.clients.remove(client)
        client.close()
    
    def process_message(self, message, client):
        """Override this method to process received messages"""
        return {"status": "received"}
    
    def send_message(self, client, message):
        """Send message to a specific client"""
        data = pickle.dumps(message)
        length = len(data).to_bytes(4, byteorder='big')
        client.sendall(length + data)
        
    def broadcast(self, message):
        """Send message to all connected clients"""
        for client in self.clients[:]:  # Copy to avoid modification during iteration
            try:
                self.send_message(client, message)
            except:
                # Remove failed client
                self.clients.remove(client)
                
    def stop(self):
        self.running = False
        for client in self.clients:
            client.close()
        self.socket.close()
        print("Server stopped")


class MessageClient:
    """Client to connect to the coordinator"""
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        
    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            self.connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
            
    def send_message(self, message):
        """Send message to server and get response"""
        if not self.connected:
            raise ConnectionError("Not connected to server")
            
        data = pickle.dumps(message)
        length = len(data).to_bytes(4, byteorder='big')
        
        self.socket.sendall(length + data)
        
        # Receive response length
        length_data = self.socket.recv(4)
        if not length_data:
            raise ConnectionError("Connection closed by server")
            
        message_length = int.from_bytes(length_data, byteorder='big')
        
        # Receive response data
        message_data = b""
        while len(message_data) < message_length:
            chunk = self.socket.recv(min(1024, message_length - len(message_data)))
            if not chunk:
                raise RuntimeError("Socket connection broken")
            message_data += chunk
            
        # Deserialize response
        return pickle.loads(message_data)
        
    def disconnect(self):
        if self.connected:
            self.socket.close()
            self.connected = False