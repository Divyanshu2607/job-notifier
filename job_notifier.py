import requests
import json
import os

# === CONFIGURATION ===
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
COUNTRY = "in"  # India
SEARCH_TERMS = ["fresher", "0 years experience", "entry level", "graduate"]
OLD_JOBS_FILE = os.path.join(os.path.dirname(__file__), "adzuna_jobs.json")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}

    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"❌ Failed to send Telegram message: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception while sending Telegram message: {e}")

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
