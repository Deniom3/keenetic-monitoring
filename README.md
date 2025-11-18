# Универсальный мониторинг устройств Keenetic

## Конфигурация

Настройки задаются через переменные окружения в файле `.env`:

```
KEENETIC_ADMIN_ENDPOINT=http://192.168.0.1:81
KEENETIC_SKIP_AUTH=true
KEENETIC_LOGIN=admin
KEENETIC_PASSWORD=

COLLECTOR_INTERVAL_SEC=120

PROMETHEUS_ENABLED=true
PROMETHEUS_EXPOSE_PORT=9100

INFLUX2_ENABLED=false
INFLUX2_URL=http://<influx_ip>:8086
INFLUX2_ORG=keenetic
INFLUX2_TOKEN=<token>
INFLUX2_BUCKET=keenetic
```

## Запуск с Docker

1. Создайте файл `.env` с настройками
2. Запустите сервис:
```bash
docker-compose up -d --build
```

## Доступ к метрикам
- Prometheus: `http://localhost:9090`
- Конечная точка метрик: `http://localhost:9100/metrics`
- InfluxDB UI: `http://localhost:8086` (если включен)

## Миграция с config.ini
Для перехода с config.ini на .env:
1. Перенесите настройки из config.ini в .env
2. Удалите монтирование config.ini из docker-compose.yml
3. Пересоберите контейнер с флагом --build
