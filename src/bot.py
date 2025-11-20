import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler

from config import Config
from utils.logger import bot_logger
from handlers.start_handler import StartHandler
from handlers.text_handler import TextHandler
from handlers.audio_handler import AudioHandler
from handlers.error_handler import ErrorHandler
from services.file_service import FileService


class TextToSpeechBot:
    """Main Telegram Bot Application"""
    
    def __init__(self):
        self.application = None
        self.audio_handler = AudioHandler()
    
    def setup_handlers(self):
        """Setup all conversation handlers"""
        
        # Main conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', StartHandler.start)],
            states={
                Config.MAIN_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, StartHandler.main_menu)
                ],
                Config.AWAITING_TEXT: [
                    MessageHandler(
                        filters.TEXT | filters.Document.ALL | filters.PHOTO, 
                        TextHandler.handle_text_input
                    ),
                    CommandHandler('cancel', StartHandler.cancel)
                ],
                Config.AWAITING_SPEED: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.audio_handler.handle_speed_selection),
                    CommandHandler('cancel', StartHandler.cancel)
                ],
                Config.CONTINUOUS_MODE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.audio_handler.handle_continuous_mode),
                    CommandHandler('cancel', StartHandler.cancel)
                ],
            },
            fallbacks=[CommandHandler('cancel', StartHandler.cancel)],
        )
        
        # Add handlers to application
        self.application.add_handler(conv_handler)
        self.application.add_handler(CommandHandler('help', StartHandler.help_command))
        self.application.add_handler(CommandHandler('cancel', StartHandler.cancel))
        
        # Add error handler
        self.application.add_error_handler(ErrorHandler.error_handler)
    
    async def post_init(self, application):
        """Run after bot initialization"""
        # Clean up old files on startup
        FileService.cleanup_old_files()
        bot_logger.info("Bot initialized successfully")
    
    async def post_stop(self, application):
        """Run before bot shutdown"""
        bot_logger.info("Bot shutting down...")
        # Clean up temp files on shutdown
        FileService.cleanup_old_files(0)  # Clean all temp files
    
    def run(self):
        """Start the bot"""
        try:
            # Validate configuration
            Config.validate_setup()
            
            # Create application
            self.application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
            
            # Setup handlers
            self.setup_handlers()
            
            # Add startup/shutdown hooks
            self.application.post_init = self.post_init
            self.application.post_stop = self.post_stop
            
            bot_logger.info("Starting bot polling...")
            
            # Start the bot
            self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
        except Exception as e:
            bot_logger.critical(f"Failed to start bot: {e}")
            raise

def main():
    """Main entry point for the bot"""
    bot = TextToSpeechBot()
    bot.run()

if __name__ == '__main__':
    main()