import os
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters

# Bot token and admin chat ID
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # Replace with your admin's chat ID

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

# Services Menu
def view_services(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("🌐 Web Development", callback_data='service_web')],
        [InlineKeyboardButton("🤖 Telegram Bot", callback_data='service_bot')],
        [InlineKeyboardButton("🛠️ Custom Project", callback_data='service_custom')],
        [InlineKeyboardButton("⬅️ Back", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.edit_text(
        "💼 *Our Services*\n\nChoose a service you’re interested in:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

# Handle Individual Services
def handle_service_selection(update: Update, context: CallbackContext) -> None:
    query_data = update.callback_query.data
    service_map = {
        "service_web": "🌐 *Web Development*\n\nWe build stunning websites tailored to your needs.",
        "service_bot": "🤖 *Telegram Bot*\n\nGet a custom bot for automation, support, and more.",
        "service_custom": "🛠️ *Custom Project*\n\nTell us your requirements and we'll bring your idea to life!"
    }
    selected_service = service_map.get(query_data, "Invalid selection")
    keyboard = [[InlineKeyboardButton("📩 Chat Admin", callback_data='chat_admin')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.edit_text(
        f"{selected_service}\n\nClick below to chat with our admin for more details.",
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
    user_message = update.message.text
    username = update.message.chat.username or "Anonymous"
    # Forward user message to admin
    if ADMIN_CHAT_ID:
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"📩 *Message from @{username}:*\n\n{user_message}",
            parse_mode=ParseMode.MARKDOWN
        )
    update.message.reply_text("✅ Your message has been sent to the admin. Please wait for a reply.")

# Handle Back to Main Menu
def back_to_menu(update: Update, context: CallbackContext) -> None:
    start(update.callback_query, context)

# Callback Query Handler
def handle_callbacks(update: Update, context: CallbackContext) -> None:
    query_data = update.callback_query.data
    if query_data == 'view_services':
        view_services(update, context)
    elif query_data in ['service_web', 'service_bot', 'service_custom']:
        handle_service_selection(update, context)
    elif query_data == 'chat_admin':
        chat_admin(update, context)
    elif query_data == 'back_to_menu':
        back_to_menu(update, context)

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

    # Callback Query Handlers
    dispatcher.add_handler(CallbackQueryHandler(handle_callbacks))

    # Message Handlers
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_user_message))

    # Run the polling bot in a thread
    Thread(target=updater.start_polling).start()

    # Start the dummy HTTP server
    run_http_server()

if __name__ == '__main__':
    main()
