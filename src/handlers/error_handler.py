import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import bot_logger

class ErrorHandler:
    """Handles errors across the bot"""
    
    @staticmethod
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Global error handler"""
        try:
            user_id = update.effective_user.id if update and update.effective_user else "Unknown"
            
            # Log the error
            bot_logger.error(f"Error for user {user_id}: {context.error}")
            
            # Send user-friendly error message
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ An unexpected error occurred. "
                    "The issue has been logged and will be investigated.\n\n"
                    "Please try your request again."
                )
                
        except Exception as e:
            # If even error handling fails
            bot_logger.critical(f"Error in error handler: {e}")