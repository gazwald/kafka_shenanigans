FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY oanda_consumer.py ./

CMD [ "python", "./oanda_consumer.py" ]
