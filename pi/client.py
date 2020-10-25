import socket
import os
import ssl


# Initialise hosts and ports
serverIP = "192.168.1.3"
serverPort = 9999


def captureImage():
    os.system("rm -f image.jpg")
    cmd = "raspistill -q 100 -t 200 -o image.jpg"
    os.system(cmd)


def sendImage(serverIP, serverPort):

    # Connect to server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # SSL wrap
    ssock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLSv1)
    ssock.connect((serverIP, serverPort))
    print("Connected to server")

    # Send image
    print("Sending image")
    f = open("image.jpg", "rb")
    line = f.read(1024)
    while (line):
        ssock.send(line)
        line = f.read(1024)

    # Send finish message
    finish = "SENT FILE"
    ssock.send(finish.encode())
    print("Image sent")

    # Receive classification
    line = ssock.recv(1024)
    mask = line.decode()
    print("Message:", mask)

    # Close connection
    ssock.close()

    return int(mask)


while(1):
    # Scan RFID tag
    # validRFID = scanRFID()
    # if validRFID:
    #   Capture image
    #   captureImage()

    # Send image to server
    mask = sendImage(serverIP, serverPort)
    print(mask)

    # if Mask == -1
    #   Restart
    #   Continue

    # if mask == 1
    #   openDoor()

    break
