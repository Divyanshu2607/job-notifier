import os
import telebot
import firebase_admin
from firebase_admin import credentials, db
import json
import io

# === Load and parse Firebase key from ENV ===
firebase_json = os.getenv("FIREBASE_KEY_JSON")
firebase_dict = json.loads(firebase_json)
cred = credentials.Certificate(firebase_dict)

firebase_admin.initialize_app(cred, {
    'databaseURL': "https://jobnotifierbot-default-rtdb.asia-southeast1.firebasedatabase.app/"
})
# === Telegram Bot Init ===
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# === Handle /start Command ===
@bot.message_handler(commands=["start"])
def register_user(message):
    chat_id = str(message.chat.id)
    ref = db.reference("/chat_ids")
    current_ids = ref.get() or {}
    if chat_id not in current_ids:
        ref.update({chat_id: True})
        bot.send_message(chat_id, "✅ You’re now registered for job alerts!")
    else:
        bot.send_message(chat_id, "🔔 You're already subscribed to job alerts.")

# === Keep Bot Polling ===
print("🤖 Bot is running...")
bot.infinity_polling()
