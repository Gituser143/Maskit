FROM ubuntu

WORKDIR /app

COPY ./ ./

RUN apt update

RUN apt install python3-pip -y

RUN pip3 install -r requirements.txt

CMD ["python3", "detect_mask_image.py", "--image", "image.jpg"]
