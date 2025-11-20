import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import io
from gtts import gTTS
import pyttsx3
from utils.logger import bot_logger
from services.file_service import FileService

class TTSService:
    """Text-to-Speech service with multiple providers"""
    
    def __init__(self):
        self._pyttsx_engine = None
    
    @property
    def pyttsx_engine(self):
        """Lazy initialization of pyttsx3 engine"""
        if self._pyttsx_engine is None:
            try:
                self._pyttsx_engine = pyttsx3.init()
                # Configure default settings
                self._pyttsx_engine.setProperty('rate', 150)  # Default speed
                self._pyttsx_engine.setProperty('volume', 0.8)
            except Exception as e:
                bot_logger.error(f"Failed to initialize pyttsx3: {e}")
                raise
        return self._pyttsx_engine
    
    def text_to_speech_gtts(self, text: str, speed: float = 1.0) -> bytes:
        """Convert text to speech using gTTS (primary service)"""
        try:
            # gTTS only supports slow=True/False, not exact speeds
            # We'll map speed ranges to slow/normal
            if speed < 0.8:
                slow = True
            elif speed > 1.2:
                # For faster speeds, we'll use normal and indicate in filename
                slow = False
            else:
                slow = False
            
            tts = gTTS(text=text, lang='en', slow=slow)
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer.read()
                
        except Exception as e:
            bot_logger.error(f"gTTS service error: {e}")
            raise
    
    def text_to_speech_pyttsx(self, text: str, speed: float = 1.0) -> str:
        """Convert text to speech using pyttsx3 (fallback service)"""
        try:
            # Generate filename
            filename = FileService.generate_filename()
            file_path = FileService.get_file_path(filename)
            
            # Configure speed (pyttsx3 rate is words per minute)
            base_rate = 150  # Normal speed
            adjusted_rate = int(base_rate * speed)
            self.pyttsx_engine.setProperty('rate', adjusted_rate)
            
            # Save to file
            self.pyttsx_engine.save_to_file(text, file_path)
            self.pyttsx_engine.runAndWait()
            
            return file_path
            
        except Exception as e:
            bot_logger.error(f"pyttsx3 service error: {e}")
            raise
    
    def convert_text_to_speech(self, text: str, speed: float = 1.0) -> str:
        """
        Main method to convert text to speech with fallback logic
        Returns path to generated audio file
        """
        bot_logger.info(f"Converting text to speech ({len(text)} chars, speed: {speed}x)")
        
        try:
            # Try gTTS first (better quality)
            audio_data = self.text_to_speech_gtts(text, speed)
            filename = FileService.generate_filename()
            file_path = FileService.save_audio_file(audio_data, filename)
            bot_logger.info("Successfully generated audio with gTTS")
            return file_path
            
        except Exception as gtts_error:
            bot_logger.warning(f"gTTS failed, trying pyttsx3: {gtts_error}")
            
            try:
                # Fallback to pyttsx3
                file_path = self.text_to_speech_pyttsx(text, speed)
                bot_logger.info("Successfully generated audio with pyttsx3 fallback")
                return file_path
                
            except Exception as pyttsx_error:
                bot_logger.error(f"All TTS services failed: {pyttsx_error}")
                raise Exception("Text-to-speech conversion failed. Please try again later.")