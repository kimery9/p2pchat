import socket
import threading
import json
import os


class P2PClient:
    def __init__(self, username):
        self.username = username
        self.discovery_server_ip = '127.0.0.1'
        self.discovery_server_port = 8000
        self.peers = {}
        self.offline_messages = {}

        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.bind(('127.0.0.1', 0))  # Automatically assigns a free port
        self.listen_port = self.listen_socket.getsockname()[1]

    def register_with_server(self):
        # Register client with the discovery server and retrieve the list of peers
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.discovery_server_ip, self.discovery_server_port))
        registration_info = {"username": self.username, "port": self.listen_port}
        self.socket.send(json.dumps(registration_info).encode('utf-8'))
        self.peers = json.loads(self.socket.recv(1024).decode('utf-8'))
        self.socket.close()

    def refresh_peers(self):
        # Refresh the list of peers from the server
        self.register_with_server()
        print("Updated peer list:", self.peers)
        self.synchronize_offline_messages()

    def store_offline_message(self, peer_username, message):
        # Store the message for the offline peer
        if peer_username not in self.offline_messages:
            self.offline_messages[peer_username] = []
        self.offline_messages[peer_username].append(message)
        print(f"Stored message for {peer_username} who is offline.")

    def synchronize_offline_messages(self):
        # Send any messages that were stored while a peer was offline
        for peer_username in list(self.offline_messages.keys()):
            if peer_username in self.peers:
                for message in self.offline_messages[peer_username]:
                    self.send_message(peer_username, message)
                del self.offline_messages[peer_username]  # Clear stored messages after sending

    def listen_for_connections(self):
        self.listen_socket.listen()
        print(f"{self.username} is listening for connections on port {self.listen_port}")

        while True:
            peer_socket, _ = self.listen_socket.accept()
            message = peer_socket.recv(1024).decode('utf-8')
            print(f"Message from {peer_socket.getpeername()}: {message}")
            peer_socket.close()

    def send_message(self, peer_username, message):
        peer_info = self.peers.get(peer_username)
        if peer_info:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer_socket:
                peer_socket.connect((peer_info['ip'], peer_info['port']))
                peer_socket.send(message.encode('utf-8'))
            print(f"Message sent to {peer_username}.")
        else:
            self.store_offline_message(peer_username, message)

    def start_chat(self):
        self.refresh_peers()  # Ensure we have the latest list of peers
        peer_username = input("Enter the username of the peer you want to chat with: ")
        if peer_username in self.peers:
            print(f"Starting chat with {peer_username}. Type /quit to end the chat.")
            while True:
                message = input("Enter your message (/quit to end): ")
                if message == "/quit":
                    break
                self.send_message(peer_username, message)
        else:
            print(f"Could not find user {peer_username}. They might be offline.")
            while True:
                message = input(f"Enter your message for {peer_username} (/quit to end): ")
                if message == "/quit":
                    break
                self.store_offline_message(peer_username, message)

    def start(self):
        threading.Thread(target=self.listen_for_connections).start()
        self.register_with_server()
        try:
            while True:
                self.start_chat()
        except KeyboardInterrupt:
            print("Chat client exited.")
        finally:
            self.listen_socket.close()


if __name__ == '__main__':
    username = input("Enter your username: ")
    client = P2PClient(username)
    client.start()
