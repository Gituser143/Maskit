import socket
import subprocess
import datetime

s = socket.socket()
s.bind(("localhost", 9999))
s.listen(10)  # Accepts up to 10 connections.

i = 1
while True:
    sc, address = s.accept()

    print(address)
    ct = datetime.datetime.now()
    filename = str(ct) + ".jpg"
    f = open(filename, 'wb')  # open in binary
    l = 1
    while (l):
        # receive data and write it to file
        l = sc.recv(1024)
        while (l):
            f.write(l)
            l = sc.recv(1024)
    f.close()

    # Run model on image
    cmd = "python3 detect_mask_image.py --image '" + filename + "'"
    output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

    # Send output back to client

    sc.close()

s.close()
