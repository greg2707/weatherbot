import os
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from travel_info import TRAVEL_INFO

# Load environment variables
load_dotenv()

# Initialize bot with your token
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN_TEST'))

# OpenWeather API configuration
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'

# Admin configuration
ADMIN_ID = os.getenv('ADMIN_TELEGRAM_ID')  # Your Telegram ID

# City coordinates
CITIES = {
    'Сингапур': {'lat': 1.29, 'lon': 103.85},
    'Пекин': {'lat': 39.90, 'lon': 116.41},
    'Шанхай': {'lat': 31.22, 'lon': 121.48},
    'Пхукет': {'lat': 7.89, 'lon': 98.40}
}

# Currency information
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
        return f"Извините, не удалось получить данные о погоде для {city}. Ошибка: {str(e)}"

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

def get_exchange_rates(currency_code):
    """Get exchange rates for a currency"""
    try:
        # Using exchangerate-api.com for free currency conversion
        url = f'https://v6.exchangerate-api.com/v6/{os.getenv("EXCHANGE_API_KEY")}/latest/{currency_code}'
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            usd_rate = data['conversion_rates']['USD']
            rub_rate = data['conversion_rates']['RUB']
            
            # Format rates to 2 decimal places
            if currency_code in ['THB', 'CNY']:  # For currencies with lower value
                formatted_usd = f"{1/usd_rate:.2f}"
                formatted_rub = f"{1/rub_rate:.2f}"
                return f"1 USD = {CURRENCIES['Китай']['symbol'] if currency_code == 'CNY' else CURRENCIES['Таиланд']['symbol']}{formatted_usd}\n1 RUB = {CURRENCIES['Китай']['symbol'] if currency_code == 'CNY' else CURRENCIES['Таиланд']['symbol']}{formatted_rub}"
            else:
                formatted_usd = f"{usd_rate:.2f}"
                formatted_rub = f"{rub_rate:.2f}"
                return f"1 {CURRENCIES['Сингапур']['symbol']} = {formatted_usd} USD\n1 {CURRENCIES['Сингапур']['symbol']} = {formatted_rub} RUB"
        else:
            return "Извините, не удалось получить курс валют. Попробуйте позже."
    except Exception as e:
        print(f"Error getting exchange rates: {e}")
        return "Произошла ошибка при получении курса валют. Попробуйте позже."

def get_main_menu_text():
    """Get main menu text"""
    return "Выберите, что вы хотите узнать:"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Handle /start and /help commands"""
    welcome_text = (
        "👋 Привет! Я твой помощник для путешествий и погоды!\n\n"
        "Что бы ты хотел узнать?"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu_markup())

@bot.callback_query_handler(func=lambda call: call.data.startswith('mode_'))
def handle_mode_selection(call):
    """Handle mode selection (weather, travel, or currency)"""
    mode = call.data.split('_')[1]
    
    if mode == 'currency':
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Выберите страну для получения курса валют:",
            reply_markup=get_currency_markup()
        )
    elif mode in ['weather', 'travel']:
        markup = InlineKeyboardMarkup()
        for city in CITIES.keys():
            markup.add(InlineKeyboardButton(city, callback_data=f'{mode}_{city}'))
        
        if mode == 'weather':
            text = "Выберите город для получения информации о погоде:"
        else:
            text = "Выберите город для получения советов путешественникам:"
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup
        )
    
    bot.answer_callback_query(call.id)

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
            text=response_text
        )
        
        # Show main menu after displaying rates
        bot.send_message(
            chat_id=call.message.chat.id,
            text=get_main_menu_text(),
            reply_markup=get_main_menu_markup()
        )
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith(('weather_', 'travel_')))
def handle_city_selection(call):
    """Handle city selection for weather or travel"""
    mode, city = call.data.split('_')
    
    if mode == 'weather':
        weather_info = get_weather(city)
        bot.edit_message_text(
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id, 
            text=weather_info
        )
        # Send main menu after weather info
        bot.send_message(
            chat_id=call.message.chat.id,
            text=get_main_menu_text(),
            reply_markup=get_main_menu_markup()
        )
    elif mode == 'travel':
        # Send photo and travel advice
        travel_info = TRAVEL_INFO.get(city, {})
        
        # Send photo if available
        if travel_info.get('photo_url'):
            try:
                # Add proper headers to comply with Wikimedia User-Agent policy
                headers = {
                    'User-Agent': 'TravelWeatherBot/1.0 (https://t.me/YourBotUsername; your_email@example.com)'
                }
                
                # Validate and download the image first
                photo_response = requests.get(
                    travel_info['photo_url'], 
                    headers=headers, 
                    timeout=10
                )
                photo_response.raise_for_status()
                
                # Check image size and type
                if len(photo_response.content) > 10 * 1024 * 1024:  # 10 MB limit
                    bot.send_message(
                        chat_id=call.message.chat.id, 
                        text=f"⚠️ Не удалось загрузить фото для {city} из-за большого размера."
                    )
                    return
                
                # Send photo using the downloaded content
                bot.send_photo(
                    chat_id=call.message.chat.id, 
                    photo=photo_response.content, 
                    caption=f"Вид на {city}"
                )
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при загрузке фото: {e}")
                bot.send_message(
                    chat_id=call.message.chat.id, 
                    text=f"⚠️ Не удалось загрузить фото для {city}. Проверьте подключение к интернету."
                )
            except Exception as e:
                print(f"Неизвестная ошибка при отправке фото: {e}")
                bot.send_message(
                    chat_id=call.message.chat.id, 
                    text=f"⚠️ Произошла неизвестная ошибка при загрузке фото для {city}."
                )
        
        # Send attractions
        attractions_text = f"🌍 Топ-3 достопримечательности в {city}:\n\n"
        for attraction in travel_info.get('attractions', []):
            attractions_text += f"{attraction}\n"
        
        bot.edit_message_text(
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id, 
            text=attractions_text
        )
        
        # Send main menu after travel info
        bot.send_message(
            chat_id=call.message.chat.id,
            text=get_main_menu_text(),
            reply_markup=get_main_menu_markup()
        )
    
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: True)
def forward_to_admin(message):
    """Forward all text messages to admin"""
    if message.text and ADMIN_ID:
        try:
            # Format the message with user info
            forward_text = (
                f"📩 Новое сообщение:\n"
                f"От: {message.from_user.first_name}"
                f"{f' {message.from_user.last_name}' if message.from_user.last_name else ''}"
                f" (@{message.from_user.username})\n"
                f"ID: {message.from_user.id}\n"
                f"Текст: {message.text}"
            )
            
            # Send formatted message to admin
            bot.send_message(ADMIN_ID, forward_text)
            
            # Reply to user with main menu
            bot.reply_to(
                message,
                "Выберите действие из меню:",
                reply_markup=get_main_menu_markup()
            )
        except Exception as e:
            print(f"Error forwarding message to admin: {e}")

# Start the bot
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
