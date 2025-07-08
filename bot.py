import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, 
    CallbackQueryHandler, ContextTypes, ConversationHandler,
    MessageHandler, filters
)
from dotenv import load_dotenv

# Load environment
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Conversation states
GET_TWITTER, GET_FACEBOOK, GET_WALLET = range(3)

# Start command with updated social links
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    welcome_msg = (
        "🌟 *Welcome to Mr. Emmanuel's Airdrop!* 🌟\n\n"
        "To qualify for the airdrop:\n"
        "1. Join our [Telegram Channel](https://t.me/dawgs_on_solana)\n"
        "2. Join our [Telegram Group](https://t.me/dawgs_on_sol)\n"
        "3. Follow us on [Twitter](https://x.com/DAWGS_On_Sol)\n"
        "4. Like our [Facebook Page](https://www.facebook.com/prolificdawg)\n"
        "5. Submit your Solana wallet address\n\n"
        "_Complete all steps to receive your rewards!_"
    )
    
    keyboard = [
        [InlineKeyboardButton("🚀 Start Verification", callback_data="start_verification")],
        [
            InlineKeyboardButton("📢 Channel", url="https://t.me/dawgs_on_solana"),
            InlineKeyboardButton("👥 Group", url="https://t.me/dawgs_on_sol")
        ],
        [
            InlineKeyboardButton("🐦 Twitter", url="https://x.com/DAWGS_On_Sol"),
            InlineKeyboardButton("📘 Facebook", url="https://www.facebook.com/prolificdawg")
        ]
    ]
    
    await update.message.reply_text(
        welcome_msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# Start verification process
async def start_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🕵️‍♂️ *Verification Process Started!*\n\n"
        "We trust you've completed all social tasks!\n"
        "Please send your Twitter username (e.g., @yourhandle):",
        parse_mode="Markdown"
    )
    return GET_TWITTER

# Twitter handler
async def get_twitter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['twitter'] = update.message.text
    await update.message.reply_text(
        "👍 Got it! Now send your Facebook profile name:"
    )
    return GET_FACEBOOK

# Facebook handler
async def get_facebook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['facebook'] = update.message.text
    await update.message.reply_text(
        "✅ Almost done! Now send your Solana wallet address:"
    )
    return GET_WALLET

# Wallet handler with reward messages
async def get_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wallet = update.message.text
    # Playful SOL address validation
    if wallet.startswith("SOL") or len(wallet) > 30:
        await update.message.reply_text(
            "🎉 *Congratulations! 10 SOL is on its way to your address!*\n"
            "Hope you didn't cheat the system! 😉",
            parse_mode="Markdown"
        )
        
        # Final congratulations message
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="🏆 *EPIC WIN!* 🏆\n\n"
            "You've successfully passed Mr. Emmanuel's airdrop challenge!\n"
            "💎 *100 SOL* will be magically transported to your wallet soon!\n\n"
            "✨ _Thank you for participating!_ ✨",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "⚠️ That doesn't look like a SOL address! Try again:"
        )
        return GET_WALLET
    return ConversationHandler.END

# Cancel handler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Registration canceled.")
    return ConversationHandler.END

# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Update {update} caused error {context.error}")
    await update.message.reply_text("😵 Oops! Something went wrong. Try /start again")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_verification, pattern="^start_verification$")],
        states={
            GET_TWITTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_twitter)],
            GET_FACEBOOK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_facebook)],
            GET_WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_wallet)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_error_handler(error)
    
    application.run_polling()

if __name__ == "__main__":
    print("🤖 Bot is running...")
    main()
