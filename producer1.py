import json
import time
import requests
from kafka import KafkaProducer

# Set up Kafka producer
producer = KafkaProducer(bootstrap_servers=['<broker-url>:9092'], 
                         value_serializer=lambda x: json.dumps(x).encode('utf-8'))

# Weather API
api_key = '<your_weather_api_key>'
weather_api_url = f'http://api.openweathermap.org/data/2.5/weather?q=London&appid={api_key}'

def fetch_weather_data():
    response = requests.get(weather_api_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Produce messages to Kafka topic
if __name__ == "__main__":
    while True:
        weather_data = fetch_weather_data()
        if weather_data:
            producer.send('weather-data', value=weather_data)
            print(f'Produced: {weather_data}')
        time.sleep(60)  # Fetch every 60 seconds
