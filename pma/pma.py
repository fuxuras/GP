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


@app.route('/power', methods=['GET'])
def power_consumption():
    power = get_system_power()
    return flask.jsonify({"power": power})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)