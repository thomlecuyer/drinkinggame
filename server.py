from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import time

app = Flask(__name__)
CORS(app)

LAST_REFRESH_FILE = 'last_refresh.txt'

def load_data(filename):
    if not os.path.exists(filename):
        return {} if filename == 'beer_sip_data.json' else []
    with open(filename, 'r') as f:
        return json.load(f)

def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)

def update_last_refresh():
    with open(LAST_REFRESH_FILE, 'w') as f:
        f.write(str(time.time()))

def get_last_refresh():
    if os.path.exists(LAST_REFRESH_FILE):
        with open(LAST_REFRESH_FILE, 'r') as f:
            return float(f.read().strip())
    return 0

@app.route('/api/sip-data', methods=['GET'])
def get_sip_data():
    return jsonify(load_data('beer_sip_data.json'))

@app.route('/api/rules', methods=['GET'])
def get_rules():
    return jsonify(load_data('rules.json'))

@app.route('/api/add-sip', methods=['POST'])
def add_sip():
    data = load_data('beer_sip_data.json')
    username = request.json['username']
    count = request.json['count']
    if username not in data:
        data[username] = {'sips': []}
    data[username]['sips'].append(count)
    save_data(data, 'beer_sip_data.json')
    return jsonify({"success": True})

@app.route('/api/add-rule', methods=['POST'])
def add_rule():
    rules = load_data('rules.json')
    rule = request.json['rule']
    sip_count = request.json['sip_count']
    rules.append([rule, sip_count])
    save_data(rules, 'rules.json')
    return jsonify({"success": True})

@app.route('/api/delete-rule', methods=['POST'])
def delete_rule():
    rules = load_data('rules.json')
    index = request.json['index']
    if 0 <= index < len(rules):
        del rules[index]
        save_data(rules, 'rules.json')
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid index"}), 400

@app.route('/api/reset-data', methods=['POST'])
def reset_data():
    save_data({}, 'beer_sip_data.json')
    save_data([], 'rules.json')
    update_last_refresh()
    return jsonify({"success": True})

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    update_last_refresh()
    return jsonify({"success": True})

@app.route('/api/last-refresh', methods=['GET'])
def last_refresh():
    return jsonify({"timestamp": get_last_refresh()})

if __name__ == '__main__':
    app.run(port=5000)