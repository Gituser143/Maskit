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

p = GPIO.PWM(servoPIN, 50)  # GPIO 17 for PWM with 50Hz
p.start(2.5)  # Initial position


def scanRFID():
    line = input("0 for inavlid ID, 1 for valid: ")
    if line == "1":
        return True
    else:
        return False


# Capture image with pi cam
def captureImage():
    os.system("rm -f image.jpg")
    cmd = "raspistill -q 100 -t 200 -o image.jpg"
    os.system(cmd)


# Send image to server
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


# Open door with servo motor
def openDoor():
    p.ChangeDutyCycle(12.5)
    time.sleep(5)
    p.ChangeDutyCycle(2.5)
    time.sleep(5)


def printMessage(type, message):
    if type == "LOG":
        print(bcolors.OKGREEN + message + bcolors.ENDC)

    elif type == "ERROR":
        print(bcolors.FAIL + bcolors.BOLD + message + bcolors.ENDC + bcolors.ENDC)

    else:
        print(bcolors.OKCYAN + bcolors.BOLD + message + bcolors.ENDC + bcolors.ENDC)


while(1):

    # Scan RFID tag
    validRFID = False
    try:
        validRFID = scanRFID()
    except:
        printMessage("ERROR", "[ERROR] Failed to scan RFID.")
        continue

    if not validRFID:
        break

    # Capture image
    try:
        captureImage()
    except:
        printMessage("ERROR", "[ERROR] Failed to capture image.")
        continue

    # Send image to server
    mask = -1
    try:
        mask = sendImage(serverIP, serverPort)
    except "ConnectionRefusedError":
        ip = input("Re enter IP")
        serverIP = ip.strip()
    except:
        printMessage("ERROR", "[ERROR] Failed to send image.")
        continue

    printMessage("CLASS", "Class: " + str(mask))

    # Restart
    if mask == -1:
        continue

    # Open door
    if mask == 1:
        try:
            openDoor()
            GPIO.cleanup()

        except:
            printMessage("ERROR", "[ERROR] Failed to open door.")
            continue
