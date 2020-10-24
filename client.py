import socket

# Initialise hosts and ports
serverIP = "localhost"
serverPort = 9999

clientPort = 8888

# Connect to server
s = socket.socket()
s.connect((serverIP, serverPort))

# Send image
f = open("image.jpg", "rb")
line = f.read(1024)
while (line):
    s.send(line)
    line = f.read(1024)

# Close connection
s.close()

# Create server to receive classification
s = socket.socket()
s.bind(("localhost", clientPort))
s.listen(1)

# Accept connection
sc, address = s.accept()

# Receive response
line = sc.recv(1024)
print(line.decode())

# Close connection
sc.close()
