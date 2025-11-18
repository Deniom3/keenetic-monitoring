# Универсальный мониторинг устройств Keenetic с использование Prometheus или InfluxDB

## Быстрый старт (Docker Compose)

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

## Настройка окружения

Создайте файл `.env` с настройками:

```
KEENETIC_ADMIN_ENDPOINT=http://192.168.0.1:81
KEENETIC_SKIP_AUTH=user
KEENETIC_LOGIN=admin # Опционально
KEENETIC_PASSWORD=пароль # Опционально

# Интервал сбора метрик (секунды)
COLLECTOR_INTERVAL_SEC=120  

# Настройки Prometheus
PROMETHEUS_ENABLED=true
PROMETHEUS_EXPOSE_PORT=9100

# Настройки InfluxDB (опционально)
INFLUX2_ENABLED=false
INFLUX2_URL=http://influxdb:8086
INFLUX2_ORG=keenetic
INFLUX2_TOKEN=токен
INFLUX2_BUCKET=keenetic
```

## Настройка роутера Keenetic

### 1. Создание пользователя API
1. Перейдите в "Пользователи и доступ" → "Создать пользователя"
2. Включите доступ к "Веб-интерфейсу"
3. Отключите "Запретить сохранение системных настроек"
4. Сохраните пользователя с надежным паролем

### 2. Альтернативный вариант - настройка API
1. Перейдите в "Правила сети" → "Проброс портов"
2. Добавьте новое правило:
   - Вход: Другое назначение
   - IP-адрес: Ваш сетевой IP (например, 192.168.1.0)
   - Маска подсети: 255.255.255.0
   - Выход: Этот Keenetic
   - Открыть порт: 79
   - Порт назначения: 81

### 3. Настройка метрик (опционально)
Вы можете скопировать и отредактировать файл `config/metrics.json` для настройки собираемых метрик.
