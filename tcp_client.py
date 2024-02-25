import socket
import re

def make_request(host, port, path="/"):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n"
    client.send(request.encode())
    response = client.recv(4096)
    client.close()
    return response

target_host = "0.0.0.0"
target_port = 9998
initial_path = "/"

# Make the initial request
response = make_request(target_host, target_port, initial_path)

print(response.decode())