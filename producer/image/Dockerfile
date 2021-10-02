FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY config.yml ./
COPY oanda_producer.py ./

CMD [ "python", "./oanda_producer.py" ]
