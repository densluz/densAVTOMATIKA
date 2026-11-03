import os
import telebot

BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
MY_ID = int(os.getenv('MY_ID'))

bot = telebot.TeleBot(BOT_TOKEN)
db = {}

@bot.business_message_handler(content_types=['text', 'photo', 'video', 'document'])
def save_message(message):
    text = message.text or message.caption or "[Медиафайл]"
    sender = message.from_user.first_name if message.from_user else "Неизвестный"
    db[(message.chat.id, message.message_id)] = f"👤 От: {sender}\n💬 Текст: {text}"

@bot.deleted_business_messages_handler()
def on_delete(message):
    if hasattr(message, 'message_ids'):
        for msg_id in message.message_ids:
            key = (message.chat.id, msg_id)
            if key in db:
                saved_text = db[key]
                try:
                    bot.send_message(MY_ID, f"🚨 УДАЛЕНО СООБЩЕНИЕ!\n\n{saved_text}")
                except Exception:
                    pass
                del db[key]
