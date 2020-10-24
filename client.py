import socket
import subprocess

# Initialise hosts and ports
serverIP = "192.168.1.3"
serverPort = 9999

cmd = "hostname -I"
output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

clientIP = output.split()[0]
clientPort = 8888

# Connect to server
s = socket.socket()
s.connect((serverIP, serverPort))
print("Connected to server")

# Send image
print("Sending image")
f = open("image.jpg", "rb")
line = f.read(1024)
while (line):
    s.send(line)
    line = f.read(1024)

print("Image sent")

# Close connection
s.close()

# Create server to receive classification
s = socket.socket()
s.bind((clientIP, clientPort))
s.listen(1)
print("Accepting Connections")

# Accept connection
sc, address = s.accept()

# Receive response
print("Received connection")
line = sc.recv(1024)
print(line.decode())

# Close connection
sc.close()
