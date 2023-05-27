import os
import sys

from dotenv import load_dotenv
from loguru import logger

load_dotenv()
DEBUG = os.getenv('DEBUG', '').lower() == 'true'

ADMIN_ID = os.getenv('ADMIN_ID')

admins = [
    ADMIN_ID,
]

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
# Configuration MongoDB
DB_URL_CONNECT = 'mongodb://mongodb:27017'

# Configuration Loguru input
logger.remove()
logger.add(
    'logs/log_{time:DD-MMM-YYYY}.log',
    format='{time:DD-MMM-YYYY HH:mm:ss} | {level} | {file} > {function} : {message}',
    backtrace=True,
    diagnose=False,
    level='INFO',
    rotation='00:00',
    retention='7 days',
    enqueue=True,
)

if DEBUG:
    # MONGO_URI = f"mongodb+srv://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}" \
    #             f"@cluster0.ixbwg99.mongodb.net/?retryWrites=true&w=majority"
    SHOW_USAGE = True
    logger.add(
        sys.stderr,
        format='<yellow>{time:DD-MMM-YY HH:mm:ss}</yellow> | <green>{level}</green> | '
               '<magenta>{file}</magenta> > <lc>{function}</lc> : <white>{message}</white>',
        colorize=True,
        diagnose=True,
        level='DEBUG'
    )
    logger.info('DEBUG is TRUE')
