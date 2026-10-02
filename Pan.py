from flask import Flask, request, jsonify
import requests
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

app = Flask(__name__)

# Global Dynamic Variables
CURRENT_BEARER_TOKEN = "a671ffd9c897107a531bedf188eb0dee38328663d2d136f86d69eb905d57c1d7a2c35a91c39906dd1af0079da3cdf13e"
BASE_URL = "https://turtlemintloans.com/api/minterprise/v1/products/personal-loan/leads/existing-lead-by-pan"

def fetch_fresh_token_automatically():
    """Background Automation Task: Grabs Bearer Token directly from Browser Network Session"""
    global CURRENT_BEARER_TOKEN
    print("[*] Background Auto-Token Refresher Started...")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Background me bina screen khole chalega
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://turtlemintloans.com/products/personal-loan/customer/MULTI/apply")
        time.sleep(5)  # Page load time

        # Extract Network Performance Logs for Authorization Token
        logs = driver.get_log('performance')
        for entry in logs:
            if 'Bearer ' in str(entry):
                log_str = str(entry)
                token_start = log_str.find('Bearer ') + 7
                token_candidate = log_str[token_start:].split('"')[0].split("'")[0]
                if len(token_candidate) > 20:
                    CURRENT_BEARER_TOKEN = token_candidate.strip()
                    print(f"[SUCCESS] Token Auto-Fetched: {CURRENT_BEARER_TOKEN[:15]}...")
                    break
        driver.quit()
    except Exception as e:
        print(f"[ERROR] Auto Token Fetch Failed: {str(e)}")

def start_token_loop():
    """Har 15 Minute me Automatic Run Hoga"""
    while True:
        fetch_fresh_token_automatically()
        time.sleep(900)  # 15 min interval

# Start Background Token Refreshing Thread
token_thread = threading.Thread(target=start_token_loop, daemon=True)
token_thread.start()

@app.route('/lookup_pan', methods=['GET'])
def lookup_pan():
    pan_number = request.args.get('pan')

    if not pan_number:
        return jsonify({"status": "error", "message": "Usage: /lookup_pan?pan=MQTPS3756A"}), 400

    headers = {
        "host": "turtlemintloans.com",
        "authorization": f"Bearer {CURRENT_BEARER_TOKEN}",
        "x-broker": "turtlemint",
        "x-provider": "signzy",
        "x-tenant": "turtlemint",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
        "content-type": "application/json"
    }

    params = {"pan": pan_number.upper().strip()}

    try:
        response = requests.get(BASE_URL, headers=headers, params=params, timeout=10)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"status": "error", "exception": str(e)}), 500

if __name__ == '__main__':
    print("[+] Starting FULL AUTOMATIC Turtlemint PAN API...")
    app.run(host='0.0.0.0', port=5000)
    