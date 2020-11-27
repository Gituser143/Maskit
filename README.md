Maskit
======

A smart COVID-19 mask detection system built for use in public workspaces!

Prerequisites
=============

-	Raspberry Pi along with Pi Cam module.

Hardware Setup
==============

-	Connect the pi camera module

-	Connect the Pi to the same network the server runs on.

How to use?
===========

Clone the repo.

```
git clone https://github.com/Gituser143/Maskit.git
```

### NOTE: Place the `server/` directory in the server and the `pi/` directory on a raspberry pi.

Server configuration
--------------------

Navigate into `server/` on the server and generate an SSL certificate. Fill in the required fields.

```
cd server
openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout cert.pem
```

The above command places a `cert.pem` in your local directory.

Install requirements on server.

```
pip3 install -r requirements.txt
```

Start the server.

```
python3 server.py
```

Client configuration
--------------------

Navigate into the `pi/` directory on a raspberry pi.

```
cd pi
```

Install requirements on pi.

```
pip3 install -r requirements.txt
```

Start client.

```
python3 client.py
```

### Voila! That should be all!