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

clientPort = 8888

# SSL configs
if not os.path.exists("cert.pem"):
    print(bcolors.FAIL + bcolors.BOLD + "[ERROR] Cannot find certfile 'cert.pem', please create one using openssl" + bcolors.ENDC + bcolors.ENDC)
    exit(1)

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.load_cert_chain(certfile="cert.pem", keyfile="cert.pem")

# Start server to receive image
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((serverIP, serverPort))
s.listen(10)  # Accepts up to 10 connections.

print(bcolors.OKGREEN + "Listening for connections on " + serverIP + bcolors.ENDC)

while True:

    # Accept connection
    sock, address = s.accept()

    # Wrap with SSL
    ssock = context.wrap_socket(sock, server_side=True)

    # Get client hostname
    clientIp = address[0]

    print(bcolors.OKGREEN + "Got connection from", clientIp + bcolors.ENDC)

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
    print(bcolors.OKGREEN + "Received image" + bcolors.ENDC)

    # Run model on image
    try:
        print(bcolors.OKGREEN + "Running classifier" + bcolors.ENDC)
        cmd = "python3 detect_mask_image.py --image '" + filename + "'"
        output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        print(bcolors.OKGREEN + "Mask: " + output + bcolors.ENDC)
    except:
        print(bcolors.FAIL + bcolors.BOLD + "[ERROR] Failed to process image, skipping" + bcolors.ENDC + bcolors.ENDC)
        ssock.send("-1".encode())
        ssock.close()
        continue

    # Send output back to client
    print(bcolors.OKGREEN + "Sending output" + bcolors.ENDC)
    ssock.send(output.encode())

    # Close connection
    ssock.close()
