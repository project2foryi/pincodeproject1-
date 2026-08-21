import os
import telebot
from telebot import types
import requests

TOKEN = os.getenv("BOT_TOKEN", "8816369632:AAH7ybJ2WkIYttXFtJP-vAFHqfOQYqF4mCQ")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🤖 GRAB X BOT is online! Send any 6-digit PIN code (e.g., 173211).")

@bot.message_handler(func=lambda message: message.text and message.text.strip().isdigit() and len(message.text.strip()) == 6)
def handle_pincode(message):
    pincode = message.text.strip()
    msg = bot.reply_to(message, f"🔍 Searching {pincode}...")
    
    try:
        # Direct URL call with headers to avoid blocking
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(f"https://api.postalpincode.in/pincode/{pincode}", headers=headers, timeout=5)
        data = res.json()
        
        bot.delete_message(message.chat.id, msg.message_id)
        
        if data and data[0].get("Status") == "Success":
            po = data[0]["PostOffice"][0]
            reply = (
                f"📍 *Location Found!*\n\n"
                f"🔢 *PIN Code:* `{pincode}`\n"
                f"🏛 *Area:* {po.get('Name')}\n"
                f"🏙 *District:* {po.get('District')}\n"
                f"🌄 *State:* {po.get('State')}\n"
                f"🌍 *Country:* {po.get('Country')}"
            )
            bot.reply_to(message, reply, parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ Invalid PIN code or not found: `{pincode}`", parse_mode="Markdown")
            
    except Exception as e:
        print(f"Error: {e}")
        try:
            bot.delete_message(message.chat.id, msg.message_id)
        except:
            pass
        bot.reply_to(message, "⚠️ Network timeout. Please try again.")

if __name__ == "__main__":
    bot.infinity_polling()
