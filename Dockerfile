FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Accept build arguments
ARG TELEGRAM_BOT_TOKEN
ARG OPENWEATHER_API_KEY
ARG ADMIN_TELEGRAM_ID
ARG EXCHANGE_API_KEY

# Set environment variables
ENV TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
ENV OPENWEATHER_API_KEY=$OPENWEATHER_API_KEY
ENV ADMIN_TELEGRAM_ID=$ADMIN_TELEGRAM_ID
ENV EXCHANGE_API_KEY=$EXCHANGE_API_KEY

# Copy the rest of the application
COPY . .

CMD ["python3", "bot.py"]
