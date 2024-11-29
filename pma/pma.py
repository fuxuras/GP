import time
import flask
import psutil
import subprocess


app = flask.Flask(__name__)

def get_system_power():
    energy_file = '/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj'
    
    with open(energy_file, 'r') as f:
        initial_energy = int(f.read().strip())
    
    time.sleep(1)
    
    with open(energy_file, 'r') as f:
        final_energy = int(f.read().strip())
    
    power_watts = (final_energy - initial_energy) / 1_000_000
    
    return round(power_watts, 2)

def get_container_stats():
    container_stats = []
    result = subprocess.run(['docker', 'stats', '--no-stream', '--format', '{{.Name}} {{.CPUPerc}}'], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        name, cpu_percent = line.split()
        if name.startswith('dummy_server_'):
            cpu_percent = float(cpu_percent.strip('%'))
            container_stats.append({
                'name': name,
                'cpu_percent': float(cpu_percent)
            })
    return container_stats

def convert_cpu_percent_to_power(container_stats, system_power):
    total_cpu = sum([container['cpu_percent'] for container in container_stats])
    container_power = []
    for container in container_stats:
        power = (container['cpu_percent'] / total_cpu) * system_power
        container_power.append({
            'name': container['name'],
            'power': round(power, 2)
        })
    return container_power
    

@app.route('/power')
def power_consumption():
    power = get_system_power()
    stats = get_container_stats()
    stats = convert_cpu_percent_to_power(stats, power)
    return flask.jsonify({
        'system_power': power,
        'container_power': stats
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)