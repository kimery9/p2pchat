import socket
import json

SECRET_KEY = "Iloveec528"
def discovery_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 8000))  # Bind to localhost on port 8000
    server.listen()

    clients = {}  # Dictionary to hold client usernames and addresses

    while True:
        client_socket, client_address = server.accept()
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            data_dict = json.loads(data)
            # Authentication check
            if data_dict.get('secret_key') != SECRET_KEY:
                print("Authentication failed")
                client_socket.close()
                continue  # Skip further processing for this connection
            username = data_dict.get('username', '')
            # Validate username
            if not username.isalnum() or len(username) > 20:
                print("Invalid username")
                client_socket.close()
                continue

            clients[username] = {'ip': client_address[0], 'port': data_dict['port']}
            client_socket.send(json.dumps(clients).encode('utf-8'))
        client_socket.close()

if __name__ == '__main__':
    print("Discovery Server is running...")
    discovery_server()
