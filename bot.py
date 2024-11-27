import os
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from travel_info import TRAVEL_INFO
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize bot with your token
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

# OpenWeather API configuration
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")

# Admin configuration
ADMIN_ID = os.getenv('ADMIN_TELEGRAM_ID')

# City coordinates
CITIES = {
    'Сингапур': {'lat': 1.29, 'lon': 103.85},
    'Пекин': {'lat': 39.90, 'lon': 116.41},
    'Шанхай': {'lat': 31.23, 'lon': 121.47},
    'Пхукет': {'lat': 7.89, 'lon': 98.40}
}

# Currency codes
CURRENCIES = {
    'Сингапур': {'code': 'SGD', 'symbol': 'S$'},
    'Таиланд': {'code': 'THB', 'symbol': '฿'},
    'Китай': {'code': 'CNY', 'symbol': '¥'}
}

def get_weather(city):
    """Fetch weather data for a specific city from OpenWeather API"""
    if city not in CITIES:
        return f"Извините, данные о погоде для {city} недоступны."

    params = {
        'lat': CITIES[city]['lat'],
        'lon': CITIES[city]['lon'],
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric'  # For Celsius
    }
    
    try:
        response = requests.get(WEATHER_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        weather_info = {
            'description': data['weather'][0]['description'].capitalize(),
            'temperature': round(data['main']['temp']),
            'humidity': data['main']['humidity'],
            'wind_speed': round(data['wind']['speed'] * 3.6, 1),  # Convert m/s to km/h
            'feels_like': round(data['main']['feels_like'])
        }
        
        return (
            f"🌟 Текущая погода в {city} 🌟\n\n"
            f"🌤 Состояние: {weather_info['description']}\n"
            f"🌡 Температура: {weather_info['temperature']}°C\n"
            f"🌡 Ощущается как: {weather_info['feels_like']}°C\n"
            f"💧 Влажность: {weather_info['humidity']}%\n"
            f"💨 Скорость ветра: {weather_info['wind_speed']} км/ч"
        )
    except Exception as e:
        return f"Извините, не удалось получить данные о погоде для {city}. Попробуйте позже."

def get_exchange_rates(currency_code):
    """Get exchange rates for a currency"""
    try:
        url = f'https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/{currency_code}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if response.status_code == 200:
            usd_rate = data['conversion_rates']['USD']
            rub_rate = data['conversion_rates']['RUB']
            
            if currency_code in ['THB', 'CNY']:
                formatted_usd = f"{1/usd_rate:.2f}"
                formatted_rub = f"{1/rub_rate:.2f}"
                return f"1 USD = {CURRENCIES['Китай']['symbol'] if currency_code == 'CNY' else CURRENCIES['Таиланд']['symbol']}{formatted_usd}\n1 RUB = {CURRENCIES['Китай']['symbol'] if currency_code == 'CNY' else CURRENCIES['Таиланд']['symbol']}{formatted_rub}"
            else:
                formatted_usd = f"{usd_rate:.2f}"
                formatted_rub = f"{rub_rate:.2f}"
                return f"1 {CURRENCIES['Сингапур']['symbol']} = {formatted_usd} USD\n1 {CURRENCIES['Сингапур']['symbol']} = {formatted_rub} RUB"
    except Exception as e:
        return "Извините, не удалось получить курс валют. Попробуйте позже."

def get_main_menu_markup():
    """Create main menu markup"""
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🌤 Погода", callback_data='mode_weather'),
        InlineKeyboardButton("✈️ Трэвел советы", callback_data='mode_travel')
    )
    markup.row(
        InlineKeyboardButton("💰 Курс валют", callback_data='mode_currency')
    )
    return markup

def get_currency_markup():
    """Create currency selection markup"""
    markup = InlineKeyboardMarkup()
    for country in CURRENCIES.keys():
        markup.add(InlineKeyboardButton(country, callback_data=f'currency_{country}'))
    return markup

def get_main_menu_text():
    """Get main menu text"""
    return "Выберите, что вы хотите узнать:"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Handle start and help commands"""
    bot.reply_to(
        message,
        "Привет! Я бот для путешествий по Азии. Я могу:\n"
        "🌤 Показать погоду\n"
        "✈️ Дать советы по путешествиям\n"
        "💰 Показать курсы валют\n\n"
        "Выберите действие из меню:",
        reply_markup=get_main_menu_markup()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('mode_'))
def handle_mode_selection(call):
    """Handle mode selection"""
    mode = call.data.split('_')[1]
    
    if mode == 'weather':
        markup = InlineKeyboardMarkup()
        for city in CITIES.keys():
            markup.add(InlineKeyboardButton(city, callback_data=f'weather_{city}'))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Выберите город:",
            reply_markup=markup
        )
    
    elif mode == 'travel':
        markup = InlineKeyboardMarkup()
        for city in TRAVEL_INFO.keys():
            markup.add(InlineKeyboardButton(city, callback_data=f'travel_{city}'))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Выберите город для получения информации:",
            reply_markup=markup
        )
    
    elif mode == 'currency':
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Выберите валюту:",
            reply_markup=get_currency_markup()
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('currency_'))
def handle_currency_selection(call):
    """Handle currency selection"""
    country = call.data.split('_')[1]
    
    if country in CURRENCIES:
        currency_code = CURRENCIES[country]['code']
        rates_info = get_exchange_rates(currency_code)
        
        response_text = f"💰 Курс валют для {country}:\n\n{rates_info}"
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response_text,
            reply_markup=get_main_menu_markup()
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('weather_'))
def handle_weather_selection(call):
    """Handle weather selection"""
    city = call.data.split('_')[1]
    weather_info = get_weather(city)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=weather_info,
        reply_markup=get_main_menu_markup()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('travel_'))
def handle_travel_selection(call):
    """Handle travel selection"""
    city = call.data.split('_')[1]
    
    if city in TRAVEL_INFO:
        info = TRAVEL_INFO[city]
        response = (
            f"🌟 {city} 🌟\n\n"
            f"📍 Описание:\n{info['description']}\n\n"
            f"🎯 Главные достопримечательности:\n"
        )
        
        for attraction in info['attractions']:
            response += f"• {attraction}\n"
        
        if 'photo_url' in info:
            bot.send_photo(
                call.message.chat.id,
                info['photo_url'],
                caption=response,
                reply_markup=get_main_menu_markup()
            )
            bot.delete_message(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
        else:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=response,
                reply_markup=get_main_menu_markup()
            )

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Handle all other messages and forward to admin"""
    if message.text and ADMIN_ID:
        try:
            # Format the message with user info
            forward_text = (
                f"📩 Новое сообщение:\n"
                f"От: {message.from_user.first_name}"
                f"{f' {message.from_user.last_name}' if message.from_user.last_name else ''}"
                f"{f' (@{message.from_user.username})' if message.from_user.username else ''}\n"
                f"ID: {message.from_user.id}\n"
                f"Текст: {message.text}"
            )
            
            # Send formatted message to admin
            bot.send_message(ADMIN_ID, forward_text)
        except Exception as e:
            print(f"Failed to forward message to admin: {e}")
    
    # Reply to user with main menu
    bot.reply_to(
        message,
        "Выберите действие из меню:",
        reply_markup=get_main_menu_markup()
    )

# Start the bot
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
