import os 
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
TEST_CHANNEL_ID = int(os.getenv('TEST_CHANNEL_ID'))

allowed_ids = os.getenv('ALLOWED_USER_ID', '')
ALLOWED_USER_ID = [int(x.strip()) for x in allowed_ids.split(',') if x.strip()]

POINTS_PER_MESSAGE = 1
POINTS_PER_VOICE_MINUTE = 2

TOP_LIMIT = 5