import os
import requests
import telebot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize bot with your token
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

# OpenWeather API configuration
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
SINGAPORE_COORDS = {'lat': 1.29, 'lon': 103.85}  # Singapore coordinates
WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'

def get_weather():
    """Fetch weather data for Singapore from OpenWeather API"""
    params = {
        'lat': SINGAPORE_COORDS['lat'],
        'lon': SINGAPORE_COORDS['lon'],
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
            f"🌟 Current Weather in Singapore 🌟\n\n"
            f"🌤 Condition: {weather_info['description']}\n"
            f"🌡 Temperature: {weather_info['temperature']}°C\n"
            f"🌡 Feels like: {weather_info['feels_like']}°C\n"
            f"💧 Humidity: {weather_info['humidity']}%\n"
            f"💨 Wind Speed: {weather_info['wind_speed']} km/h"
        )
    except Exception as e:
        return f"Sorry, I couldn't fetch the weather data. Error: {str(e)}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Handle /start and /help commands"""
    welcome_text = (
        "👋 Hello! I'm your Singapore Weather Bot!\n\n"
        "Use these commands:\n"
        "/weather - Get current weather in Singapore\n"
        "/help - Show this help message"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['weather'])
def send_weather(message):
    """Handle /weather command"""
    weather_info = get_weather()
    bot.reply_to(message, weather_info)

# Start the bot
if __name__ == '__main__':
    print("Bot started...")
    bot.infinity_polling()
