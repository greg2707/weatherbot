# Telegram Weather Bot 🌤️

A multilingual Telegram bot for getting current weather information in different cities.

## 🌍 Supported Cities

- Singapore
- Beijing
- Shanghai
- Phuket

## 🌟 Features

- Get current weather for selected cities
- Temperature in Celsius
- Humidity levels
- Wind speed
- "Feels like" temperature
- Weather condition description
- Fully multilingual interface
- Currency converter functionality for popular Asian destinations
  - Supported currencies:
    * Singapore Dollar (SGD)
    * Thai Baht (THB)
    * Chinese Yuan (CNY)
  - Exchange rates relative to:
    * US Dollar (USD)
    * Russian Ruble (RUB)

## 🛠 Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example` and add your API keys:
   - Get a Telegram Bot Token from [@BotFather](https://t.me/BotFather)
   - Get an OpenWeather API key from [OpenWeather](https://openweathermap.org/api)
   - Get an ExchangeRate API key from [ExchangeRate](https://www.exchangerate-api.com/)

4. Run the bot:
   ```bash
   python3 bot.py
   ```

## 🤖 Usage

- `/start` - Launch the bot and view available commands
- `/weather` - Select a city and get current weather information
- `/currency` - Convert currencies for popular Asian destinations

## 🔧 Requirements

- Python 3.7+
- pyTelegramBotAPI
- requests
- python-dotenv

## 🌐 Technologies

- Telegram Bot API
- OpenWeather API
- ExchangeRate API
- Docker for containerization
- GitHub Actions for continuous deployment
