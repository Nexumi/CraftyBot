FROM python:3.10.12-slim

RUN pip install -U py-cord requests

WORKDIR /home/user/app
COPY ./src ./

CMD [ "python", "-u", "main.py" ]
