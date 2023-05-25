import os
import sys

from dotenv import load_dotenv
from loguru import logger

load_dotenv()
ADMIN_ID = os.getenv('ADMIN_ID')

admins = [
    ADMIN_ID,
]

DEBUG = os.getenv('DEBUG')

BOT_TOKEN = os.getenv('BOT_TOKEN')
SHOW_USAGE = os.getenv('SHOW_USAGE')
MAX_MESSAGE_LENGTH = 4096

OPEN_AI_TOKEN = os.getenv('OPEN_AI_TOKEN')
OPENAI_CONFIG = {
    'api_key': OPEN_AI_TOKEN,
    # 'model': 'gpt-3.5-turbo',
    'model': 'gpt-4',
    'temperature': 0.4,
    'n_choices': 1,
    'max_tokens': 2000,
    'presence_penalty': 0,
    'frequency_penalty': 0,
}

# MONGODB CONFIG
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_URL_CONNECT = f'mongodb+srv://AirsCods:{DB_PASSWORD}@cluster0.ixbwg99.mongodb.net/?retryWrites=true&w=majority'

# Configuration loguru input
logger.remove()

if DEBUG:
    logger.add(
        sys.stdout,
        format='<yellow>{time:DD-MMM-YYYY HH:mm:ss}</yellow> | <green>{level}</green> | '
               '{file} | <red>{function}</red> | <cyan>{message}</cyan>',
        colorize=True,
        level='INFO',
    )
else:
    logger.add(
        'logs/log_{time:DD-MMM-YYYY}.log',
        rotation='00:00',
        retention='7 days',
        format='{time:DD-MMM-YYYY HH:mm:ss} | {level} | {message}',
        colorize=True,
        level='INFO',
    )
