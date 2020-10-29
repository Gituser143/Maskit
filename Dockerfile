FROM tensorflow/tensorflow

WORKDIR /app

COPY ./server ./

RUN pip3 install -r /app/requirements.txt

RUN apt update && apt install -y libsm6 libxext6

RUN apt-get install -y libxrender-dev

CMD ["python3", "server.py"]
