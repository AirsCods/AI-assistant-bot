import os

from dotenv import load_dotenv

load_dotenv()

admins = [
    os.getenv('ADMIN_ID')
]

DEBUG = os.getenv('DEBUG')

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

SHOW_USAGE = os.getenv('SHOW_USAGE')

OPEN_AI_TOKEN = os.getenv('OPEN_AI_TOKEN')

OPENAI_CONFIG = {
    'api_key': OPEN_AI_TOKEN,
    'model': 'gpt-3.5-turbo',
    'temperature': 0.5,
    'n_choices': 1,
    'max_tokens': 1000,
    'presence_penalty': 0,
    'frequency_penalty': 0,
}

# MONGODB CONFIG
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_URL_CONNECT = f'mongodb+srv://AirsCods:{DB_PASSWORD}@cluster0.ixbwg99.mongodb.net/?retryWrites=true&w=majority'
