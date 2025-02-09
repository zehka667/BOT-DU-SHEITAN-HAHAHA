from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# 🔑 Remplace avec ton token API
TOKEN = "8129568801:AAFZA__AxqXMrxEgwDdIOLZcFNMZVMm37B8"

# 🆔 Remplace avec ton propre ID Telegram
ADMIN_CHAT_ID = 7782664298  

def start(update: Update, context: CallbackContext) -> None:
    """ Répond uniquement au démarrage du bot """
    user = update.message.from_user
    update.message.reply_text("Bienvenue chez MEGA bot. Comment puis-je vous aider ?")

    # Envoyer une notification à l'admin
    context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"👤 Nouvel utilisateur : {user.first_name} (@{user.username}) a démarré le bot."
    )

def forward_message(update: Update, context: CallbackContext) -> None:
    """ Transfère tous les messages reçus à l'admin sans répondre à l'utilisateur """
    user = update.message.from_user
    message_text = update.message.text

    context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"📩 Message de {user.first_name} (@{user.username}):\n\n{message_text}"
    )

def main():
    """ Lancer le bot """
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Gérer la commande /start
    dp.add_handler(CommandHandler("start", start))

    # Gérer tous les messages texte envoyés par les utilisateurs sans réponse
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, forward_message))

    # Démarrer le bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
