import socket
import subprocess
import datetime

# Initialise hosts and ports
cmd = "hostname -I"
output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

serverIP = output.split()[0]
serverPort = 9999

clientPort = 8888

# Start server to receive image
s = socket.socket()
s.bind((serverIP, serverPort))
s.listen(10)  # Accepts up to 10 connections.

print("Listening for connections")

while True:

    # Accept connection
    sc, address = s.accept()

    # Get client hostname
    clientIp = address[0]

    print("Got connection from", clientIp)

    # Create file with name timestamp
    ct = datetime.datetime.now()
    filename = str(ct) + ".jpg"
    f = open(filename, 'wb')  # open in binary

    # receive data and write it to file
    line = sc.recv(1024)
    while (line):
        f.write(line)
        line = sc.recv(1024)
    f.close()
    print("Received image")

    # Close previous connection
    sc.close()

    # Run model on image
    print("Running classifier")
    cmd = "python3 detect_mask_image.py --image '" + filename + "'"
    output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
    print("Mask:", output)

    # Send output back to client
    print("Sending output")
    clientSock = socket.socket()
    clientSock.connect((clientIp, clientPort))
    clientSock.send(output.encode())
    clientSock.close()
