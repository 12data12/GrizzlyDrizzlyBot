import datetime
import re
from pprint import pprint
import requests
import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters, MessageHandler, CallbackQueryHandler

from Tokens import get_openweather_token, get_telegram_token

updater = Updater(get_telegram_token(), use_context=True)
dispatcher = updater.dispatcher


def startCommand(update: Update, context: CallbackContext):
    button_a = telegram.InlineKeyboardButton('Поздороваться', callback_data='button_a')
    button_b = telegram.InlineKeyboardButton('Прогноз погоды', callback_data='button_b')
    markup = telegram.InlineKeyboardMarkup(inline_keyboard=[[button_a], [button_b]])

    update.message.reply_text('Привет, выбери одно из действий.', reply_markup=markup)
    return callback


def callback(update: Update, context: CallbackContext):
    query = update.callback_query
    variant = query.data
    if variant == 'button_a':
        query.answer()
        query.edit_message_text(text=f'Привет, {update.effective_user.first_name},я так себе прогноз.\n'
                                     f'Ты можешь ввести команду /start и выбрать кнопку прогноза погоды.')

    if variant == 'button_b':
        query.answer()
        query.edit_message_text(text='Напиши: "Город: твой город"')


def get_weather(city):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Морось \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }
    weather_token = get_openweather_token()
    try:
        r = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_token}&units=metric")
        data = r.json()
        pprint(data)

        city = data["name"]
        cur_weather = data["main"]["temp"]

        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "У меня нет нужного эмоджи, посмотри в окошко."

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])

        return (f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
                f"Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n"
                f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n"
                f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\n"
                f"Продолжительность дня: {length_of_the_day}\n"
                f"Не выходи из комнаты, не совершай ошибку.")

    except Exception as ex:
        print(ex)
        return "Проверь название города"


def print_weather(update: Update, context: CallbackContext):
    city = update.message.text
    print(city.split()[1])
    forecast = get_weather(re.sub('Город: ', '', city))
    print(forecast)
    update.message.reply_text(f'Погода в городе {city[7:]}: {forecast}', parse_mode='Markdown')


#Хендлеры
start_command_handler = CommandHandler('start', startCommand)
weather_handler = MessageHandler(Filters.regex('Город: '), print_weather)
callback_button_handler = CallbackQueryHandler(callback=callback, pattern=None, run_async=False)

# Хендлеры в диспетчер
dispatcher.add_handler(start_command_handler)
dispatcher.add_handler(callback_button_handler)
dispatcher.add_handler(weather_handler)


updater.start_polling()
updater.idle()
