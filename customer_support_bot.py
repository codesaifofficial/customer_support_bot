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
    user_message_map[update.message.message_id] = user_id

    # Forward user message to admin
    if ADMIN_CHAT_ID:
        forwarded_message = context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"📩 *Message from @{username} (ID: {user_id}):*\n\n{user_message}",
            parse_mode=ParseMode.MARKDOWN
        )
        # Save forwarded message ID for tracking replies
        user_message_map[forwarded_message.message_id] = user_id

    update.message.reply_text("✅ Your message has been sent to the admin. Please wait for a reply.")

# Handle Admin Replies
def handle_admin_reply(update: Update, context: CallbackContext) -> None:
    if update.message.reply_to_message:
        original_message_id = update.message.reply_to_message.message_id

        # Check if this message corresponds to a user
        if original_message_id in user_message_map:
            user_id = user_message_map[original_message_id]
            admin_reply = update.message.text

            # Send the reply to the original user
            context.bot.send_message(
                chat_id=user_id,
                text=f"📩 *Reply from Admin:*\n\n{admin_reply}",
                parse_mode=ParseMode.MARKDOWN
            )
            update.message.reply_text("✅ Reply sent to the user.")
        else:
            update.message.reply_text("❌ Unable to find the original user. Please ensure the message was forwarded correctly.")
    else:
        update.message.reply_text("❌ To reply to a user, reply to their forwarded message directly.")

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
