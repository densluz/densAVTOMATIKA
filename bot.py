import os
import telebot
from datetime import datetime

BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
MY_ID = int(os.getenv('MY_ID'))

bot = telebot.TeleBot(BOT_TOKEN)
db = {}

@bot.business_message_handler(content_types=['text'])
def handle_chat_commands(message):
    if message.text and message.text.lower().strip().startswith('.dox'):
        
        target_name = message.chat.first_name or "Неизвестный"
        target_username = message.chat.username  # Может быть None
        
        # 1. Меняем текст сообщения на "Ищу данные..."
        try:
            bot.edit_message_text(
                text=f"🔍 Ищу данные по {target_name}...",
                chat_id=message.chat.id,
                message_id=message.message_id,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Не удалось отредактировать сообщение: {e}")
            return
        
        # 2. Проверяем, есть ли юзернейм
        if not target_username:
            # Если юзернейма нет — пишем "Ничего не найдено"
            try:
                bot.edit_message_text(
                    text="❌ Ничего не найдено (у пользователя нет открытого юзернейма).",
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    parse_mode='Markdown'
                )
            except Exception:
                pass
            return
            
        # 3. Если юзернейм есть — формируем сводку
        summary = f"👤 **Сводка по:** {target_name}\n"
        summary += f"🎂 **Дата рождения:** *Скрыта (если не указана в профиле)*\n"
        summary += f"🆔 **Юзернейм:** @{target_username}\n\n"
        
        summary += "🌐 **Открытые ссылки:**\n"
        sites = {
            'VK': f'https://vk.com/{target_username}',
            'GitHub': f'https://github.com/{target_username}',
            'Instagram': f'https://instagram.com/{target_username}',
            'TikTok': f'https://tiktok.com/@{target_username}',
            'Telegram': f'https://t.me/{target_username}'
        }
        
        for name, url in sites.items():
            summary += f"• [{name}]({url})\n"
        
        # 4. Показываем результат
        try:
            bot.edit_message_text(
                text=summary,
                chat_id=message.chat.id,
                message_id=message.message_id,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
        except Exception as e:
            print(f"Не удалось отправить результат: {e}")

# --- Логика сохранения удаленных сообщений ---
@bot.business_message_handler(content_types=['text', 'photo', 'video', 'document'])
def save_message(message):
    if message.text and message.text.lower().strip().startswith('.dox'):
        return
        
    text = message.text or message.caption or ""
    if message.from_user:
        sender_name = message.from_user.first_name
        sender_id = message.from_user.id
    else:
        sender_name, sender_id = "Неизвестный", "Нет ID"
        
    msg_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
    db[(message.chat.id, message.message_id)] = {
        "text": text, "name": sender_name, "id": sender_id, "time": msg_time
    }

@bot.deleted_business_messages_handler()
def on_delete(message):
    if hasattr(message, 'message_ids'):
        for msg_id in message.message_ids:
            key = (message.chat.id, msg_id)
            if key in db:
                saved = db[key]
                del_time = datetime.now().strftime("%H:%M:%S")
                report = (
                    f"🚨 *УДАЛЕНО СООБЩЕНИЕ!*\n\n"
                    f"👤 *От кого:* {saved['name']}\n"
                    f"🆔 *ID:* `{saved['id']}`\n"
                    f"🕒 *Время отправки:* {saved['time']}\n"
                    f"🗑 *Время удаления:* {del_time}"
                )
                if saved['text']:
                    report += f"\n💬 *Текст:* {saved['text']}"
                try:
                    bot.send_message(MY_ID, report, parse_mode='Markdown')
                except Exception:
                    pass
                del db[key]
