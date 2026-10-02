from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ==================== TURTLEMINT CONFIG ====================
BASE_URL = "https://turtlemintloans.com/api/minterprise/v1/products/personal-loan/leads/existing-lead-by-pan"

BEARER_TOKEN = "f13517d5a59b689d16aa30c528ccaf7801f823b0f5548f65d6d3793270cfe8d628cea877289aba166e5425c31cfc7a0b"

HEADERS = {
    "x-broker": "turtlemint",
    "x-instana-l": "1,correlationType=web;correlationId=9f7a05debcb2c4c8",
    "x-instana-s": "9f7a05debcb2c4c8",
    "authorization": f"Bearer {BEARER_TOKEN}",
    "x-provider": "signzy",
    "sec-ch-ua-platform": '"Android"',
    "sec-ch-ua": '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
    "sec-ch-ua-mobile": "?1",
    "x-partner-id": "undefined",
    "x-tenant": "turtlemint",
    "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Mobile Safari/537.36",
    "content-type": "application/json",
    "accept": "*/*",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://turtlemintloans.com/products/personal-loan/customer/MULTI/apply",
    "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
}

COOKIES = {
    "PLAY_SESSION": "b9491e006d593b36da5043bf7febea23a8f2b906-host=http%3A%2F%2Fturtlemintloans.com&X-Forwarded-For=152.59.185.172&broker=turtlemint",
    "category": "partner",
}

@app.route("/")
def home():
    return jsonify({
        "api": "PAN to Info API",
        "usage": "/pan-info?pan=JCZPS4827P",
        "example": "/pan-info?pan=JCZPS4827P"
    })

@app.route("/pan-info", methods=["GET"])
def pan_info():
    pan = request.args.get("pan", "").strip().upper()

    if not pan or len(pan) != 10:
        return jsonify({
            "error": "Valid 10-digit PAN required",
            "example": "/pan-info?pan=JCZPS4827P"
        }), 400

    url = f"{BASE_URL}?pan={pan}"

    try:
        resp = requests.get(
            url,
            headers=HEADERS,
            cookies=COOKIES,
            timeout=15
        )

        if resp.status_code == 200:
            data = resp.json()
            return jsonify(data)
        else:
            return jsonify({
                "error": f"Upstream error {resp.status_code}",
                "raw_response": resp.text[:500]
            }), resp.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
