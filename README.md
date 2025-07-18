# VaultGuard_TelegramBot
# 🔐 OTP Bot - Secure One-Time Password Generator

A sophisticated Telegram bot that generates and verifies secure One-Time Passwords (OTPs) for various authentication services. Built with Python and the python-telegram-bot library.

## ✨ Features

- **🔑 OTP Generation**: Generate secure 6-digit OTP codes
- **⏰ Time-Limited Codes**: Configurable expiry times (2-10 minutes)
- **🛡️ Multiple Services**: Support for various authentication scenarios
- **✅ Verification System**: Verify OTPs with automatic expiry
- **📊 Usage Statistics**: Track your OTP generation and verification stats
- **💾 Data Persistence**: Save user data and statistics
- **🎨 Interactive UI**: Rich inline keyboard interface
- **🔒 Security Features**: Single-use codes, automatic cleanup

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Installation

1. **Clone or download the bot code**
   ```bash
   git clone <repository-url>
   cd otp-bot
   ```

2. **Install required packages**
   ```bash
   pip install python-telegram-bot
   ```

3. **Get your Bot Token**
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Create a new bot with `/newbot`
   - Copy the token provided

4. **Configure the bot**
   - Open the Python file
   - Replace `"YOUR_BOT_TOKEN_HERE"` with your actual bot token
   - Save the file

5. **Run the bot**
   ```bash
   python otp_bot.py
   ```

## 🎯 Usage

### Commands

- `/start` - Welcome message and main menu
- `/generate` - Generate a new OTP code
- `/verify` - Verify an OTP code
- `/services` - View available services
- `/stats` - View your usage statistics
- `/help` - Show help information

### How to Use

1. **Start the bot**: Send `/start` to begin
2. **Generate OTP**: Click "Generate OTP" or use `/generate`
3. **Select Service**: Choose from available services
4. **Use the Code**: Copy the 6-digit code within the time limit
5. **Verify**: Click "Verify OTP" or send the code directly

## 🛠️ Available Services

| Service | Description | Expiry Time |
|---------|-------------|-------------|
| Email Verification | Email account verification | 5 minutes |
| 2FA Login | Two-factor authentication | 3 minutes |
| Password Reset | Password recovery | 10 minutes |
| Transaction Verification | Financial transaction auth | 2 minutes |
| Account Security | General security verification | 5 minutes |

## 🔧 Configuration

### Adding New Services

Modify the `services` dictionary in the `OTPBot` class:

```python
self.services = {
    'your_service_id': {
        'name': 'Your Service Name', 
        'expiry': 300  # seconds
    }
}
```

### Customizing OTP Length

Change the `generate_otp` method parameter:

```python
def generate_otp(self, length: int = 6) -> str:
    # Change the default length as needed
```

## 📁 File Structure

```
otp-bot/
├── otp_bot.py          # Main bot code
├── bot_data.json       # User data storage (auto-generated)
├── README.md           # This file
└── requirements.txt    # Python dependencies
```

## 💾 Data Storage

The bot automatically saves:
- User registration data
- OTP generation statistics
- Verification counts
- Usage patterns

Data is stored in `bot_data.json` and persists between restarts.

## 🔒 Security Features

- **Time-Limited Codes**: All OTPs expire automatically
- **Single-Use**: Each OTP can only be verified once
- **Secure Generation**: Uses cryptographically secure random numbers
- **No Storage of Sensitive Data**: OTPs are cleared after use
- **User Isolation**: Each user's data is separate

## 📊 Statistics Tracking

The bot tracks:
- Total OTPs generated
- Total OTPs verified
- Success rate
- Registration date
- Current active OTP status

## 🐛 Troubleshooting

### Common Issues

1. **Bot Token Error**
   - Ensure you've replaced the placeholder token
   - Check that the token is correct and active

2. **Import Errors**
   - Install required packages: `pip install python-telegram-bot`
   - Ensure Python 3.8+ is installed

3. **Bot Not Responding**
   - Check internet connection
   - Verify bot token is valid
   - Ensure the bot is running

4. **Data Not Saving**
   - Check file permissions in the bot directory
   - Ensure sufficient disk space

### Error Messages

- `"❌ Error: Please set your bot token!"` - Replace the placeholder token
- `"❌ No Active OTP"` - Generate an OTP first
- `"❌ Invalid or Expired OTP"` - Code is wrong or expired

## 📈 Performance

- **Lightweight**: Minimal resource usage
- **Fast Response**: Instant OTP generation
- **Scalable**: Handles multiple users simultaneously
- **Reliable**: Automatic error handling and recovery

## 🛡️ Best Practices

1. **Keep Your Token Secret**: Never share your bot token
2. **Regular Updates**: Keep the bot code updated
3. **Monitor Usage**: Check logs for unusual activity
4. **Backup Data**: Regularly backup `bot_data.json`
5. **Use HTTPS**: Deploy with SSL in production

## 🔄 Updates & Maintenance

### Version History

- **v1.0.0** (December 2024): Initial release
  - Basic OTP generation and verification
  - Multiple service support
  - Statistics tracking
  - Interactive UI

### Future Enhancements

- [ ] Custom OTP lengths
- [ ] Email integration
- [ ] Webhook support
- [ ] Admin panel
- [ ] Multi-language support

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the error messages
3. Contact the bot administrator
4. Check Telegram Bot API documentation

## 📄 License

This project is open source. Feel free to modify and distribute according to your needs.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test your changes
4. Submit a pull request

## 🙏 Acknowledgments

- Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Inspired by secure authentication practices
- Thanks to the Telegram Bot API team

---

**Made with ❤️ for secure authentication**

*Last Updated: 2025*
