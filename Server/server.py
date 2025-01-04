from flask import Flask, request, jsonify
from numba import jit
import threading

load_value = 0

class prime_finder(threading.Thread):
    def __init__(self, n):
        super().__init__()
        self.result = None
        self.n = n

    def run(self):
        self.result = self.nth_prime(self.n)

    @staticmethod
    @jit(nopython=True, nogil=True)
    def nth_prime(n):
        def is_prime(number):
            if number <= 1:
                return False
            for i in range(2, number - 1):
                if number % i == 0:
                    return False
            return True

        count = 0
        num = 1
        while count < n:
            num += 1
            if is_prime(num):
                count += 1
        return num



app = Flask(__name__)

@app.route('/nth_prime', methods=['GET'])
def get_nth_prime():
    global load_value
    n = request.args.get('n', type=int)
    if n is None or n <= 0:
        return jsonify({"error": "Invalid input"}), 400
    try:
        load_value+=n
        prime_finder_thread = prime_finder(n)
        prime_finder_thread.start()
        prime_finder_thread.join()
        prime_number = prime_finder_thread.result
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        load_value-=n
    return jsonify({"nth_prime": prime_number})


@app.route('/load_value', methods=['GET'])
def get_load_value():
    global load_value
    return jsonify({"load_value": load_value})

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

