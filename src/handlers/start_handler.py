import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from config import Config
from utils.logger import bot_logger

class StartHandler:
    """Handles start command and main menu navigation"""
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Send welcome message and show main menu"""
        user = update.effective_user
        
        welcome_text = (
            "🎤 *Welcome to Text-to-Speech Bot!*\n\n"
            "I can convert your text to speech with multiple speed options!\n\n"
            "✨ *Features:*\n"
            "• Convert text to audio\n"
            "• Multiple speed options (0.5x to 2.0x + custom)\n"
            "• Support for .txt files\n"
            "• Photo caption processing\n"
            "• Up to 5,000 characters\n\n"
            "📝 *How to use:*\n"
            "1. Send me text, a .txt file, or a photo with caption\n"
            "2. Choose your preferred speed\n"
            "3. Receive your audio file!\n\n"
            "Click the button below to get started! 🚀"
        )
        
        keyboard = [["🎤 Convert Text"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        bot_logger.info(f"User {user.id} started the bot")
        return Config.MAIN_MENU
    
    @staticmethod
    async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle main menu navigation"""
        user_input = update.message.text
        
        if user_input == "🎤 Convert Text":
            await update.message.reply_text(
                "📝 Please send your text, .txt file, or photo with caption:\n\n"
                "You can send:\n"
                "• Direct text message\n"
                "• .txt file (document)\n"
                "• Photo with caption\n\n"
                "Or use /cancel to go back",
                reply_markup=ReplyKeyboardRemove()
            )
            return Config.AWAITING_TEXT
        
        else:
            # Invalid input in main menu
            keyboard = [["🎤 Convert Text"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                "Please use the button below to get started:",
                reply_markup=reply_markup
            )
            return Config.MAIN_MENU
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send help message"""
        help_text = (
            "🤖 *Text-to-Speech Bot Help*\n\n"
            "📝 *How to use:*\n"
            "1. Send /start to begin\n"
            "2. Choose 'Convert Text'\n"
            "3. Send your text in one of these ways:\n"
            "   • Direct text message\n"
            "   • .txt file upload\n"
            "   • Photo with caption\n"
            "4. Select playback speed\n"
            "5. Receive your audio file!\n\n"
            "⚡ *Speed Options:*\n"
            "• 0.5x🐢 - Very slow\n"
            "• 1.0x⚡ - Normal speed\n"
            "• 1.5x🚀 - Fast\n"
            "• 2.0x💨 - Very fast\n"
            "• Custom🔧 - Any speed from 0.1x to 3.0x\n\n"
            "📏 *Limits:*\n"
            "• Max 5,000 characters per conversion\n\n"
            "🛠 *Commands:*\n"
            "/start - Start the bot\n"
            "/help - Show this help\n"
            "/cancel - Cancel current operation"
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel conversation and return to start"""
        user = update.effective_user
        
        # Clear user data
        context.user_data.clear()
        
        await update.message.reply_text(
            "Operation cancelled.\n\n"
            "Use /start to begin again!",
            reply_markup=ReplyKeyboardRemove()
        )
        
        bot_logger.info(f"User {user.id} cancelled operation")
        return ConversationHandler.END