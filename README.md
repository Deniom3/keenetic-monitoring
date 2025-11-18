# Универсальный мониторинг устройств Keenetic

## Конфигурация

Поддерживаются следующие экспортеры метрик (можно включать/отключать в config.ini):

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

## Запуск с Docker

1. Обновите docker-compose.yml при необходимости
2. Запустите сервис:
```bash
docker-compose up -d
```

## Доступ к метрикам
- Prometheus: `http://localhost:9090`
- Конечная точка метрик: `http://localhost:9100/metrics`
- InfluxDB UI: `http://localhost:8086` (если включен)
