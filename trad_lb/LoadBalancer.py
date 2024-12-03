import requests
from flask import Flask, request, jsonify

class LoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.index = 0

    def round_robin(self):
        server = self.servers[self.index]
        self.index = (self.index + 1) % len(self.servers)
        return server



app = Flask(__name__)
lb = LoadBalancer(["localhost:5000", "localhost:5001", "localhost:5002"])

@app.route('/nth_prime', methods=['GET'])
def nth_prime():
    n = request.args.get('n', type=int)
    
    server = lb.round_robin()
    url = f"http://{server}/nth_prime?n={n}"
    result = requests.get(url).json()

    return jsonify(result)

if __name__ == "__main__":
    app.run(port=8080)