import socket
import subprocess
import datetime
import ssl
import os


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
cmd = "hostname -I"
output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

serverIP = output.split()[0]
serverPort = 9999


def printMessage(type, message):
    if type == "LOG":
        print(bcolors.OKGREEN + message + bcolors.ENDC)

    elif type == "ERROR":
        print(bcolors.FAIL + bcolors.BOLD + message + bcolors.ENDC + bcolors.ENDC)

    else:
        print(bcolors.OKCYAN + bcolors.BOLD + message + bcolors.ENDC + bcolors.ENDC)


# SSL configs
if not os.path.exists("cert.pem"):
    printMessage("ERROR", "[ERROR] Cannot find certfile 'cert.pem', please create one using openssl")
    exit(1)

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.load_cert_chain(certfile="cert.pem", keyfile="cert.pem")

# Start server to receive image
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((serverIP, serverPort))
s.listen(10)  # Accepts up to 10 connections.

printMessage("LOG", "Listening for connections on " + str(serverIP))

while True:

    # Accept connection
    sock, address = s.accept()

    # Wrap with SSL
    ssock = context.wrap_socket(sock, server_side=True)

    # Get client hostname
    clientIp = address[0]

    printMessage("LOG", "Got connection from " + str(clientIp))

    # Create file with name timestamp
    ct = datetime.datetime.now()
    filename = str(ct) + ".jpg"

    # open in binary
    f = open(filename, 'wb')

    # receive data and write it to file
    line = ssock.recv(1024)
    while (line):
        try:
            if line.decode() == "SENT FILE":
                break
        except:
            pass
        f.write(line)
        line = ssock.recv(1024)
    f.close()
    printMessage("LOG", "Received image")

    # Run model on image
    try:
        printMessage("LOG", "Running classifier")
        cmd = "python3 detect_mask_image.py --image '" + filename + "'"
        output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        printMessage("LOG", "Mask: " + str(output))
    except:
        printMessage("ERROR", "[ERROR] Failed to process image, skipping")
        ssock.close()
        continue

    # Send output back to client
    printMessage("LOG", "Sending output")
    ssock.send(output.encode())

    # Close connection
    ssock.close()
