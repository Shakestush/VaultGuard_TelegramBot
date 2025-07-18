import logging
import random
import string
import time
from datetime import datetime, timedelta
from typing import Dict, Optional
import asyncio
import json
import os

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class OTPBot:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.users: Dict[int, dict] = {}
        self.otp_codes: Dict[int, dict] = {}
        self.services: Dict[str, dict] = {
            'email_verification': {'name': 'Email Verification', 'expiry': 300},
            'login_2fa': {'name': '2FA Login', 'expiry': 180},
            'password_reset': {'name': 'Password Reset', 'expiry': 600},
            'transaction_verify': {'name': 'Transaction Verification', 'expiry': 120},
            'account_security': {'name': 'Account Security', 'expiry': 300}
        }
        self.load_data()

    def load_data(self):
        """Load user data from file if exists"""
        try:
            if os.path.exists('bot_data.json'):
                with open('bot_data.json', 'r') as f:
                    data = json.load(f)
                    self.users = data.get('users', {})
                    # Convert string keys back to int
                    self.users = {int(k): v for k, v in self.users.items()}
        except Exception as e:
            logger.error(f"Error loading data: {e}")

    def save_data(self):
        """Save user data to file"""
        try:
            data = {
                'users': self.users,
                'timestamp': datetime.now().isoformat()
            }
            with open('bot_data.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving data: {e}")

    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP code"""
        return ''.join(random.choices(string.digits, k=length))

    def is_otp_valid(self, user_id: int, otp: str) -> bool:
        """Check if OTP is valid and not expired"""
        if user_id not in self.otp_codes:
            return False
        
        otp_data = self.otp_codes[user_id]
        if otp_data['code'] != otp:
            return False
        
        # Check if OTP is expired
        if datetime.now() > otp_data['expires_at']:
            del self.otp_codes[user_id]
            return False
        
        return True

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        user = update.effective_user
        user_id = user.id
        
        # Register user if not exists
        if user_id not in self.users:
            self.users[user_id] = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'registered_at': datetime.now().isoformat(),
                'otp_count': 0,
                'verified_count': 0
            }
            self.save_data()
        
        welcome_message = f"""
🔐 **Welcome to OTP Bot!** 🔐

Hello {user.first_name}! I'm your secure OTP (One-Time Password) generator and verification bot.

**What I can do:**
• Generate secure OTP codes for various services
• Verify OTP codes with expiration
• Track your OTP usage
• Support multiple authentication scenarios

**Commands:**
/start - Show this welcome message
/generate - Generate a new OTP code
/verify - Verify an OTP code
/services - View available services
/stats - View your OTP statistics
/help - Get detailed help

**Quick Start:**
1. Click "Generate OTP" to create a new code
2. Use the code within the time limit
3. Verify it when needed

Let's get started! 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("🔑 Generate OTP", callback_data='generate')],
            [InlineKeyboardButton("✅ Verify OTP", callback_data='verify')],
            [InlineKeyboardButton("📊 My Stats", callback_data='stats')],
            [InlineKeyboardButton("🛠️ Services", callback_data='services')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Handle both message and callback query
        if update.callback_query:
            await update.callback_query.edit_message_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

    async def generate_otp_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /generate command"""
        await self.show_services_for_generation(update, context)

    async def show_services_for_generation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show services selection for OTP generation"""
        keyboard = []
        for service_id, service_info in self.services.items():
            keyboard.append([InlineKeyboardButton(
                f"🔐 {service_info['name']}", 
                callback_data=f'gen_{service_id}'
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Main", callback_data='main')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = """
🔑 **Select Service for OTP Generation**

Choose the service you want to generate an OTP for:
        """
        
        if update.callback_query:
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

    async def generate_otp_for_service(self, update: Update, context: ContextTypes.DEFAULT_TYPE, service_id: str) -> None:
        """Generate OTP for specific service"""
        user_id = update.effective_user.id
        service_info = self.services[service_id]
        
        # Generate OTP
        otp_code = self.generate_otp()
        expiry_seconds = service_info['expiry']
        expires_at = datetime.now() + timedelta(seconds=expiry_seconds)
        
        # Store OTP
        self.otp_codes[user_id] = {
            'code': otp_code,
            'service': service_id,
            'service_name': service_info['name'],
            'created_at': datetime.now(),
            'expires_at': expires_at,
            'used': False
        }
        
        # Update user stats
        self.users[user_id]['otp_count'] += 1
        self.save_data()
        
        # Format expiry time
        expiry_mins = expiry_seconds // 60
        expiry_secs = expiry_seconds % 60
        
        message = f"""
🔑 **OTP Generated Successfully!**

**Service:** {service_info['name']}
**OTP Code:** `{otp_code}`
**Expires in:** {expiry_mins}:{expiry_secs:02d} minutes
**Generated at:** {datetime.now().strftime('%H:%M:%S')}

⚠️ **Important:**
• This code is valid for {expiry_mins} minutes only
• Don't share this code with anyone
• Use it only for the intended service

*Tap the code to copy it*
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Verify This OTP", callback_data='verify_current')],
            [InlineKeyboardButton("🔄 Generate New OTP", callback_data='generate')],
            [InlineKeyboardButton("🔙 Back to Main", callback_data='main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

    async def verify_otp_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /verify command"""
        user_id = update.effective_user.id
        
        if user_id in self.otp_codes:
            otp_data = self.otp_codes[user_id]
            time_left = (otp_data['expires_at'] - datetime.now()).total_seconds()
            
            if time_left > 0:
                mins, secs = divmod(int(time_left), 60)
                current_otp_info = f"""
**Current OTP:** `{otp_data['code']}`
**Service:** {otp_data['service_name']}
**Time Left:** {mins}:{secs:02d}
                """
            else:
                current_otp_info = "❌ **No active OTP** (expired or not generated)"
        else:
            current_otp_info = "❌ **No active OTP** (not generated yet)"
        
        message = f"""
🔍 **OTP Verification**

{current_otp_info}

**To verify an OTP:**
1. Make sure you have an active OTP
2. Click "Verify Current OTP" or
3. Type the OTP code directly

**Options:**
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Verify Current OTP", callback_data='verify_current')],
            [InlineKeyboardButton("🔑 Generate New OTP", callback_data='generate')],
            [InlineKeyboardButton("🔙 Back to Main", callback_data='main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

    async def verify_current_otp(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Verify the current OTP"""
        user_id = update.effective_user.id
        
        if user_id not in self.otp_codes:
            message = "❌ **No OTP to verify!**\n\nPlease generate an OTP first."
            keyboard = [[InlineKeyboardButton("🔑 Generate OTP", callback_data='generate')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            return
        
        otp_data = self.otp_codes[user_id]
        
        if self.is_otp_valid(user_id, otp_data['code']):
            # Mark as used
            self.otp_codes[user_id]['used'] = True
            self.users[user_id]['verified_count'] += 1
            self.save_data()
            
            # Remove OTP after verification
            del self.otp_codes[user_id]
            
            message = f"""
✅ **OTP Verified Successfully!**

**Service:** {otp_data['service_name']}
**OTP Code:** `{otp_data['code']}`
**Verified at:** {datetime.now().strftime('%H:%M:%S')}

🎉 **Verification Complete!**
Your OTP has been successfully verified and is now used.
            """
        else:
            message = f"""
❌ **OTP Verification Failed!**

**Reason:** OTP has expired
**Service:** {otp_data['service_name']}
**OTP Code:** `{otp_data['code']}`

Please generate a new OTP code.
            """
        
        keyboard = [
            [InlineKeyboardButton("🔑 Generate New OTP", callback_data='generate')],
            [InlineKeyboardButton("📊 View Stats", callback_data='stats')],
            [InlineKeyboardButton("🔙 Back to Main", callback_data='main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show user statistics"""
        user_id = update.effective_user.id
        user_data = self.users[user_id]
        
        # Current OTP info
        current_otp_info = ""
        if user_id in self.otp_codes:
            otp_data = self.otp_codes[user_id]
            time_left = (otp_data['expires_at'] - datetime.now()).total_seconds()
            
            if time_left > 0:
                mins, secs = divmod(int(time_left), 60)
                current_otp_info = f"""
**🔄 Current OTP Status:**
• Code: `{otp_data['code']}`
• Service: {otp_data['service_name']}
• Time Left: {mins}:{secs:02d}
• Status: Active ✅
                """
            else:
                current_otp_info = """
**🔄 Current OTP Status:**
• Status: Expired ❌
                """
        else:
            current_otp_info = """
**🔄 Current OTP Status:**
• Status: No active OTP
            """
        
        registered_date = datetime.fromisoformat(user_data['registered_at']).strftime('%B %d, %Y')
        
        message = f"""
📊 **Your OTP Statistics**

**👤 User Info:**
• Name: {user_data['first_name']} {user_data.get('last_name', '') or ''}
• Username: @{user_data.get('username', 'N/A')}
• Registered: {registered_date}

**📈 Usage Stats:**
• Total OTPs Generated: {user_data['otp_count']}
• Total OTPs Verified: {user_data['verified_count']}
• Success Rate: {(user_data['verified_count'] / max(user_data['otp_count'], 1) * 100):.1f}%

{current_otp_info}

**🛠️ Available Services:** {len(self.services)}
        """
        
        keyboard = [
            [InlineKeyboardButton("🔑 Generate OTP", callback_data='generate')],
            [InlineKeyboardButton("✅ Verify OTP", callback_data='verify')],
            [InlineKeyboardButton("🔙 Back to Main", callback_data='main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_services(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show available services"""
        message = """
🛠️ **Available OTP Services**

Here are the services you can generate OTPs for:
        """
        
        for service_id, service_info in self.services.items():
            expiry_mins = service_info['expiry'] // 60
            message += f"\n**{service_info['name']}**\n• Expiry: {expiry_mins} minutes\n• ID: `{service_id}`\n"
        
        message += """
**How to use:**
1. Select "Generate OTP" from the main menu
2. Choose the service you need
3. Use the generated OTP within the time limit
4. Verify when prompted

**Security Features:**
• Time-limited codes
• Single-use verification
• Secure generation algorithm
• Usage tracking
        """
        
        keyboard = [
            [InlineKeyboardButton("🔑 Generate OTP", callback_data='generate')],
            [InlineKeyboardButton("🔙 Back to Main", callback_data='main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        message = """
🆘 **OTP Bot Help**

**Commands:**
• `/start` - Welcome message and main menu
• `/generate` - Generate a new OTP code
• `/verify` - Verify an OTP code
• `/services` - View available services
• `/stats` - View your usage statistics
• `/help` - Show this help message

**How OTP Generation Works:**
1. Select a service (Email, 2FA, etc.)
2. Bot generates a 6-digit code
3. Code expires after set time
4. Use code for verification

**Security Features:**
• ⏰ Time-limited codes (2-10 minutes)
• 🔒 Single-use verification
• 🛡️ Secure random generation
• 📊 Usage tracking
• 🚫 Automatic expiry

**Tips:**
• Generate OTP only when needed
• Don't share codes with others
• Use codes within expiry time
• Keep track of your usage stats

**Support:**
If you encounter any issues, please contact the bot administrator.

**Version:** 1.0.0
**Last Updated:** December 2024
        """
        
        keyboard = [
            [InlineKeyboardButton("🔑 Generate OTP", callback_data='generate')],
            [InlineKeyboardButton("🔙 Back to Main", callback_data='main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages (potential OTP codes)"""
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        # Check if it's a 6-digit number (potential OTP)
        if message_text.isdigit() and len(message_text) == 6:
            if user_id in self.otp_codes:
                if self.is_otp_valid(user_id, message_text):
                    # Mark as used
                    otp_data = self.otp_codes[user_id]
                    self.otp_codes[user_id]['used'] = True
                    self.users[user_id]['verified_count'] += 1
                    self.save_data()
                    
                    # Remove OTP after verification
                    del self.otp_codes[user_id]
                    
                    await update.message.reply_text(
                        f"✅ **OTP Verified Successfully!**\n\n"
                        f"**Service:** {otp_data['service_name']}\n"
                        f"**Code:** `{message_text}`\n"
                        f"**Verified at:** {datetime.now().strftime('%H:%M:%S')}\n\n"
                        f"🎉 Your OTP has been successfully verified!",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text(
                        "❌ **Invalid or Expired OTP**\n\n"
                        "The OTP you entered is either:\n"
                        "• Incorrect\n"
                        "• Expired\n"
                        "• Already used\n\n"
                        "Please generate a new OTP code.",
                        parse_mode='Markdown'
                    )
            else:
                await update.message.reply_text(
                    "❌ **No Active OTP**\n\n"
                    "You don't have any active OTP to verify.\n"
                    "Please generate an OTP first using /generate",
                    parse_mode='Markdown'
                )
        else:
            # Not an OTP, show help
            await update.message.reply_text(
                "🤔 **I didn't understand that**\n\n"
                "I can help you with:\n"
                "• Generate OTP codes\n"
                "• Verify OTP codes\n"
                "• View statistics\n\n"
                "Use /help for more information or /start for the main menu.",
                parse_mode='Markdown'
            )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'main':
            await self.start(update, context)
        elif query.data == 'generate':
            await self.show_services_for_generation(update, context)
        elif query.data == 'verify':
            await self.verify_otp_command(update, context)
        elif query.data == 'verify_current':
            await self.verify_current_otp(update, context)
        elif query.data == 'stats':
            await self.show_stats(update, context)
        elif query.data == 'services':
            await self.show_services(update, context)
        elif query.data.startswith('gen_'):
            service_id = query.data[4:]  # Remove 'gen_' prefix
            await self.generate_otp_for_service(update, context, service_id)

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /stats command"""
        await self.show_stats(update, context)

    async def services_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /services command"""
        await self.show_services(update, context)

    def run(self):
        """Run the bot"""
        # Create application
        application = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("generate", self.generate_otp_command))
        application.add_handler(CommandHandler("verify", self.verify_otp_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("services", self.services_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        
        # Run the bot
        print("🤖 OTP Bot is starting...")
        print("📱 Bot is ready to generate and verify OTP codes!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Main function"""
    # Replace with your bot token from @BotFather
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Error: Please set your bot token!")
        print("1. Create a bot with @BotFather on Telegram")
        print("2. Get your bot token")
        print("3. Replace 'YOUR_BOT_TOKEN_HERE' with your actual token")
        return
    
    # Create and run the bot
    bot = OTPBot(BOT_TOKEN)
    bot.run()

if __name__ == "__main__":
    main()
