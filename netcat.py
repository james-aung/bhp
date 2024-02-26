import argparse
import socket
import shlex # Used to split the command string into a list of arguments
import subprocess
import sys
import textwrap
import threading

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT) # check_output() runs a command on the local operating system and returns the output as a byte string. 
    return output.decode()

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()
    
    def send(self):
        self.socket.connect((self.args.target, self.args.port)) # We connect to the target IP and port using the connect() method.
        if self.buffer:
            self.socket.send(self.buffer) # If we have a buffer, we send it to the target.

        try:
            while True: # We then enter a loop where we receive data from the target and print it to the screen. We also wait for input from the user and send it to the target. Until the user terminates the program.
                recv_len = 1
                response = ""
                while recv_len:
                    data = self.socket.recv(4096) # We receive data from the target using the recv() method in chunks of 4096 bytes.
                    recv_len = len(data) 
                    response += data.decode() # We decode the data and add it to the response string.
                    if recv_len < 4096: # If the length of the data is less than 4096, we know we have received all the data and we can break out of the loop.
                        break
                if response:
                    print(response)
                    buffer = input("") # We print the response to the screen and then wait for input from the user.
                    buffer += "\n"
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print("User terminated.")
            self.socket.close()
            sys.exit()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5) 
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()

    def handle(self, client_socket):
        if self.args.execute: # If the -e option is specified, we execute the command and send the output to the target.
            output = execute(self.args.execute)
            client_socket.send(output.encode()) # We send the output back to the target.
        elif self.args.upload: # If the -u option is specified, we receive data from the target and write it to a file.
            file_buffer = b""
            while True:
                data = client_socket.recv(1024)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload, "wb") as f: # We then write the data to a file. wb means write binary
                f.write(file_buffer) 
            message = f"Saved file {self.args.upload}"
            client_socket.send(message.encode())
        elif self.args.command: # If the -c option is specified, we enter a loop where we receive commands from the target and execute them on the local operating system.
            cmd_buffer = b""
            while True:
                try:
                    client_socket.send(b"BHP: #> ")
                    while "\n" not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(1024)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b""
                except Exception as e:
                    print(f"Server killed {e}")
                    self.socket.close()
                    sys.exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="BHP Net Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""Example:
            netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
            netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
            netcat.py -t 192.168.1.108 -p 5555 -l -e="cat /etc/passwd" # execute command
            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135
            netcat.py -t 192.168.1.108 -p 5555 # connect to server
        """)
    )
    parser.add_argument("-c", dest="command", help="command shell", action="store_true")
    parser.add_argument("-e", dest="execute", help="execute a command")
    parser.add_argument("-l", dest="listen", help="listen", action="store_true")
    parser.add_argument("-p", dest="port", type=int, default=5555, help="specified port")
    parser.add_argument("-t", dest="target", help="specified IP", default="192.168.1.203")
    parser.add_argument("-u", dest="upload", help="upload file")
    args = parser.parse_args()
    if args.listen:
        buffer = "" # If the -l option is specified, we will listen for incoming connections and print any data we receive to the screen.
        print("Listening")
    else:
        buffer = sys.stdin.read()
    
    nc = NetCat(args, buffer.encode())
    nc.run()