import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import subprocess
import time
import psutil
import sys
from config import Config
from utils.logger import admin_logger

class AdminPanel:
    """Admin control panel for bot management"""
    
    def __init__(self):
        self.bot_process = None
        self.monitor_process = None
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls')
    
    def is_bot_running(self):
        """Check if bot process is running"""
        bot_pid_file = os.path.join(Config.DATA_DIR, 'bot.pid')
        
        if not os.path.exists(bot_pid_file):
            return False
        
        try:
            with open(bot_pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            return psutil.pid_exists(pid)
                
        except (ValueError, FileNotFoundError):
            return False
    
    def get_bot_status(self):
        """Get bot status with emoji"""
        if self.is_bot_running():
            return "🟢 RUNNING"
        else:
            return "🔴 STOPPED"
    
    def get_uptime(self):
        """Get bot uptime if running"""
        bot_pid_file = os.path.join(Config.DATA_DIR, 'bot.pid')
        
        if not os.path.exists(bot_pid_file):
            return "Not running"
        
        try:
            with open(bot_pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                create_time = process.create_time()
                uptime_seconds = time.time() - create_time
                
                # Format uptime
                hours = int(uptime_seconds // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                seconds = int(uptime_seconds % 60)
                
                return f"{hours}h {minutes}m {seconds}s"
            else:
                return "Not running"
                
        except:
            return "Unknown"
    
    def start_bot(self):
        """Start the bot process"""
        if self.is_bot_running():
            return "❌ Bot is already running!"
        
        try:
            # Start bot process
            self.bot_process = subprocess.Popen(
                [sys.executable, "src/bot.py"],
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Save PID to file
            bot_pid_file = os.path.join(Config.DATA_DIR, 'bot.pid')
            with open(bot_pid_file, 'w') as f:
                f.write(str(self.bot_process.pid))
            
            # Wait for bot to initialize
            for _ in range(10):
                if self.is_bot_running():
                    admin_logger.info("Bot started successfully")
                    return "✅ Bot started successfully!"
                time.sleep(0.5)
            
            return "🟡 Bot process started - initializing..."
            
        except Exception as e:
            admin_logger.error(f"Failed to start bot: {e}")
            return f"❌ Failed to start bot: {e}"
    
    def stop_bot(self):
        """Stop the bot process gracefully"""
        if not self.is_bot_running():
            return "❌ Bot is not running!"
        
        try:
            # Read PID from file
            bot_pid_file = os.path.join(Config.DATA_DIR, 'bot.pid')
            with open(bot_pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Terminate process
            process = psutil.Process(pid)
            process.terminate()
            
            # Wait for shutdown
            for _ in range(10):
                if not self.is_bot_running():
                    # Remove PID file
                    if os.path.exists(bot_pid_file):
                        os.remove(bot_pid_file)
                    admin_logger.info("Bot stopped successfully")
                    return "✅ Bot stopped successfully!"
                time.sleep(0.5)
            
            return "🟡 Stop command sent - waiting for shutdown"
            
        except Exception as e:
            admin_logger.error(f"Error stopping bot: {e}")
            return f"❌ Error stopping bot: {e}"
    
    def start_log_terminal(self):
        """Start log monitor terminal"""
        try:
            log_file = os.path.join(Config.LOGS_DIR, 'bot.log')
            
            # Create log file if it doesn't exist
            if not os.path.exists(log_file):
                with open(log_file, 'w') as f:
                    f.write("Log file created\n")
            
            # Start new terminal with log tailing
            self.monitor_process = subprocess.Popen(
                [
                    'cmd', '/k',
                    f'title Bot Monitor && '
                    f'echo === Bot Log Monitor === && '
                    f'echo Close this window anytime && '
                    f'powershell Get-Content "{log_file}" -Wait'
                ],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            admin_logger.info("Log terminal opened")
            return "✅ Log terminal opened!"
            
        except Exception as e:
            admin_logger.error(f"Failed to start log terminal: {e}")
            return f"❌ Failed to start log terminal: {e}"
    
    def display_menu(self):
        """Display admin menu based on bot status"""
        self.clear_screen()
        
        print("=================================")
        print("🤖 TEXT-TO-SPEECH BOT ADMIN")
        print("=================================")
        print(f"Bot: SpeechBot v1.0")
        print(f"Status: {self.get_bot_status()}")
        
        if self.is_bot_running():
            print(f"Uptime: {self.get_uptime()}")
            print("\n1. STOP Bot")
            print("2. OPEN Log Terminal")
            print("3. EXIT")
        else:
            print(f"Last Run: {self.get_uptime()}")
            print("\n1. START Bot")
            print("2. OPEN Log Terminal")
            print("3. EXIT")
        
        print("=================================")
    
    def run(self):
        """Main admin panel loop"""
        admin_logger.info("Admin panel started")
        
        while True:
            self.display_menu()
            
            try:
                choice = input("Choice [1-3]: ").strip()
                self.clear_screen()
                
                print("=================================")
                print("🤖 TEXT-TO-SPEECH BOT ADMIN")
                print("=================================")
                
                if self.is_bot_running():
                    # Bot is running menu
                    if choice == "1":
                        result = self.stop_bot()
                        print(result)
                    elif choice == "2":
                        result = self.start_log_terminal()
                        print(result)
                    elif choice == "3":
                        print("👋 Goodbye!")
                        break
                    else:
                        print("❌ Invalid choice! Please select 1-3")
                
                else:
                    # Bot is stopped menu
                    if choice == "1":
                        result = self.start_bot()
                        print(result)
                    elif choice == "2":
                        result = self.start_log_terminal()
                        print(result)
                    elif choice == "3":
                        print("👋 Goodbye!")
                        break
                    else:
                        print("❌ Invalid choice! Please select 1-3")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Admin panel closed by user")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                input("Press Enter to continue...")

def main():
    """Main entry point for admin panel"""
    try:
        Config.validate_setup()
        admin = AdminPanel()
        admin.run()
    except Exception as e:
        print(f"❌ Failed to start admin panel: {e}")
        input("Press Enter to exit...")

if __name__ == '__main__':
    main()