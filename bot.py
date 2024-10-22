import os
import telebot
import weather
from buttons import buttons
from random import choice
from time import sleep
import requests
import dotenv


dotenv.load_dotenv()
api_key = os.getenv("API_KEY")

bot = telebot.TeleBot(api_key)

commands_text = {
    "Погода на завтра",
    "Погода на послезавтра",
    "Погода на послепослезавтра",
}

excuses = [
    "Погода не меряется...",
    "Градусник сломался, чиню...",
    "Да что ж такое...",
    "Тяжело...",
    "Сегодня без погоды...",
    "💥..."
]

error_text = "Я устал и не хочу работать, возвращайтесь позже когда я отдохну"


def edit_message(chat_id: int, message_id: int, day: int, reroll=False):
    try:
        if reroll:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="Обновляем...")
            sleep(0.5)

        weather_data = None
        last_ex = ""
        for _ in range(5):
            data = weather.get_weather(day)
            if not data[0] == "Err":
                weather_data = data[1]
                break
            else:
                log(data[1])
                ex = choice(excuses)
                while ex == last_ex:
                    ex = choice(excuses)
                last_ex = ex
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=ex)
                sleep(1)
        else:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=error_text)
            return

        weather_text = f"Прогноз погоды на {weather_data['date']}\n\n"
        weather_text += f"🔆 *ДНЕМ*:\n*Температура*: {weather_data['day']['temp']}\n*Погода*: {weather_data['day']['weather']}\n*Ветер*: {weather_data['day']['wind']}\n\n"
        if any([weather_data["night"]["temp"], weather_data['night']['weather'], weather_data['night']['wind']]):
            weather_text += f"🌙 *НОЧЬЮ*:\n*Температура*: {weather_data['night']['temp']}\n*Погода*: {weather_data['night']['weather']}\n*Ветер*: {weather_data['night']['wind']}\n\n"

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=weather_text,
            parse_mode="Markdown",
            reply_markup=buttons([{"text": "Обновить 🔄", "url": None, "key": f"update|{chat_id}|{message_id}|{day}"}]))

    except telebot.apihelper.ApiTelegramException as e:
        pass

    except Exception as e:
        log(e)
        bot.send_message(
            chat_id,
            "Возникла непредвиденная ошибка..."
        )


def send_weather(ctx, day: int):
    send = bot.send_message(
        ctx.chat.id,
        "Измеряю температуру на улице...🌡🌡🌡")
    edit_message(ctx.chat.id, send.message_id, day)


logs_key = os.getenv("LOGS_KEY")  # If you want to send logs to your telegram log bot
logs_id = os.getenv("LOGS_USER_ID")  # Your telegram id


def log(text):
    print(text)
    if logs_key is None or logs_id is None: return
    url = f"https://api.telegram.org/bot{logs_key}/sendMessage"
    params = {"chat_id": logs_id, "text": "Weather Telegram Bot: " + str(text), }
    r = requests.post(url, params=params)
    if r.status_code != 200:
        print(r.text)


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    kb = [{"text": command} for command in commands_text]
    print(kb)
    keyboard = buttons(kb, inline=False)
    bot.reply_to(message, "Стартуем! Жми на комманду ↓", reply_markup=keyboard)


@bot.message_handler(content_types="text")
def send_wearher_command(message):
    if message.text == "Погода на завтра":
        send_weather(message, 1)
    elif message.text == "Погода на послезавтра":
        send_weather(message, 2)
    elif message.text == "Погода на послепослезавтра":
        send_weather(message, 3)


"""---------------------------------------------------------------------------------------"""


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if "update" in call.data:
        edit_message(*call.data.split("|")[1:], reroll=True)
        # bot.send_message(call.message.chat.id, f"Я пока еще так не могу, но учусь\nА еще вот: {call.data}")


log("Bot is ready!")
bot.infinity_polling()
