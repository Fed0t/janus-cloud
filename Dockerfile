FROM python:3.10-buster

RUN apt update
RUN apt install -y ffmpeg
RUN update-ca-certificates

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN mkdir /home/code/
RUN mkdir /opt/recordings/

COPY . /home/code
WORKDIR /home/code
RUN pip install -r requirements.txt

RUN python setup.py build
RUN python setup.py install

ENV PYTHONUNBUFFERED=1

CMD ["janus-backup", "/home/code/conf/janus-backup.yml"]

