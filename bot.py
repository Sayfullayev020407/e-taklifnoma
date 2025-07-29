import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
import urllib.parse

API_TOKEN = '7262457869:AAGWaZENB2jkp1Gcaj5m4o_p1ELTuwX0wEg'

bot = telebot.TeleBot(API_TOKEN)

def get_user_photo_url(user_id):
    """Foydalanuvchi profil rasmini olish."""
    photos = bot.get_user_profile_photos(user_id)
    if photos.total_count > 0:
        file_id = photos.photos[0][0].file_id
        file_info = bot.get_file(file_id)
        photo_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}"
        return photo_url
    return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    tg_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    profile_photo = get_user_photo_url(tg_id)

    # URL encoded qilish
    profile_photo_encoded = urllib.parse.quote(profile_photo or '', safe='')
    web_app_url = (
        f"https://phoenix-rapid-factually.ngrok-free.app/?tg_id={tg_id}&username={username}"
        f"&first_name={first_name}&last_name={last_name}&profile_photo={profile_photo_encoded}"
    )

    web_app_button = InlineKeyboardButton(
        text="Web App ni ochish",
        web_app=WebAppInfo(url=web_app_url)
    )

    keyboard = InlineKeyboardMarkup()
    keyboard.add(web_app_button)

    bot.send_message(
        message.chat.id,
        f"Assalomu alaykum, {first_name}! Botga xush kelibsiz.\n"
        f"Web App orqali o'zingiz istagan online taklifnomalarni yaratishingiz mumkin !",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

if __name__ == '__main__':
    bot.infinity_polling()
