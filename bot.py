from telegram.ext import Application, CommandHandler

async def start(update, context):
    await update.message.reply_text("Привет! Я бот.")

def main():
    app = Application.builder().token('7832997993:AAGp5G-cO0Yv9n8-fNxkrQA2Fwmo1flCd_o').build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
