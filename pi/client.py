import socket
import subprocess
import os

# Initialise hosts and ports
serverIP = "192.168.1.3"
serverPort = 9999

cmd = "hostname -I"
output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

clientIP = output.split()[0]
clientPort = 8888


def captureImage():
    os.system("rm -f image.jpg")
    cmd = "raspistill -q 100 -t 200 -o image.jpg"
    os.system(cmd)


def sendImage(serverIP, serverPort):

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


def receiveClass(clientIP, clientPort):

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
    mask = line.decode()
    print("Message:", mask)

    # Close connection
    sc.close()

    return mask


while(1):
    # Scan RFID

    # If RFID is valid
    # Capture image
    captureImage()

    # Send image to server
    sendImage(serverIP, serverPort)

    # Recive classification
    mask = receiveClass(clientIP, clientPort)

    # If mask
    # Rotate motor to open door
