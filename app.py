from flask import Flask, request, render_template_string
import os
import secrets
import string
import sqlite3
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')

# Telegram config
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Database setup
def init_db():
    conn = sqlite3.connect('canary.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            id TEXT PRIMARY KEY,
            token_type TEXT,
            name TEXT,
            created_at TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS triggers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_id TEXT,
            ip_address TEXT,
            user_agent TEXT,
            triggered_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def generate_token_id():
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(16))

def send_telegram_alert(token_name, ip, user_agent):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured")
        return
    
    message = f"""
🚨 CANARY TOKEN TRIGGERED!

Token: {token_name}
IP: {ip}
User Agent: {user_agent[:100]}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ Investigate immediately!
"""
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
        requests.post(url, data=data, timeout=10)
        print("Alert sent to Telegram!")
    except Exception as e:
        print(f"Failed to send alert: {e}")

@app.route('/')
def dashboard():
    conn = sqlite3.connect('canary.db')
    cursor = conn.cursor()
    
    # Get all tokens
    cursor.execute('SELECT * FROM tokens ORDER BY created_at DESC')
    tokens = cursor.fetchall()
    
    # Get recent triggers
    cursor.execute('''
        SELECT triggers.*, tokens.name 
        FROM triggers 
        JOIN tokens ON triggers.token_id = tokens.id 
        ORDER BY triggered_at DESC 
        LIMIT 20
    ''')
    triggers = cursor.fetchall()
    conn.close()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🪤 Canary Token System</title>
        <style>
            body { font-family: Arial; background: #0a0e27; color: white; margin: 0; padding: 20px; }
            h1 { color: #00ff88; }
            .card { background: #1a1f3e; padding: 20px; margin: 20px 0; border-radius: 10px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #333; }
            .btn { background: #00ff88; color: black; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }
            code { background: #0a0e27; padding: 2px 6px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <h1>🪤 Canary Token System</h1>
        
        <div class="card">
            <a href="/generate" class="btn">➕ Create New Token</a>
        </div>
        
        <div class="card">
            <h2>📋 Your Tokens</h2>
            <table>
                <tr><th>ID</th><th>Type</th><th>Name</th><th>Created</th><th>Status</th></tr>
                {% for token in tokens %}
                <tr>
                    <td><code>{{ token[0][:8] }}...</code></td>
                    <td>{{ token[1] }}</td>
                    <td>{{ token[2] }}</td>
                    <td>{{ token[3][:16] }}</td>
                    <td>🟢 Active</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        
        <div class="card">
            <h2>🚨 Trigger History</h2>
            <table>
                <tr><th>Time</th><th>Token</th><th>IP Address</th><th>User Agent</th></tr>
                {% for trigger in triggers %}
                <tr style="background: rgba(255,68,68,0.1);">
                    <td>{{ trigger[4][:16] }}</td>
                    <td>{{ trigger[5] }}</td>
                    <td><code>{{ trigger[2] }}</code></td>
                    <td>{{ trigger[3][:40] }}...</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    '''
 
    return render_template_string(html, tokens=tokens, triggers=triggers)

@app.route('/generate')
def generate_form():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Create Token</title>
        <style>
            body { font-family: Arial; background: #0a0e27; color: white; padding: 20px; }
            .card { background: #1a1f3e; padding: 20px; border-radius: 10px; max-width: 500px; }
            input, select { padding: 10px; margin: 10px 0; width: 100%; }
            .btn { background: #00ff88; color: black; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Create Canary Token</h1>
            <form method="POST">
                <label>Token Type:</label><br>
                <select name="token_type">
                    <option value="url">URL Token (Click tracking)</option>
                </select><br>
                <label>Token Name:</label><br>
                <input type="text" name="name" placeholder="e.g., fake-passwords" required><br>
                <button type="submit" class="btn">✨ Generate Token</button>
            </form>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/generate', methods=['POST'])
def create_token():
    token_type = request.form.get('token_type')
    name = request.form.get('name')
    token_id = generate_token_id()

    conn = sqlite3.connect('canary.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tokens VALUES (?, ?, ?, ?)',
                   (token_id, token_type, name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

    token_url = f"http://127.0.0.1:5000/token/{token_id}"

    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Token Created</title>
        <style>
            body {{ font-family: Arial; background: #0a0e27; color: white; padding: 20px; }}
            .card {{ background: #1a1f3e; padding: 20px; border-radius: 10px; }}
            .token {{ background: #0a0e27; padding: 15px; font-family: monospace; word-break: break-all; }}
            .btn {{ background: #00ff88; color: black; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>✅ Token Created!</h1>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Type:</strong> {token_type}</p>
            <p><strong>Token URL:</strong></p>
            <div class="token">{token_url}</div>
            <p>⚠️ Save this URL! You won't see it again.</p>
            <a href="/" class="btn">← Back to Dashboard</a>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/token/<token_id>')
def token_triggered(token_id):
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')

    conn = sqlite3.connect('canary.db')
    cursor = conn.cursor()

    # Get token name
    cursor.execute('SELECT name FROM tokens WHERE id = ?', (token_id,))
    token = cursor.fetchone()

    if token:
        # Log trigger
        cursor.execute('INSERT INTO triggers (token_id, ip_address, user_agent, triggered_at) VALUES (?, ?, ?, ?)',
                       (token_id, ip, user_agent, datetime.now().isoformat()))
        conn.commit()

        # Send alert
        send_telegram_alert(token[0], ip, user_agent)

    conn.close()

    # Return fake 404 page to attacker
    return "Page not found", 404

if __name__ == '__main__':
    print("🪤 Canary Token System Starting...")
    print(f"📍 Dashboard: http://127.0.0.1:5000")
    app.run(debug=True)
