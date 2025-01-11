import socket
 
UDP_IP = socket.gethostbyname(socket.gethostname())
UDP_PORT = 5005
UDP_SELF_PORT = 5000
MESSAGE = b'Hello, World!'

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)
 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_SELF_PORT))

sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
