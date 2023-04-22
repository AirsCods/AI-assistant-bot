import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv('DEBUG')

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

OPEN_AI_TOKEN = os.getenv('OPEN_AI_TOKEN')
SHOW_USAGE = os.getenv('SHOW_USAGE')
