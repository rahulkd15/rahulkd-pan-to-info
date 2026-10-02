from flask import Flask, request, jsonify
import requests
import os
import re

app = Flask(__name__)

BASE_URL = os.environ.get("BASE_URL", "https://turtlemintloans.com/api/minterprise/v1/products/personal-loan/leads/existing-lead-by-pan")
API_TOKEN = os.environ.get("API_TOKEN", "a671ffd9c897107a531bedf188eb0dee38328663d2d136f86d69eb905d57c1d7a2c35a91c39906dd1af0079da3cdf13e")


def valid_pan(pan):
    return bool(re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", pan))


@app.route("/api", methods=["GET"])
def lookup():
    pan = request.args.get("pan", "").strip().upper()

    if not pan:
        return jsonify({
            "status": "error",
            "message": "Usage: /api?pan=ABCDE1234F"
        }), 400

    if not valid_pan(pan):
        return jsonify({
            "status": "error",
            "message": "Invalid PAN format"
        }), 400

    if not BASE_URL:
        return jsonify({
            "status": "error",
            "message": "BASE_URL environment variable is not configured"
        }), 500

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(
            BASE_URL,
            headers=headers,
            params={"pan": pan},
            timeout=10
        )

        try:
            data = response.json()
        except ValueError:
            data = {
                "raw_response": response.text
            }

        return jsonify(data), response.status_code

    except requests.Timeout:
        return jsonify({
            "status": "error",
            "message": "Upstream API timed out"
        }), 504

    except requests.RequestException as e:
        return jsonify({
            "status": "error",
            "message": "Upstream API request failed",
            "detail": str(e)
        }), 502

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Internal server error",
            "detail": str(e)
        }), 500


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "Flask API is running",
        "endpoint": "/api?pan=ABCDE1234F"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
