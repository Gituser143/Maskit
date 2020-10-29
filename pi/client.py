import socket
import os
import ssl
import RPi.GPIO as GPIO
import time

# Colours for logs and messages
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Initialise hosts and ports
serverIP = "192.168.1.3"
serverPort = 9999

# Initialisation for servo motor
servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
p.start(2.5) # Initialization


def openDoor():
    p.ChangeDutyCycle(12.5)
    time.sleep(5)
    p.ChangeDutyCycle(2.5)


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
    print(bcolors.OKGREEN + "Connected to server" + bcolors.ENDC)

    # Send image
    print(bcolors.OKGREEN + "Sending image" + bcolors.ENDC)
    f = open("image.jpg", "rb")
    line = f.read(1024)
    while (line):
        ssock.send(line)
        line = f.read(1024)

    # Send finish message
    finish = "SENT FILE"
    ssock.send(finish.encode())
    print(bcolors.OKGREEN + "Image sent" + bcolors.ENDC)

    # Receive classification
    line = ssock.recv(1024)
    mask = line.decode()

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
    mask = -1
    try:
        mask = sendImage(serverIP, serverPort)
    except:
        print(bcolors.FAIL + bcolors.BOLD + "[ERROR] Failed to send image." + bcolors.ENDC + bcolors.ENDC)
        # Continue in production, exit only in dev
        exit(1)
        # continue

    print(bcolors.OKCYAN + bcolors.BOLD + "Class: " + str(mask) + bcolors.ENDC + bcolors.ENDC)

    #   Restart
    if mask == -1:
        continue

    #   openDoor()
    if mask == 1:
        openDoor()

    break
