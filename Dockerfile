FROM python:3.12.4-slim

RUN pip install -U py-cord==2.6.0 requests==2.32.3

WORKDIR /home/user/app
COPY ./src ./

CMD [ "python", "-u", "main.py" ]
