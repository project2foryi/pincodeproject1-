import os
import time
import telebot
from telebot import types
import requests

# Environment variables se token lena (Railway par variables mein set karna hoga)
TOKEN = os.getenv("BOT_TOKEN", "8816369632:AAH7ybJ2WkIYttXFtJP-vAFHqfOQYqF4mCQ")
bot = telebot.TeleBot(TOKEN)

# In-Memory Cache & Cooldown (Anti-Spam)
pincode_cache = {}
user_cooldown = {}
COOLDOWN_TIME = 2  # 2 seconds delay

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🤖 *Welcome to GRAB X BOT (Advanced)*\n\n"
        "📍 Send any 6-digit Indian PIN code directly or use:\n"
        "👉 `/pincode 173211`"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['pincode'])
def handle_pincode_command(message):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit() or len(args[1]) != 6:
        bot.reply_to(message, "⚠️ Usage: `/pincode 173211`", parse_mode="Markdown")
        return
    
    process_pincode(message, args[1])

@bot.message_handler(func=lambda message: message.text and message.text.strip().isdigit() and len(message.text.strip()) == 6)
def handle_text_pincode(message):
    user_id = message.from_user.id
    current_time = time.time()
    
    # Rate limiter check
    if user_id in user_cooldown and current_time - user_cooldown[user_id] < COOLDOWN_TIME:
        bot.reply_to(message, "⚠️ Please slow down! Wait a couple of seconds.")
        return
    
    user_cooldown[user_id] = current_time
    process_pincode(message, message.text.strip())

def process_pincode(message, pincode):
    processing_msg = bot.reply_to(message, f"🔍 Looking up `{pincode}`...", parse_mode="Markdown")
    
    try:
        # Check Cache first
        if pincodeCache_check(pincode):
            result = pincode_cache[pincode]
        else:
            response = requests.get(f"https://api.postalpincode.in/pincode/{pincode}")
            raw_data = response.json()
            
            success = raw_data and raw_data[0].get("Status") == "Success"
            if success:
                post_offices = raw_data[0].get("PostOffice", [])
                result = {
                    "success": True,
                    "data": [{
                        "area": po.get("Name"),
                        "branchType": po.get("BranchType"),
                        "district": po.get("District"),
                        "state": po.get("State"),
                        "country": po.get("Country")
                    } for po in post_offices]
                }
                pincode_cache[pincode] = result
            else:
                result = {"success": False}

        # Purana processing message delete karna
        bot.delete_message(message.chat.id, processing_msg.message_id)

        if result.get("success") and result.get("data"):
            data = result["data"]
            main_loc = data[0]
            
            max_display = 8
            areas_list = "\n".join([f"• *{item['area']}* ({item['branchType']})" for item in data[:max_display]])
            
            if len(data) > max_display:
                areas_list += f"\n_...and {len(data) - max_display} more areas._"

            reply_message = (
                f"📍 *Location Intelligence Report*\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"🔢 *PIN Code:* `{pincode}`\n"
                f"🏛 *District:* {main_loc['district']}\n"
                f"🌄 *State:* {main_loc['state']}\n"
                f"🌍 *Country:* {main_loc['country']}\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"📌 *Covered Areas:*\n{areas_list}"
            )

            # Inline Button for Google Maps
            maps_url = f"https://www.google.com/maps/search/?api=1&query={pincode}+{main_loc['district']}+{main_loc['state']}"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🗺 Open in Google Maps", url=maps_url))

            bot.reply_to(message, reply_message, parse_mode="Markdown", reply_markup=markup)
        else:
            bot.reply_to(message, f"❌ No records found for PIN code `{pincode}`.", parse_mode="Markdown")

    except Exception as e:
        print(f"Error: {e}")
        try:
            bot.delete_message(message.chat.id, processing_msg.message_id)
        except:
            pass
        bot.reply_to(message, "⚠️ Internal system error. Please try again later.")

def pincodeCache_check(pincode):
    return pincode in pinc_cache_keys() if 'pinc_cache_keys' else pincode in pincode_cache

if __name__ == "__main__":
    print("🚀 GRAB X BOT (Advanced Python) is starting...")
    bot.infinity_polling()
          
