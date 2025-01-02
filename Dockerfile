FROM python:latest
WORKDIR /app
COPY . /app
EXPOSE 5000 5000
#RUN apk update && apk add python3-dev gcc libc-dev libffi-dev libwebp-dev
#RUN apk add jpeg-dev zlib-dev ffmpeg
#RUN apk add --virtual .build-deps build-base linux-headers 
#RUN python3 -m pip install --upgrade pip && pip3 install -r requirements.txt
RUN pip install -r requirements.txt
CMD python3 web/app.py
