import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your_bot_token_here')
    MAX_TEXT_LENGTH = int(os.getenv('MAX_TEXT_LENGTH', 5000))
    DEFAULT_SPEED = float(os.getenv('DEFAULT_SPEED', 1.0))
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
    LOGS_DIR = os.path.join(BASE_DIR, '..', 'logs')
    TEMP_AUDIO_DIR = os.path.join(DATA_DIR, 'temp_audio')
    
    DATABASE_PATH = os.path.join(DATA_DIR, 'user_sessions.db')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    SPEED_OPTIONS = {
        '0.5x': 0.5,
        '1.0x': 1.0,
        '1.5x': 1.5,
        '2.0x': 2.0,
        'custom': 'custom'
    }
    
    MAIN_MENU, AWAITING_TEXT, AWAITING_SPEED, CONTINUOUS_MODE = range(4)
    
    @classmethod
    def validate_setup(cls):
        if cls.TELEGRAM_TOKEN == 'your_bot_token_here':
            raise ValueError("Please set TELEGRAM_BOT_TOKEN in .env file")
        
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)
        os.makedirs(cls.TEMP_AUDIO_DIR, exist_ok=True)
        
        return True