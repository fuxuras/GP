import time
import flask
import csv
import threading
import subprocess
import json

import requests

app = flask.Flask(__name__)

power = 0
power_lock = threading.Lock()


@app.route('/power', methods=['GET'])
def power_consumption():
    with power_lock:
        current_power = power
    return flask.jsonify({"power": current_power})


def main_loop():
    while True:
        docker_status = get_docker_stats()
        power_usage = get_power_consumption()
        container_power_usage = calc_container_power_usage(power_usage, docker_status)
        container_power_usage = get_active_conn(container_power_usage)
        write_power_to_csv(container_power_usage)


def get_docker_stats():
    try:
        result = subprocess.run(['docker', 'stats', '--no-stream', '--format', '{{json .}}'], capture_output=True,
                                text=True)
        if result.returncode != 0:
            raise Exception(f"Error executing docker stats: {result.stderr}")

        stats = [json.loads(line) for line in result.stdout.strip().split('\n')]
        cpu_stats = [{"container": stat["Name"], "cpu": stat["CPUPerc"]} for stat in stats]
        return cpu_stats
    except Exception as e:
        print(f"Failed to get docker stats: {e}")
        return []


def get_power_consumption():
    energy_file = '/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj'

    with open(energy_file, 'r') as f:
        initial_energy = int(f.read().strip())

    time.sleep(0.3)

    with open(energy_file, 'r') as f:
        final_energy = int(f.read().strip())

    power_watts = (final_energy - initial_energy) / 1_000_000

    return round(power_watts, 2)


def calc_container_power_usage(power_usage, docker_stats):
    total_cpu = sum(float(stat["cpu"].strip('%')) for stat in docker_stats)
    if total_cpu == 0:
        return {stat["container"]: 0 for stat in docker_stats}

    container_power_usage = {}
    for stat in docker_stats:
        container_cpu = float(stat["cpu"].strip('%'))
        container_power_usage[stat["container"]] = round((container_cpu / total_cpu) * power_usage, 2)

    return container_power_usage


def write_power_to_csv(container_power_usage):
    file_path = '/home/fuxuras/school/gp/power_metric_api/power_usage.csv'

    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        for container, usage in container_power_usage.items():
            writer.writerow([timestamp, container, usage['active_conn'], usage['load_value'] , usage['power']])
            print(f"Writing to CSV: {timestamp}, {container}, {usage['active_conn']}, {usage['load_value']} , {usage['power']}")


def get_active_conn(container_power_usage):
    for container in container_power_usage:
        try:
            port = 8000 + int(container.split('_')[-1])
            response = requests.get(f'http://localhost:{port}/stats')
            if response.status_code == 200:
                active_conn = response.json().get('active_conn', 0)
                load_value = response.json().get('load_value', 0)
                power_value = container_power_usage[container]
                container_power_usage[container] = {'active_conn': active_conn, 'load_value':load_value, 'power': power_value}
            else:
                print(f"Failed to get load value for {container}: {response.status_code}")
        except Exception as e:
            print(f"Error getting load value for {container}: {e}")

    return container_power_usage


if __name__ == '__main__':
    csv_thread = threading.Thread(target=main_loop)
    csv_thread.daemon = True
    csv_thread.start()
    app.run(host='0.0.0.0', port=8000)


