import socket
import os
import ssl
import RPi.GPIO as GPIO
import time
import MFRC522
import signal
import datetime
import threading

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


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
serverIP = "192.168.1.2"
serverPort = 9999

# Initialisation for servo motor
servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50)  # GPIO 17 for PWM with 50Hz
p.start(2.5)  # Initial position

validRFIDs = {}


def initRFIDs():
    with open("valid_rfids.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            rfid = line.strip()
            rfid, SRN = rfid.split(':')
            rfid = [i for i in rfid.split(",")]
            rfid = ",".join(rfid)
            validRFIDs[rfid] = SRN

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


def scanRFID():

    global continueReading
    MIFAREReader = MFRC522.MFRC522()

    # Scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    global currentUSER
    currentUSER = ''
    if status == MIFAREReader.MI_OK:

        printMessage("LOG", "Scanned Card")
        # Get the UID of the card
        (status, uid) = MIFAREReader.MFRC522_Anticoll()
        uid = [str(i) for i in uid]
        uid = ",".join(uid)

        # Authenticate
        if uid in validRFIDs:
            printMessage("VALID", "Valid RFID card")
            printMessage("LOG:", validRFIDs[uid])
            currentUSER = validRFIDs[uid]
            return True
        else:
            printMessage("ERROR", "Invalid RFID card")
            return False


def logToCloud(USER):

    myMQTTClient = AWSIoTMQTTClient("clientid")
    myMQTTClient.configureEndpoint("a26zkbv9c1bz6c-ats.iot.eu-west-2.amazonaws.com", 8883)
    myMQTTClient.configureCredentials("/home/pi/Maskit/pi/root-ca.pem","/home/pi/Maskit/pi/private.pem.key", "/home/pi/Maskit/pi/certificate.pem.crt")
    myMQTTClient.configureOfflinePublishQueueing(-1)
    myMQTTClient.configureDrainingFrequency(2)
    myMQTTClient.configureConnectDisconnectTimeout(10)
    myMQTTClient.configureMQTTOperationTimeout(5)

    myMQTTClient.connect()

    printMessage("LOG", "Publishing message")

    message = dict()

    message["user"] = USER
    message["time"] = str(datetime.datetime.now())

    myMQTTClient.publish(
        topic="home/Maskit",
        QoS=1,
        payload=str(message)
    )


def cleanup(signal, frame):
    global continueReading
    GPIO.cleanup()
    continueReading = False


signal.signal(signal.SIGINT, cleanup)

initRFIDs()
continueReading = True
currentUSER = ''

while continueReading:

    # Scan RFID
    try:
        isValid = scanRFID()
        if not isValid:
            continue
    except:
        printMessage("ERROR", "[ERROR] Failed to scan RFID.")
        continue

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
    except ConnectionRefusedError:
        printMessage("ERROR", "Could not connect to host " + serverIP)
        ip = input("Re enter IP: ")
        serverIP = ip.strip()
        continue
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
            logToCloud(currentUSER)

            openDoor()
            GPIO.cleanup()

        except:
            printMessage("ERROR", "[ERROR] Failed to open door.")
            continue
