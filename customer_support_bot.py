import os
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters

# Bot token and admin chat ID
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # Replace with your admin's chat ID

# A dictionary to track user messages and their IDs
user_message_map = {}

# Welcome Message
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("👥 Join My Telegram Channel", url="https://t.me/codesaif_group")],
        [InlineKeyboardButton("🛍️ Our Cheap Products", url="https://store.codesaif.in")],
        [InlineKeyboardButton("💼 Services", callback_data='view_services')],
        [InlineKeyboardButton("📩 Chat Admin", callback_data='chat_admin')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "🤖 *Welcome to Codesaif Customer Support Bot!*\n\nHow can we assist you today? Choose an option below:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

# Chat Admin
def chat_admin(update: Update, context: CallbackContext) -> None:
    update.callback_query.message.reply_text(
        "📩 *Chat Admin*\n\nSend your message directly here. We'll get back to you shortly!"
    )

# Handle User Messages
def handle_user_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat.id
    username = update.message.chat.username or "Anonymous"
    user_message = update.message.text

    # Save user details in the map
    user_message_map[user_id] = username

    # Forward user message to admin
    if ADMIN_CHAT_ID:
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"📩 *Message from @{username} (ID: {user_id}):*\n\n{user_message}",
            parse_mode=ParseMode.MARKDOWN
        )
    update.message.reply_text("✅ Your message has been sent to the admin. Please wait for a reply.")

# Handle Admin Replies
def handle_admin_reply(update: Update, context: CallbackContext) -> None:
    admin_message = update.message.text

    # Check if the message starts with "reply:" to identify a reply to a user
    if admin_message.startswith("reply:"):
        try:
            # Parse user ID and reply message
            parts = admin_message.split(":", 2)
            user_id = int(parts[1].strip())
            reply_message = parts[2].strip()

            # Send the reply to the user
            context.bot.send_message(
                chat_id=user_id,
                text=f"📩 *Reply from Admin:*\n\n{reply_message}",
                parse_mode=ParseMode.MARKDOWN
            )
            update.message.reply_text("✅ Reply sent to the user.")
        except (IndexError, ValueError):
            update.message.reply_text("❌ Invalid reply format. Use `reply:<user_id>:<message>`.")
    else:
        update.message.reply_text(
            "❌ To reply to a user, use the format `reply:<user_id>:<message>`."
        )

# Callback Query Handler
def handle_callbacks(update: Update, context: CallbackContext) -> None:
    query_data = update.callback_query.data
    if query_data == 'chat_admin':
        chat_admin(update, context)

# Dummy HTTP Server
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_http_server():
    server_address = ('', int(os.environ.get("PORT", 8000)))  # Default port 8000
    httpd = HTTPServer(server_address, DummyServer)
    httpd.serve_forever()

# Main Function
def main():
    # Start polling
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Command Handlers
    dispatcher.add_handler(CommandHandler('start', start))

    # Admin Replies Handler
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.chat(int(ADMIN_CHAT_ID)), handle_admin_reply))

    # Callback Query Handlers
    dispatcher.add_handler(CallbackQueryHandler(handle_callbacks))

    # User Messages Handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_user_message))

    # Run the polling bot in a thread
    Thread(target=updater.start_polling).start()

    # Start the dummy HTTP server
    run_http_server()

if __name__ == '__main__':
    main()
