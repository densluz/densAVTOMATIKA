import os
import threading
from flask import Flask
import bot as tg

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "Bot is running", 200

if __name__ == "__main__":
    threading.Thread(target=lambda: tg.bot.infinity_polling(allowed_updates=['message', 'business_message', 'deleted_business_messages', 'edited_business_message']), daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
