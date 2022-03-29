FROM python:3.9-alpine3.14


RUN mkdir /home/code/
RUN mkdir /opt/recordings/

COPY . /home/code
WORKDIR /home/code
RUN apk update && apk add gcc g++ musl-dev  libffi-dev file make ffmpeg

RUN pip install -r requirements.txt

RUN python setup.py build
RUN python setup.py install

ENV PYTHONUNBUFFERED=1

RUN sed -i 's/redis:\/\//rediss:\/\//' /usr/local/lib/python3.9/site-packages/januscloud/proxy/main.py 
RUN sed -i 's/redis:\/\//rediss:\/\//' /usr/local/lib/python3.9/site-packages/januscloud/proxy/plugin/p2pcall.py
RUN sed -i 's/redis:\/\//rediss:\/\//' /usr/local/lib/python3.9/site-packages/januscloud/proxy/plugin/videocall.py
RUN sed -i 's/redis:\/\//rediss:\/\//' /usr/local/lib/python3.9/site-packages/januscloud/proxy/plugin/videoroom.py

CMD ["janus-backup", "/home/code/conf/janus-backup.yml"]

