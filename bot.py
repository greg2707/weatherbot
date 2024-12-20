import os
import requests
import telebot
import logging
from logging.handlers import RotatingFileHandler
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from travel_info import TRAVEL_INFO
from datetime import datetime
import pytz

# Configure logging
def setup_logging():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler for all logs
    file_handler = RotatingFileHandler(
        'logs/bot.log',
        maxBytes=1024*1024,  # 1MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # File handler for errors only
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=1024*1024,  # 1MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    error_handler.setFormatter(error_formatter)
    logger.addHandler(error_handler)

    return logger

# Initialize logging
logger = setup_logging()

# Load environment variables
load_dotenv()

# Validate required environment variables
def validate_env_variables():
    required_vars = {
        'TELEGRAM_BOT_TOKEN': 'Telegram Bot Token',
        'OPENWEATHER_API_KEY': 'OpenWeather API Key',
        'EXCHANGE_API_KEY': 'Exchange Rate API Key'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{description} ({var})")
    
    if missing_vars:
        error_msg = "Missing required environment variables: " + ", ".join(missing_vars)
        logger.critical(error_msg)
        raise ValueError(error_msg)

# Validate environment variables before starting
validate_env_variables()

# Initialize bot with your token
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
try:
    bot = telebot.TeleBot(bot_token)
    logger.info("Bot initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize bot: {e}")
    raise

# OpenWeather API configuration
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")

# City coordinates and timezone information
CITIES = {
    'Сингапур': {
        'lat': 1.29,
        'lon': 103.85,
        'timezone': 'Asia/Singapore'
    },
    'Пекин': {
        'lat': 39.90,
        'lon': 116.41,
        'timezone': 'Asia/Shanghai'
    },
    'Шанхай': {
        'lat': 31.23,
        'lon': 121.47,
        'timezone': 'Asia/Shanghai'
    },
    'Пхукет': {
        'lat': 7.89,
        'lon': 98.40,
        'timezone': 'Asia/Bangkok'
    }
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
        logger.error(f"Failed to get weather data for {city}: {e}")
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
        logger.error(f"Failed to get exchange rates for {currency_code}: {e}")
        return "Извините, не удалось получить курс валют. Попробуйте позже."

def get_time_differences():
    """Get current time differences between Moscow and all cities"""
    moscow_tz = pytz.timezone('Europe/Moscow')
    moscow_time = datetime.now(moscow_tz)
    
    time_diff_text = "🕒 Разница во времени с Москвой:\n\n"
    
    for city, info in CITIES.items():
        city_tz = pytz.timezone(info['timezone'])
        city_time = datetime.now(city_tz)
        
        # Calculate time difference in hours
        diff_hours = (city_time.utcoffset() - moscow_time.utcoffset()).total_seconds() / 3600
        
        # Format the time string
        city_time_str = city_time.strftime('%H:%M')
        
        # Create difference string
        if diff_hours > 0:
            diff_str = f"+{int(diff_hours)}"
        else:
            diff_str = str(int(diff_hours))
            
        time_diff_text += f"{city}: {city_time_str} ({diff_str}ч)\n"
    
    return time_diff_text

def get_main_menu_markup():
    """Create main menu markup"""
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🌤 Погода", callback_data="weather"),
        InlineKeyboardButton("💰 Курс валют", callback_data="currency")
    )
    markup.row(
        InlineKeyboardButton("ℹ️ О стране", callback_data="travel"),
        InlineKeyboardButton("🕒 Время", callback_data="time")
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

@bot.callback_query_handler(func=lambda call: call.data == "weather")
def handle_weather_selection(call):
    """Handle weather selection"""
    markup = InlineKeyboardMarkup()
    for city in CITIES.keys():
        markup.add(InlineKeyboardButton(city, callback_data=f'weather_{city}'))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выберите город:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('weather_'))
def handle_weather_city_selection(call):
    """Handle weather city selection"""
    city = call.data.split('_')[1]
    weather_info = get_weather(city)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=weather_info,
        reply_markup=get_main_menu_markup()
    )

@bot.callback_query_handler(func=lambda call: call.data == "currency")
def handle_currency_selection(call):
    """Handle currency selection"""
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выберите валюту:",
        reply_markup=get_currency_markup()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('currency_'))
def handle_currency_country_selection(call):
    """Handle currency country selection"""
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

@bot.callback_query_handler(func=lambda call: call.data == "travel")
def handle_travel_selection(call):
    """Handle travel selection"""
    markup = InlineKeyboardMarkup()
    for city in TRAVEL_INFO.keys():
        markup.add(InlineKeyboardButton(city, callback_data=f'travel_{city}'))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выберите город для получения информации:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('travel_'))
def handle_travel_city_selection(call):
    """Handle travel city selection"""
    city = call.data.split('_')[1]
    
    if city in TRAVEL_INFO:
        info = TRAVEL_INFO[city]
        
        try:
            # Format the travel information
            response = (
                f"🌟 {city} 🌟\n\n"
                f"🎯 Главные достопримечательности:\n\n"
            )
            
            for attraction in info['attractions']:
                response += f"{attraction}\n"
            
            # Try to send photo with caption
            try:
                bot.send_photo(
                    chat_id=call.message.chat.id,
                    photo=info['photo_url'],
                    caption=response,
                    reply_markup=get_main_menu_markup()
                )
                # Delete the original message
                bot.delete_message(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id
                )
            except Exception as photo_error:
                logger.error(f"Failed to send photo for {city}: {photo_error}")
                # If photo fails, just send text
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=response,
                    reply_markup=get_main_menu_markup()
                )
        except Exception as e:
            logger.error(f"Error handling travel info for {city}: {e}")
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Извините, произошла ошибка при получении информации. Попробуйте позже.",
                reply_markup=get_main_menu_markup()
            )

@bot.callback_query_handler(func=lambda call: call.data == "time")
def handle_time_selection(call):
    """Handle time difference selection"""
    try:
        time_diff_text = get_time_differences()
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=time_diff_text,
            reply_markup=get_main_menu_markup()
        )
    except Exception as e:
        logger.error(f"Error handling time differences: {e}")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Извините, произошла ошибка при получении информации о времени. Попробуйте позже.",
            reply_markup=get_main_menu_markup()
        )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Handle all other messages by directing users to the menu"""
    bot.reply_to(
        message,
        "Пожалуйста, воспользуйтесь меню для взаимодействия с ботом:",
        reply_markup=get_main_menu_markup()
    )

# Start the bot
if __name__ == '__main__':
    logger.info("Starting the bot...")
    try:
        bot.infinity_polling()
        logger.info("Bot is running...")
    except Exception as e:
        logger.critical(f"Bot crashed: {e}")
        raise
