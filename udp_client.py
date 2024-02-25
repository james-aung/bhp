import socket

target_host = "127.0.0.1"
target_port = 9997

# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # The only difference between this and the TCP example is that we use SOCK_DGRAM instead of SOCK_STREAM. This is the socket type for UDP connections.

# send some data    
client.sendto(b"AAABBBCCC", (target_host, target_port)) # The sendto() method is used to send data. The first parameter is the data, and the second parameter is the target address. The target address is a tuple containing the IP address and the port.

# receive some data
data, addr = client.recvfrom(4096) # The recvfrom() method is used to receive data. The return value is a tuple containing the data and the details of the remote host.

print(data.decode())
client.close()