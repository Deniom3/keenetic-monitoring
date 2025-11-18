FROM python:3.8-alpine AS dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.8-alpine AS build-image
COPY --from=dependencies /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages

COPY value_normalizer.py keenetic_monitoring.py influxdb_writter.py keenetic_api.py prometheus_writter.py /home/
ENV PYTHONPATH=/home
COPY config/metrics.json /home/config/metrics.json

CMD [ "python", "-u", "/home/keenetic_monitoring.py" ]
