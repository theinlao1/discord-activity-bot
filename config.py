import os 
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
TEST_CHANNEL_ID = int(os.getenv('TEST_CHANNEL_ID'))
ALLOWED_USER_ID = int(os.getenv('ALLOWED_USER_ID'))

POINTS_PER_MESSAGE = 1
POINTS_PER_VOICE_MINUTE = 2

TOP_LIMIT = 5