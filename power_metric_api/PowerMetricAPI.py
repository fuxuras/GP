import time
import flask
import csv
import threading

app = flask.Flask(__name__)

power = 0
power_lock = threading.Lock()

def get_system_power():
    energy_file = '/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj'
    
    with open(energy_file, 'r') as f:
        initial_energy = int(f.read().strip())
    
    time.sleep(1)
    
    with open(energy_file, 'r') as f:
        final_energy = int(f.read().strip())
    
    power_watts = (final_energy - initial_energy) / 1_000_000
    
    return round(power_watts, 2)

def write_power_to_csv():
    global power
    with open('power_metrics.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Power (Watts)'])
        
        while True:
            current_power = get_system_power()
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            with power_lock:
                power = current_power
            writer.writerow([timestamp, current_power])
            file.flush()

@app.route('/power', methods=['GET'])
def power_consumption():
    with power_lock:
        current_power = power
    return flask.jsonify({"power": current_power})

if __name__ == '__main__':
    csv_thread = threading.Thread(target=write_power_to_csv)
    csv_thread.daemon = True
    csv_thread.start()
    app.run(host='0.0.0.0', port=5000)