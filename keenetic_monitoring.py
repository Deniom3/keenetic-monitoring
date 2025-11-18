import configparser
import json
import logging
import os
import time
from typing import Dict, List

from jsonpath_rw import parse

from influxdb_writter import InfuxWriter
from prometheus_writter import PrometheusWriter
from keenetic_api import KeeneticClient, KeeneticApiException
from value_normalizer import normalize_value

logging.basicConfig(level='INFO', format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s')


def json_path_init(paths: Dict[str, str]):
    queries = {}

    for pathName, path in paths.items():
        if path == "~":
            queries[pathName] = path
        else:
            queries[pathName] = parse(path)

    return queries


class KeeneticCollector(object):

    def __init__(self, keenetic_client: KeeneticClient, metric_configuration: Dict[str, object]):
        self._keenetic_client = keenetic_client
        self._command: str = metric_configuration['command']
        self._params = metric_configuration.get('param', {})
        self._root = parse(metric_configuration['root'])
        self._tags = json_path_init(metric_configuration['tags'])
        self._values = json_path_init(metric_configuration['values'])

    def collect(self) -> List[dict]:
        try:
            response = self._keenetic_client.metric(self._command, self._params)
        except KeeneticApiException as e:
            logging.warning(f"Skipping metric '{self._command}' collection. Reason keenetic api exception, "
                            f"status: {e.status_code}, response: {e.response_text}")
            return []

        roots = self._root.find(response)
        metrics = []
        start_time = time.time_ns()

        for root in roots:
            tags = self._params.copy()
            values = {}

            for tagName, tagPath in self._tags.items():
                if tagPath == '~':
                    tags[tagName] = root.path.fields[0]
                elif str(tagPath).startswith('`parent`'):
                    full_path = root.full_path.child(tagPath)
                    tags[tagName] = self.get_first_value(full_path.find(response))
                else:
                    tags[tagName] = self.get_first_value(tagPath.find(root.value))

            # Пропускаем некорректные записи
            if (self._command == "interface" and (tags.get('description') is None and tags.get('address') is None)) or \
               (self._command == "processes" and (tags.get('name') is None or tags.get('pid') == -1)):
                continue

            for valueName, valuePath in self._values.items():
                value = self.get_first_value(valuePath.find(root.value))
                if value is not None:
                    values[valueName] = normalize_value(value)

            if values.__len__() == 0:
                logging.debug(f"No values collected for command: {self._command}, tags: {tags}")
                continue

            metric = self.create_metric(self._command, tags, values)
            logging.debug(f"Collected metric: {json.dumps(metric)}")
            metrics.append(metric)

        metrics.append(
            self.create_metric("collector", {"command": self._command}, {"duration": (time.time_ns() - start_time)}))

        return metrics

    @staticmethod
    def create_metric(measurement, tags, values):
        return {
            "measurement": measurement,
            "tags": tags,
            "time": time.time_ns(),
            "fields": values
        }

    @staticmethod
    def get_first_value(array):
        if array and len(array) > 0:
            return array[0].value
        else:
            return None


if __name__ == '__main__':
    logging.info("\n\n" + "  _  __                    _   _         _____      _ _           _             \n | |/ /                   | | (_)       / ____|    | | |         | |            \n | ' / ___  ___ _ __   ___| |_ _  ___  | |     ___ | | | ___  ___| |_ ___  _ __     \n |  < / _ \/ _ \ '_ \ / _ \ __| |/ __| | |    / _ \| | |/ _ \/ __| __/ _ \| '__|\n | . \  __/  __/ | | |  __/ |_| | (__  | |___| (_) | | |  __/ (__| || (_) | |   \n |_|\_\___|\___|_| |_|\___|\__|_|\___|  \_____\___/|_|_|\___|\___|\__\___/|_|   \n\n")
    pwd = os.path.dirname(os.path.realpath(__file__))
    metrics_configuration = json.load(open(pwd + "/config/metrics.json", "r"))

    metrics = metrics_configuration['metrics']

    writers = []
    if os.getenv('INFLUX2_ENABLED', 'false').lower() == 'true':
        writers.append(InfuxWriter({
            'enabled': True,
            'url': os.getenv('INFLUX2_URL'),
            'org': os.getenv('INFLUX2_ORG'),
            'bucket': os.getenv('INFLUX2_BUCKET'),
            'token': os.getenv('INFLUX2_TOKEN')
        }, None))
    if os.getenv('PROMETHEUS_ENABLED', 'false').lower() == 'true':
        writers.append(PrometheusWriter({
            'expose_port': os.getenv('PROMETHEUS_EXPOSE_PORT', '9100')
        }))
    
    if not writers:
        logging.warning("No exporters enabled - both influx2 and prometheus are disabled")

    keenetic_config = {
        'admin_endpoint': os.getenv('KEENETIC_ADMIN_ENDPOINT'),
        'skip_auth': os.getenv('KEENETIC_SKIP_AUTH', 'false').lower() == 'true',
        'login': os.getenv('KEENETIC_LOGIN'),
        'password': os.getenv('KEENETIC_PASSWORD')
    }
    logging.info("Connecting to router: " + keenetic_config['admin_endpoint'])

    collectors = []
    with KeeneticClient(keenetic_config['admin_endpoint'], keenetic_config['skip_auth'],
                        keenetic_config['login'], keenetic_config['password']) as kc:
        for metric_configuration in metrics:
            logging.info("Configuring metric: " + metric_configuration['command'])
            collectors.append(KeeneticCollector(kc, metric_configuration))

        wait_interval = int(os.getenv('COLLECTOR_INTERVAL_SEC', '120'))
        logging.info(f"Configuration done. Start collecting with interval: {wait_interval} sec")
        while True:
            try:
                for collector in collectors:
                    metrics = collector.collect()
                    for writer in writers:
                        writer.write_metrics(metrics)
            except Exception as e:
                logging.error(f"Collector failed. Reason: {e}")

            time.sleep(wait_interval)