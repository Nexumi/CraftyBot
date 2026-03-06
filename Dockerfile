FROM python:3.12.4-slim

RUN pip install -U py-cord requests

WORKDIR /home/user/app
COPY ./src ./

CMD [ "python", "-u", "main.py" ]
