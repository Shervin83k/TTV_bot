import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import uuid
from datetime import datetime, timedelta
from config import Config
from utils.logger import bot_logger

class FileService:
    @staticmethod
    def generate_filename():
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"audio_{timestamp}_{unique_id}.mp3"
    
    @staticmethod
    def get_file_path(filename):
        return os.path.join(Config.TEMP_AUDIO_DIR, filename)
    
    @staticmethod
    def cleanup_old_files(hours_old=1):
        try:
            current_time = datetime.now()
            deleted_count = 0
            
            for filename in os.listdir(Config.TEMP_AUDIO_DIR):
                file_path = os.path.join(Config.TEMP_AUDIO_DIR, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    if current_time - file_time > timedelta(hours=hours_old):
                        os.remove(file_path)
                        deleted_count += 1
            
            if deleted_count > 0:
                bot_logger.info(f"Cleaned up {deleted_count} old audio files")
                
        except Exception as e:
            bot_logger.error(f"Error cleaning up files: {e}")
    
    @staticmethod
    def save_audio_file(audio_data, filename):
        try:
            file_path = FileService.get_file_path(filename)
            with open(file_path, 'wb') as f:
                f.write(audio_data)
            return file_path
        except Exception as e:
            bot_logger.error(f"Error saving audio file: {e}")
            raise
    
    @staticmethod
    def delete_file(file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            bot_logger.error(f"Error deleting file {file_path}: {e}")