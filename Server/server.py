from flask import Flask, request, jsonify

def is_prime(num):
    if num <= 1:
        return False
    for i in range(2, num - 1):
        if num % i == 0:
            return False
    return True

def nth_prime(n):
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
    n = request.args.get('n', type=int)
    if n is None or n <= 0:
        return jsonify({"error": "Invalid input"}), 400
    prime_number = nth_prime(n)
    return jsonify({"nth_prime": prime_number})

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

