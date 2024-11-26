import os
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize bot with your token
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN_TEST'))

# OpenWeather API configuration
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'

# City coordinates with Russian names
CITIES = {
    'Сингапур': {'lat': 1.29, 'lon': 103.85},
    'Пекин': {'lat': 39.90, 'lon': 116.41},
    'Шанхай': {'lat': 31.22, 'lon': 121.48},
    'Пхукет': {'lat': 7.89, 'lon': 98.40}
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
        return f"Извините, не удалось получить данные о погоде для {city}. Ошибка: {str(e)}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Handle /start and /help commands"""
    welcome_text = (
        "👋 Привет! Я бот с погодой!\n\n"
        "Используйте /weather, чтобы узнать погоду в городе"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['weather'])
def choose_city(message):
    """Show city selection keyboard"""
    markup = InlineKeyboardMarkup()
    
    # Create buttons for each city
    for city in CITIES.keys():
        markup.add(InlineKeyboardButton(city, callback_data=f'weather_{city}'))
    
    bot.send_message(message.chat.id, "Выберите город:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('weather_'))
def handle_city_selection(call):
    """Handle city selection and fetch weather"""
    city = call.data.split('_')[1]
    weather_info = get_weather(city)
    
    # Edit the original message with weather information
    bot.edit_message_text(
        chat_id=call.message.chat.id, 
        message_id=call.message.message_id, 
        text=weather_info
    )
    
    # Answer the callback query
    bot.answer_callback_query(call.id)

# Start the bot
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
