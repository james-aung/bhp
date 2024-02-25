import socket
import threading

IP = "0.0.0.0"
PORT = 9998

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a new socket object, same as we do for creating a client
    server.bind((IP, PORT))
    server.listen(5) # This time, we call the listen() method. The argument is the number of connections the server can handle at once.
    print(f"[*] Listening on {IP}:{PORT}")

    while True:
        client, address = server.accept() # Returns a new socket object and the address of the client. The new socket object is used to communicate with the client.
        print(f"[*] Accepted connection from: {address[0]}:{address[1]}")
        # Spin up a new thread to handle the new client
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f"[*] Received: {request.decode()}")
        sock.send(b"Hi mom!")

if __name__ == "__main__":
    main()