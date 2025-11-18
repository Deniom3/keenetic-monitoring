import logging
from flask import Flask, Response
from threading import Thread
from typing import List, Dict
import time
import json
from waitress import serve

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PrometheusWriter:
    def __init__(self, config: Dict[str, str]):
        self._metrics = {}  # Словарь для хранения метрик
        self._app = Flask(__name__)
        self._port = int(config.get('expose_port', 9100))
        
        @self._app.route('/metrics')
        def metrics():
            # Возвращаем все накопленные метрики
            return Response('\n'.join(self._metrics.values()), mimetype='text/plain')

        self._server_thread = Thread(target=self._run_server)
        self._server_thread.daemon = True
        self._server_thread.start()

    def _run_server(self):
        serve(self._app, host='0.0.0.0', port=self._port)

    def write_metrics(self, metrics: List[Dict]):
        """Convert metrics to Prometheus format and store/update them"""
        current_time = int(time.time() * 1000)  # Текущая метка времени
        
        for metric in metrics:
            # Формируем имя метрики, сохраняя префикс но убирая пробелы
            name = metric['measurement'].replace(' ', '_').replace('.', '_')
            labels = ','.join(
                f'{k}="{v.replace(" ", "_") if v is not None else ""}"'  # Заменяем пробелы и обрабатываем None
                for k, v in metric['tags'].items()
            )
            if labels:
                labels = f"{{{labels}}}"
            else:
                labels = ""
                
            for field, value in metric['fields'].items():
                # Создаем уникальный ключ для метрики (имя + лейблы)
                metric_key = f'{name}_{field}{labels}'
                # Обновляем метрику только со значением (без timestamp)
                self._metrics[metric_key] = f'{metric_key} {value}'
                logger.debug(f"Updated metric: {metric_key}")
                
        logger.info(f"Processed {len(metrics)} metrics, total stored: {len(self._metrics)}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass