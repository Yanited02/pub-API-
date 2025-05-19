from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import datetime
import os
VALID_API_KEYS = ["SECRET123", "PUBLOVER456"]
from flask import abort

def check_api_key():
    api_key = request.args.get('api_key')
    if api_key not in VALID_API_KEYS:
        logging.warning(f"Unauthorized access attempt with key: {api_key}")
        abort(401, description="Invalid or missing API key.")


app = Flask(__name__)
CORS(app)

# Logging configuration
LOG_FILE = 'logs/app.log'
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# In-memory data for simplicity; this can later be moved to a JSON or database
pubs = [
    {"id": 1, "name": "The Crown", "location": "Belfast", "rating": 4.5},
    {"id": 2, "name": "The Dirty Onion", "location": "Belfast", "rating": 4.7},
    {"id": 3, "name": "The Spaniard", "location": "Belfast", "rating": 4.6},
]

@app.route('/api/pubs', methods=['GET'])
def get_pubs():
    location = request.args.get('location')
    rating = request.args.get('min_rating', type=float)
    results = pubs

    if location:
        results = [pub for pub in results if pub['location'].lower() == location.lower()]
        logging.info(f"Filtered by location: {location}")
    
    if rating:
        results = [pub for pub in results if pub['rating'] >= rating]
        logging.info(f"Filtered by minimum rating: {rating}")
    
    return jsonify(results)

@app.route('/api/pubs/<int:pub_id>', methods=['GET'])
def get_pub_by_id(pub_id):
    pub = next((p for p in pubs if p['id'] == pub_id), None)
    if pub:
        logging.info(f"Pub found with ID: {pub_id}")
        return jsonify(pub)
    logging.warning(f"Pub not found with ID: {pub_id}")
    return jsonify({"error": "Pub not found"}), 404

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "status": "running",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "endpoints": ["/api/pubs", "/api/pubs/<id>", "/api/status"]
    })

@app.errorhandler(404)
def not_found(e):
    logging.warning("404 error encountered.")
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    logging.error(f"500 error: {str(e)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

