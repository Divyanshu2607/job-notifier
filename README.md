# 🧠 Adzuna Fresher Job Notifier Bot

This Python script checks the [Adzuna Job API](https://developer.adzuna.com/overview) for new **fresher / entry-level jobs** in India and sends notifications to a **Telegram chat**.  
It avoids sending duplicate job posts by maintaining a record of already-sent jobs using a local JSON file.

---

## 🚀 Features

- ✅ Fetches jobs using keywords like `"fresher"`, `"0 years experience"`, `"entry level"`, etc.
- ✅ Filters out previously sent jobs (stored locally in `adzuna_jobs.json`)
- ✅ Sends job listings to Telegram with:
  - Job Title
  - Company Name
  - Location
  - Apply Link
- ✅ Sends:
  - `"🔔 X new jobs found..."` when new jobs exist
  - `"ℹ️ No new jobs found today."` if there are none

---

## 📦 Requirements

- Python 3.7+
- `requests` library

Install dependencies:

```bash
pip install requests
