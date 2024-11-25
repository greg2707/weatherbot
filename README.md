# Singapore Weather Bot

A Telegram bot that provides real-time weather information for Singapore using the OpenWeather API.

## Features

- Get current weather conditions in Singapore
- Temperature in Celsius
- Humidity levels
- Wind speed
- "Feels like" temperature
- Weather description

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on `.env.example` and add your API keys:
   - Get a Telegram Bot Token from [@BotFather](https://t.me/BotFather)
   - Get an OpenWeather API key from [OpenWeather](https://openweathermap.org/api)

4. Run the bot:
   ```bash
   python bot.py
   ```

## Usage

- `/start` - Start the bot and see available commands
- `/weather` - Get current weather information for Singapore
- `/help` - Show help message

## Requirements

- Python 3.7+
- pyTelegramBotAPI
- requests
- python-dotenv
