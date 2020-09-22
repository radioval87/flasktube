FROM ubuntu:16.04

LABEL Valentin Guniakov "radioval87@yandex.ru"

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev && \
    apt-get install -y sqlite3 libsqlite3-dev

COPY ./requirements.txt /requirements.txt

RUN pip3 install -r requirements.txt

COPY . /app

WORKDIR /app

ENTRYPOINT [ "python3" ]

CMD [ "./flasktube.py" ]