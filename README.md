# VMSilentBot

## Introduction
VMSilentBot is an automation project using Selenium.

## System Requirements
- Python 3.13.1 or higher
- Google Chrome and compatible ChromeDriver
- Windows environment

## Installation

1. **Clone the project**:
   ```bash
   git clone https://github.com/ReGuide-Labs/VMSilentBotWindow.git
   cd VMSilentBot
   ```

2. **Create a virtual environment**:
   ```bash
   py -m venv venv
   source venv/bin/activate  # On Linux/MacOS
   venv\Scripts\activate     # On Windows
   ```

3. **Download and extract Chromium**:
   - Download the Chromium browser from the following link:
     [ungoogled-chromium_134.0.6998.88-1.1_windows_x64.zip](https://github.com/ungoogled-software/ungoogled-chromium-windows/releases/download/134.0.6998.88-1.1/ungoogled-chromium_134.0.6998.88-1.1_windows_x64.zip)
   - Extract the contents of the ZIP file into a folder named `chromium` in the project's root directory.

4. **Install required libraries**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure the token file**:
   - Create a file named `token.txt` in the project's root directory.
   - Add your tokens to this file, one token per line.

## Run the Project

1. **Start the bot**:
   ```bash
   py silentbot.py
   ```

2. **Monitor logs**:
   - The bot will automatically send notifications to Telegram when important events occur.

## Notes
- Ensure that you have correctly configured `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in the `silentbot.py` file.
- If you encounter errors, review the installation steps or contact support.

## Support Us
- **Donate (EVM)**: `0xfa98dc932041755636ed44a4e2455c33b2378ca9`
- **Join Telegram**: [https://t.me/ReReGuide](https://t.me/ReReGuide)
- **Follow on X**: [https://x.com/HeosRe](https://x.com/HeosRe)

