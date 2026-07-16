import sqlite3
import telebot
import os
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

# --- Configuration ---
# Load environment variables from .env file
load_dotenv()

# Extract the Telegram bot token from environment variables
API_TOKEN = os.getenv('TELEGRAM_TOKEN')
if not API_TOKEN:
    raise ValueError("ERROR: Token not found")

# Obtain the base directory and database path
BASE_DIR = Path(__file__).resolve().parent.parent
default_db_path = BASE_DIR / "Data" / "bot_logs.db"
DB_PATH = Path(os.getenv('DB_PATH', default_db_path))

bot = telebot.TeleBot(API_TOKEN)

def init_db() -> None:
    """
    Ensures the database and the 'InteractionLogs' table exist before the bot starts.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS InteractionLogs (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                TelegramUserId INTEGER NOT NULL,
                Username TEXT,
                MessageText TEXT NOT NULL,
                Timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()
    print("Database and table initialized successfully.")

def log_interaction(user_id: int, username: str, message_text: str) -> None:
    """
    Saves a log of the user's interaction into the SQLite database.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO InteractionLogs (TelegramUserId, Username, MessageText, Timestamp)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, message_text, timestamp))
        conn.commit()
    print(f"Logged: User {username} ({user_id}) sent '{message_text}'")

# --- SQL Logic for Bot Commands ---

def get_global_stats() -> Tuple[int, int]:
    """
    Queries the database using SQL aggregation functions.
    Returns a tuple: (total_messages, unique_users)
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*), 
                COUNT(DISTINCT TelegramUserId) 
            FROM InteractionLogs
        ''')
        result = cursor.fetchone()

    return result if result else (0, 0)

def get_user_history(user_id: int) -> List[Tuple[str, str]]:
    """
    Queries the database using WHERE, ORDER BY, and LIMIT.
    Returns the last 5 messages sent by a specific user.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT MessageText, Timestamp 
            FROM InteractionLogs 
            WHERE TelegramUserId = ? 
            ORDER BY Id DESC 
            LIMIT 5
        ''', (user_id,))
        results = cursor.fetchall()
        
    return results

# --- Bot Event Handlers ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: telebot.types.Message) -> None:
    """
    Handles the /start and /help commands.
    """
    user_id = message.from_user.id
    username = message.from_user.username or "Anonymous"
    
    welcome_text = (
        f"Hello, {username}! 🤖\n\n"
        "I am an advanced Notification Bot.\n\n"
        "Try these commands:\n"
        "📊 /stats - Show global bot statistics (SQL aggregate queries)\n"
        "📜 /history - Show your last 5 logged messages\n"
        "✍️ Or just send me any text to log it!"
    )
    
    bot.reply_to(message, welcome_text)
    log_interaction(user_id, username, message.text)

@bot.message_handler(commands=['stats'])
def show_stats(message: telebot.types.Message) -> None:
    """
    Fetches aggregate database data and replies with global stats.
    """
    user_id = message.from_user.id
    username = message.from_user.username or "Anonymous"
    
    total_msgs, unique_users = get_global_stats()
    
    response = (
        "📊 *Global System Statistics*\n\n"
        f"Total Messages Logged: `{total_msgs}`\n"
        f"Unique Active Users: `{unique_users}`"
    )
    
    bot.reply_to(message, response, parse_mode="Markdown")
    log_interaction(user_id, username, message.text)

@bot.message_handler(commands=['history'])
def show_history(message: telebot.types.Message) -> None:
    """
    Fetches filtered database data and replies with user-specific history.
    """
    user_id = message.from_user.id
    username = message.from_user.username or "Anonymous"
    
    history = get_user_history(user_id)
    
    if not history:
        bot.reply_to(message, "You don't have any logged messages yet.")
        return

    response_lines = ["📜 *Your Last 5 Logged Messages:*\n"]
    for i, (msg_text, timestamp) in enumerate(history, 1):
        response_lines.append(f"{i}. *\"{msg_text}\"* \n   _Logged at: {timestamp}_")
        
    response = "\n".join(response_lines)
    
    bot.reply_to(message, response, parse_mode="Markdown")
    log_interaction(user_id, username, message.text)

@bot.message_handler(func=lambda message: True)
def echo_all(message: telebot.types.Message) -> None:
    """
    Catches any other text message, replies to the user, and logs it.
    """
    user_id = message.from_user.id
    username = message.from_user.username or "Anonymous"
    
    response_text = f"Logged: '{message.text}'"
    bot.reply_to(message, response_text)
    log_interaction(user_id, username, message.text)

# --- Main Entry Point ---
if __name__ == "__main__":
    init_db()
    print("Bot is listening for messages... Press Ctrl+C to stop.")
    bot.infinity_polling()