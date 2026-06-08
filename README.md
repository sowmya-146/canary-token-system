# Canary Token System

## Deception Technology for SOC / Blue Team

### What is this?
A web-based canary token system that creates fake tracking URLs. When attackers click them, you get instant Telegram alerts.

### Features
- Generate fake tracking URLs
- Real-time Telegram alerts with attacker IP
- Dashboard to see all triggers
- Fake 404 page (attacker doesn't know they're caught)

### Tech Stack
- Python 3.9+
- Flask (Web framework)
- SQLite (Database)
- Telegram API (Alerts)

### How to Run

```bash
# Clone repository
git clone https://github.com/sowmya-146/canary-token-system.git

# Go to folder
cd canary-token-system

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "TELEGRAM_BOT_TOKEN=your_token" > .env
echo "TELEGRAM_CHAT_ID=your_chat_id" >> .env
echo "SECRET_KEY=your_secret" >> .env

# Run the app
python app.py

## Screenshots

### Dashboard
![Dashboard](screenshots/dashboard-with-trigger.png)

### Create Token
![Create Token](screenshots/token-created.png)

### Telegram Alert (Working!)
![Telegram Alert](screenshots/telegram-alert.png)

### Fake 404 Page (Attacker View)
![Fake 404](screenshots/fake-404.png)
