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

excuses = [
    "Погода не меряется...",
    "Градусник сломался, чиню...",
    "Да что ж такое...",
    "Тяжело...",
    "Сегодня без погоды...",
    "💥..."
]

error_text = "Я устал и не хочу работать, возвращайтесь позже когда я отдохну"


def edit_message(chat_id, message_id, day, reroll=False):
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


def send_weather(ctx, day: str):
    send = bot.send_message(
        ctx.chat.id,
        "Измеряю температуру на улице...🌡🌡🌡")
    edit_message(ctx.chat.id, send.message_id, day)


logs_key = None  # If you want to send logs to your telegram log bot
logs_id = "1234568790"  # Your telegram id


def log(text):
    print(text)
    if logs_key is None: return
    url = f"https://api.telegram.org/bot{logs_key}/sendMessage"
    params = {"chat_id": logs_id, "text": "Weather Telegram Bot: " + str(text), }
    requests.post(url, params=params)


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Стартуем! Жми на комманду ↓")


@bot.message_handler(commands=["today"])
def send_today_weather(ctx):
    send_weather(ctx, "today")


@bot.message_handler(commands=["tomorrow"])
def generate_answer(ctx):
    send_weather(ctx, "tomorrow")


@bot.message_handler(commands=["aftertomorrow"])
def generate_answer(ctx):
    send_weather(ctx, "after_tomorrow")


"""---------------------------------------------------------------------------------------"""


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if "update" in call.data:
        edit_message(*call.data.split("|")[1:], reroll=True)
        # bot.send_message(call.message.chat.id, f"Я пока еще так не могу, но учусь\nА еще вот: {call.data}")


log("Bot is ready!")
bot.infinity_polling()
