import socket
import subprocess
import datetime

# Initialise hosts and ports
serverIP = "localhost"
serverPort = 9999

clientPort = 8888

# Start server to receive image
s = socket.socket()
s.bind((serverIP, serverPort))
s.listen(10)  # Accepts up to 10 connections.

i = 1
while True:

    # Accept connection
    sc, address = s.accept()

    # Get client hostname
    clientIp = address[0]

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

    # Close previous connection
    sc.close()

    # Run model on image
    cmd = "python3 detect_mask_image.py --image '" + filename + "'"
    output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
    print("Mask:", output)

    # Send output back to client
    clientSock = socket.socket()
    clientSock.connect((clientIp, clientPort))
    clientSock.send(output.encode())
    clientSock.close()
