import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from config import Config
from utils.logger import bot_logger
from services.tts_service import TTSService
from services.file_service import FileService

class AudioHandler:
    """Handles speed selection and audio generation"""
    
    def __init__(self):
        self.tts_service = TTSService()
    
    async def handle_speed_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle speed selection and generate audio"""
        user = update.effective_user
        user_input = update.message.text
        
        # Handle back button
        if user_input == "Back↩️":
            from handlers.start_handler import StartHandler
            return await StartHandler.main_menu(update, context)
        
        # Get speed value
        speed = await self._parse_speed_input(update, user_input, context)
        if speed is None:
            return Config.AWAITING_SPEED
        
        # Get text from context
        text = context.user_data.get('text_to_process')
        if not text:
            await update.message.reply_text("❌ Text not found. Please start over.")
            from handlers.start_handler import StartHandler
            return await StartHandler.main_menu(update, context)
        
        # Store speed for continuous mode
        context.user_data['last_speed'] = speed
        
        # Generate audio
        await self._generate_and_send_audio(update, context, text, speed, user.id)
        
        # Ask for next action
        keyboard = [["🔄 Keep Sending", "🛑 Stop"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "What would you like to do next?",
            reply_markup=reply_markup
        )
        
        return Config.CONTINUOUS_MODE
    
    async def handle_continuous_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle continuous mode operations"""
        user_input = update.message.text
        user = update.effective_user
        
        if user_input == "🛑 Stop":
            from handlers.start_handler import StartHandler
            return await StartHandler.main_menu(update, context)
        
        elif user_input == "🔄 Keep Sending":
            await update.message.reply_text(
                "📝 Send your next text (or /cancel to stop)",
                reply_markup=ReplyKeyboardRemove()
            )
            return Config.AWAITING_TEXT
        
        else:
            # User sent text directly in continuous mode
            text = update.message.text
            
            if not text or text.startswith('/'):
                await update.message.reply_text(
                    "⚠️ Please send text or use the buttons below",
                    reply_markup=ReplyKeyboardMarkup([["🔄 Keep Sending", "🛑 Stop"]], resize_keyboard=True)
                )
                return Config.CONTINUOUS_MODE
            
            # Validate text
            if len(text) > Config.MAX_TEXT_LENGTH:
                await update.message.reply_text(
                    f"❌ Text too long ({len(text)}/{Config.MAX_TEXT_LENGTH} characters)"
                )
                return Config.CONTINUOUS_MODE
            
            # Use last speed or default
            speed = context.user_data.get('last_speed', Config.DEFAULT_SPEED)
            
            # Generate audio
            await self._generate_and_send_audio(update, context, text, speed, user.id)
            
            # Keep same keyboard for next action
            keyboard = [["🔄 Keep Sending", "🛑 Stop"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                "Next:",
                reply_markup=reply_markup
            )
            
            return Config.CONTINUOUS_MODE
    
    async def _parse_speed_input(self, update: Update, user_input: str, context: ContextTypes.DEFAULT_TYPE) -> float:
        """Parse speed input from user"""
        speed = None
        
        # Map button text to speed values
        speed_mapping = {
            "0.5x🐢": 0.5,
            "1.0x⚡": 1.0,
            "1.5x🚀": 1.5,
            "2.0x💨": 2.0,
            "Custom🔧": "custom"
        }
        
        if user_input in speed_mapping:
            speed_value = speed_mapping[user_input]
            if speed_value == "custom":
                await update.message.reply_text(
                    "🔧 Enter speed multiplier (0.1 to 3.0):\n"
                    "Example: 0.8 for slower, 1.2 for faster",
                    reply_markup=ReplyKeyboardRemove()
                )
                context.user_data['awaiting_custom_speed'] = True
                return None
            else:
                speed = speed_value
        
        elif context.user_data.get('awaiting_custom_speed'):
            try:
                speed = float(user_input)
                if 0.1 <= speed <= 3.0:
                    context.user_data['awaiting_custom_speed'] = False
                else:
                    await update.message.reply_text("❌ Please enter between 0.1 and 3.0")
                    return None
            except ValueError:
                await update.message.reply_text("❌ Please enter a valid number (0.1 to 3.0)")
                return None
        
        else:
            # Invalid input in speed selection
            keyboard = [
                ["0.5x🐢", "1.0x⚡", "1.5x🚀"],
                ["2.0x💨", "Custom🔧", "Back↩️"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                "⚠️ Please choose a speed option from the buttons:",
                reply_markup=reply_markup
            )
            return None
        
        return speed
    
    async def _generate_and_send_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                     text: str, speed: float, user_id: int):
        """Generate audio and send to user with progress updates"""
        try:
            # Send progress message
            progress_msg = await update.message.reply_text(
                f"🔄 Creating audio...\n"
                f"📊 Text: {len(text)} characters\n"
                f"⚡ Speed: {speed}x"
            )
            
            # Generate audio
            audio_file_path = self.tts_service.convert_text_to_speech(text, speed)
            
            # Update progress
            await progress_msg.edit_text("📤 Sending audio...")
            
            # Send audio file
            with open(audio_file_path, 'rb') as audio_file:
                await update.message.reply_audio(
                    audio=audio_file,
                    title="Text-to-Speech Audio",
                    performer="SpeechBot",
                    caption=f"Speed: {speed}x | Text: {len(text)} chars"
                )
            
            # Delete progress message
            await progress_msg.delete()
            
            # Clean up audio file
            FileService.delete_file(audio_file_path)
            
            bot_logger.info(f"User {user_id} received audio (speed: {speed}x, length: {len(text)} chars)")
            
        except Exception as e:
            bot_logger.error(f"Audio generation failed for user {user_id}: {e}")
            await update.message.reply_text(
                "❌ Failed to generate audio. Please try again with different text."
            )
            
            # Clean up any partial files
            if 'audio_file_path' in locals() and os.path.exists(audio_file_path):
                FileService.delete_file(audio_file_path)