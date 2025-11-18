[![Latest Release][version-image]][version-url]
[![Docker Pulls][dockerhub-image]][dockerhub-url]
[![Build Status][gh-actions-image]][gh-actions-url]

# Universal monitoring of Keenetic devices using Prometheus or InfluxDB

[Русская версия](README.ru.md) | [English version](README.en.md)

## Quick Start (Docker Compose)

```yaml
services:
  keenetic-monitoring:
    container_name: keenetic-monitoring
    image: deniom3/keenetic-monitoring:latest
    restart: unless-stopped
    ports:
      - '9100:9100' # Prometheus метрики
    env_file:
      - .env
```

## Environment setup

Create a .env file with the following settings:

```
KEENETIC_ADMIN_ENDPOINT=http://192.168.0.1:81
KEENETIC_SKIP_AUTH=true
KEENETIC_LOGIN=user
KEENETIC_PASSWORD=password

# Metrics collection interval (seconds)
COLLECTOR_INTERVAL_SEC=120

# Prometheus Settings
PROMETHEUS_ENABLED=true
PROMETHEUS_EXPOSE_PORT=9100

# InfluxDB Settings (optional)
INFLUX2_ENABLED=false
INFLUX2_URL=http://influxdb:8086
INFLUX2_ORG=keenetic
INFLUX2_TOKEN=token
INFLUX2_BUCKET=keenetic
```

## Configuring the Keenetic Router

### 1. Creating an API User
1. Go to "Users and Access" → "Create User"
2. Enable access to the "Web Interface"
3. Disable "Prevent saving system settings"
4. Save the user with a strong password

### 2. Alternatively, configure the API
1. Go to "Network Rules" → "Port Forwarding"
2. Add a new rule:
- Input: Other destination
- IP address: Your network IP (e.g., 192.168.1.0)
- Subnet mask: 255.255.255.0
- Output: This Keenetic
- Open port: 79
- Destination port: 81

### 3. Configure metrics (optional)
You can copy and edit the `config/metrics.json` file to configure the metrics collected.

[version-image]: https://img.shields.io/github/v/release/Deniom3/keenetic-monitoring?style=for-the-badge
[version-url]: https://github.com/Deniom3/keenetic-monitoring/releases

[gh-actions-image]: https://img.shields.io/github/actions/workflow/status/Deniom3/keenetic-monitoring/docker-publish.yml?style=for-the-badge
[gh-actions-url]: https://github.com/Deniom3/keenetic-monitoring/actions

[dockerhub-image]: https://img.shields.io/docker/pulls/deniom3/keenetic-monitoring?label=DockerHub%20Pulls&style=for-the-badge
[dockerhub-url]: https://hub.docker.com/r/deniom3/keenetic-monitoring
