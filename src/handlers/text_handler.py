import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
from telegram import Update
from telegram.ext import ContextTypes
from config import Config
from utils.logger import bot_logger

class TextHandler:
    """Handles text input validation and processing"""
    
    @staticmethod
    async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Process text input from user"""
        user = update.effective_user
        
        # Extract text from different message types
        text = await TextHandler._extract_text(update, context)
        
        if not text:
            await update.message.reply_text(
                "❌ No text found. Please send text, .txt file, or photo with caption."
            )
            return Config.AWAITING_TEXT
        
        # Validate text length
        if len(text) > Config.MAX_TEXT_LENGTH:
            await update.message.reply_text(
                f"❌ Text too long ({len(text)}/{Config.MAX_TEXT_LENGTH} characters). "
                f"Please shorten your text."
            )
            return Config.AWAITING_TEXT
        
        # Validate text content
        if not TextHandler._is_valid_text(text):
            await update.message.reply_text(
                "❌ Text contains only emojis or special characters. "
                "Please send readable text."
            )
            return Config.AWAITING_TEXT
        
        # Store text in context for speed selection
        context.user_data['text_to_process'] = text
        context.user_data['text_length'] = len(text)
        
        bot_logger.info(f"User {user.id} submitted text ({len(text)} chars)")
        
        # Show character count and request speed selection
        keyboard = [
            ["0.5x🐢", "1.0x⚡", "1.5x🚀"],
            ["2.0x💨", "Custom🔧", "Back↩️"]
        ]
        
        from telegram import ReplyKeyboardMarkup
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"✅ Received {len(text)} characters\n"
            "Now choose playback speed:",
            reply_markup=reply_markup
        )
        
        return Config.AWAITING_SPEED
    
    @staticmethod
    async def _extract_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Extract text from different message types"""
        text = ""
        
        if update.message.text and not update.message.text.startswith('/'):
            # Regular text message
            text = update.message.text
            
        elif update.message.document:
            # Text file
            document = update.message.document
            if document.mime_type == 'text/plain' or document.file_name.endswith('.txt'):
                try:
                    file = await document.get_file()
                    file_path = f"temp_{document.file_id}.txt"
                    await file.download_to_drive(file_path)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    # Clean up temp file
                    os.remove(file_path)
                    
                    bot_logger.info(f"User {update.effective_user.id} uploaded text file")
                    
                except Exception as e:
                    bot_logger.error(f"Error reading text file: {e}")
                    await update.message.reply_text("❌ Error reading text file. Please try again.")
                    
        elif update.message.photo and update.message.caption:
            # Photo with caption
            text = update.message.caption
            bot_logger.info(f"User {update.effective_user.id} used photo caption")
        
        return text.strip() if text else ""
    
    @staticmethod
    def _is_valid_text(text: str) -> bool:
        """Check if text contains readable content"""
        # Remove whitespace and check if we have meaningful content
        cleaned = text.strip()
        if not cleaned:
            return False
        
        # Check if text is mostly emojis/special characters
        alpha_count = sum(1 for char in cleaned if char.isalnum())
        if alpha_count == 0:
            return False
        
        return True