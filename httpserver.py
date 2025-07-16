from flask import Blueprint, request, jsonify

import shared_data


app = Blueprint("api", __name__)

@app.route('/api/data', methods=['POST'])
def process_data():
    data = request.json
    # Process the data as needed
    return jsonify({"status": "success", "data": data})

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "This is a test endpoint"})

@app.route('/data/<string:parsername>', methods=['GET'])
def parsed_data(parsername):
    with shared_data.data_lock:
        data = shared_data.data_dict.get(parsername)
        if data is None:
            return jsonify({"error": "No data found for this parser", "available": list(shared_data.data_dict.keys())}), 404
        return jsonify(data)


