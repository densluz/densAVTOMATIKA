import os
import telebot
from datetime import datetime

BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
MY_ID = int(os.getenv('MY_ID'))

bot = telebot.TeleBot(BOT_TOKEN)
db = {}

@bot.business_message_handler(content_types=['text', 'photo', 'video', 'document'])
def save_message(message):
    text = message.text or message.caption or "[Медиафайл]"
    
    # Берем данные отправителя
    if message.from_user:
        sender_name = message.from_user.first_name
        sender_id = message.from_user.id
    else:
        sender_name = "Неизвестный"
        sender_id = "Нет ID"
        
    # Запоминаем время получения сообщения (по сути, время его отправки)
    msg_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
    # Сохраняем всё в базу
    db[(message.chat.id, message.message_id)] = {
        "text": text,
        "name": sender_name,
        "id": sender_id,
        "time": msg_time
    }

@bot.deleted_business_messages_handler()
def on_delete(message):
    if hasattr(message, 'message_ids'):
        for msg_id in message.message_ids:
            key = (message.chat.id, msg_id)
            if key in db:
                saved = db[key]
                # Время удаления
                del_time = datetime.now().strftime("%H:%M:%S")
                
                # Формируем красивое сообщение
                report = (
                    f"🚨 **УДАЛЕНО СООБЩЕНИЕ!**\n\n"
                    f"👤 **От кого:** {saved['name']}\n"
                    f"🆔 **ID:** `{saved['id']}`\n"
                    f"🕒 **Время отправки:** {saved['time']}\n"
                    f"🗑 **Время удаления:** {del_time}\n"
                    f"💬 **Текст:** {saved['text']}"
                )
                
                try:
                    # parse_mode='Markdown' делает текст жирным и красивым
                    bot.send_message(MY_ID, report, parse_mode='Markdown')
                except Exception:
                    pass
                
                del db[key]
