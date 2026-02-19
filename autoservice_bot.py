"""
Telebot script template for an auto service assistant.

This script implements a simple Telegram bot that guides users through
booking an appointment for automotive services such as polishing,
interior cleaning (\u0445\u0438\u043c\u0447\u0438\u0441\u0442\u043a\u0430), ceramic coating, or other services.

The bot asks the user to select a service, then prompts for the make
and model of the vehicle, and finally asks for a convenient time to
book the service. After collecting this information, it sends a
confirmation message to the user, notifies the administrator with the
details of the request, and logs the request to a local CSV file.

To use this script you must:
  1. Install the `python-telegram-bot` library (version 20 or higher):
       pip install python-telegram-bot --upgrade
  2. Obtain a bot token from @BotFather on Telegram and set the
       BOT_TOKEN environment variable.
  3. Determine your administrator chat ID (e.g. your own Telegram
       numeric ID) and set the ADMIN_CHAT_ID environment variable.
  4. Run this script: python autoservice_bot.py

Note: This is a minimal example for demonstration purposes. In
production you might integrate with Google Sheets or a database
instead of writing to a CSV file. Also, you should secure your bot
token and handle exceptions appropriately.
"""

import logging
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# --- Configuration ---
BOT_TOKEN: str = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID: int = int(os.getenv("ADMIN_CHAT_ID") or 0)

LOG_FILE: str = "requests.csv"
SERVICE, CAR, TIME = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [
        ["\u041f\u043e\u043b\u0438\u0440\u043e\u0432\u043a\u0430", "\u0425\u0438\u043c\u0447\u0438\u0441\u0442\u043a\u0430"],
        ["\u041a\u0435\u0440\u0430\u043c\u0438\u043a\u0430", "\u0414\u0440\u0443\u0433\u043e\u0435"],
    ]
    await update.message.reply_text(
        "\u0417\u0434\u0440\u0430\u0432\u0441\u0442\u0432\u0443\u0439\u0442\u0435! \u041a\u0430\u043a\u0430\u044f \u0443\u0441\u043b\u0443\u0433\u0430 \u0438\u043d\u0442\u0435\u0440\u0435\u0441\u0443\u0435\u0442?\n\n"
        "\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0432\u0430\u0440\u0438\u0430\u043d\u0442:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return SERVICE


async def service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["service"] = update.message.text
    await update.message.reply_text(
        "\u041d\u0430\u043f\u0438\u0448\u0438\u0442\u0435 \u043c\u0430\u0440\u043a\u0443 \u0438 \u043c\u043e\u0434\u0435\u043b\u044c \u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u044f:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return CAR


async def car(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["car"] = update.message.text
    await update.message.reply_text("\u041a\u043e\u0433\u0434\u0430 \u0443\u0434\u043e\u0431\u043d\u043e \u0437\u0430\u043f\u0438\u0441\u0430\u0442\u044c\u0441\u044f?")
    return TIME


async def time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["time"] = update.message.text
    await update.message.reply_text(
        "\u0421\u043f\u0430\u0441\u0438\u0431\u043e! \u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u0441\u0432\u044f\u0436\u0435\u0442\u0441\u044f \u0441 \u0432\u0430\u043c\u0438 \u0432 \u0431\u043b\u0438\u0436\u0430\u0439\u0448\u0435\u0435 \u0432\u0440\u0435\u043c\u044f.",
        reply_markup=ReplyKeyboardRemove(),
    )
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.full_name
    service_selected = context.user_data.get("service", "\u043d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u0430")
    car_model = context.user_data.get("car", "\u043d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u0430")
    time_requested = context.user_data.get("time", "\u043d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u043e")
    admin_text = (
        "\u041d\u043e\u0432\u0430\u044f \u0437\u0430\u044f\u0432\u043a\u0430:\n"
        f"\u0423\u0441\u043b\u0443\u0433\u0430: {service_selected}\n"
        f"\u0410\u0432\u0442\u043e: {car_model}\n"
        f"\u0412\u0440\u0435\u043c\u044f: {time_requested}\n"
        f"\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c: {username} (ID: {user.id})"
    )
    if ADMIN_CHAT_ID:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as file:
            file.write(f"{service_selected},{car_model},{time_requested},{user.id}\n")
    except Exception as e:
        logging.error("Failed to write request to log file: %s", e)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "\u041e\u043f\u0435\u0440\u0430\u0446\u0438\u044f \u043e\u0442\u043c\u0435\u043d\u0435\u043d\u0430.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)
    if not BOT_TOKEN:
        logger.error(
            "BOT_TOKEN is not set. Please set BOT_TOKEN environment variable."
        )
        return
    application = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, service)],
            CAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, car)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, time)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)
    logger.info("Bot is starting...")
    application.run_polling()


if __name__ == "__main__":
    main()
