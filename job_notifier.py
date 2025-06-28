import requests
import json
import os
import base64
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db

# === CONFIGURATION ===
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
COUNTRY = "in"
SEARCH_TERMS = ["fresher", "0 years experience", "entry level", "graduate"]
OLD_JOBS_FILE = os.path.join(os.path.dirname(__file__), "adzuna_jobs.json")

# === FIREBASE INITIALIZATION ===
firebase_b64 = os.getenv("FIREBASE_KEY_B64")
firebase_json = base64.b64decode(firebase_b64).decode("utf-8")
cred = credentials.Certificate(json.loads(firebase_json))
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://jobnotifierbot-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

# === LOAD CHAT IDS FROM FIREBASE ===
def load_chat_ids():
    ref = db.reference("/chat_ids")
    data = ref.get()
    return list(data.keys()) if data else []

# === FETCH JOBS FROM ADZUNA ===
def fetch_jobs(query):
    url = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 20,
        "what": query,
        "content-type": "application/json"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"❌ Error fetching for '{query}': {response.status_code}")
        return []

# === LOAD OLD JOBS ===
def load_old_jobs():
    if os.path.exists(OLD_JOBS_FILE):
        with open(OLD_JOBS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

# === SAVE JOBS ===
def save_jobs(job_ids):
    with open(OLD_JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(job_ids), f, indent=2)

# === TELEGRAM NOTIFIER ===
def send_telegram_message(message):
    chat_ids = load_chat_ids()
    if not chat_ids:
        print("⚠️ No chat IDs found.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    for chat_id in chat_ids:
        data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
        response = requests.post(url, data=data)
        print(f"🔔 Sent to {chat_id} → Status: {response.status_code}")

# === MAIN LOGIC ===
def main():
    seen_ids = load_old_jobs()
    new_ids = set()
    all_new_jobs = []

    for query in SEARCH_TERMS:
        jobs = fetch_jobs(query)
        for job in jobs:
            job_id = job["id"]
            if job_id not in seen_ids:
                new_ids.add(job_id)
                all_new_jobs.append(job)

    if all_new_jobs:
        send_telegram_message(f"🔔 {len(all_new_jobs)} new jobs found. Sending details...")
        for job in all_new_jobs:
            msg = (
                f"<b>{job['title']}</b>\n"
                f"🏢 {job.get('company', {}).get('display_name', 'Unknown')}\n"
                f"📍 {job.get('location', {}).get('display_name', 'Unknown')}\n"
                f"🔗 <a href='{job['redirect_url']}'>Apply Here</a>"
            )
            send_telegram_message(msg)
    else:
        send_telegram_message("ℹ️ No new jobs found today.")

    save_jobs(seen_ids.union(new_ids))

if __name__ == "__main__":
    main()
