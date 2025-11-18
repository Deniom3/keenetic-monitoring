# Keenetic Monitoring with Prometheus/InfluxDB

## Configuration

By default both exporters are disabled. Enable them in config.ini:

```ini
[influx2]
enabled=true
url=http://<influx_ip>:8086
org=keenetic
token=<token>
bucket=keenetic

[prometheus]
enabled=true
expose_port=9100
```

## Running with Docker

1. For Prometheus, update docker-compose.yml:
```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - 9090:9090
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
```

2. Start services:
```bash
docker-compose up -d
```

## Access Metrics
- Prometheus: `http://localhost:9090`
- Metrics endpoint: `http://localhost:9100/metrics`
- InfluxDB UI: `http://localhost:8086`
