import os
import logging
import csv

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

# Conversation states
SERVICE, CAR, TIME = range(3)

# Load token and admin chat ID from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

# Set up basic logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user for the desired service."""
    reply_keyboard = [[
        'Полировка',
        'Химчистка',
        'Керамика',
        'Другое',
    ]]
    update.message.reply_text(
        'Здравствуйте! Какая услуга вас интересует?\n\n'
        'Выберите нужную услугу:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return SERVICE

def service(update: Update, context: CallbackContext) -> int:
    """Stores the selected service and asks for the car make/model."""
    context.user_data['service'] = update.message.text
    update.message.reply_text(
        'Напишите марку и модель вашего автомобиля:',
        reply_markup=ReplyKeyboardRemove(),
    )
    return CAR

def car(update: Update, context: CallbackContext) -> int:
    """Stores the car info and asks for a convenient time."""
    context.user_data['car'] = update.message.text
    update.message.reply_text('Когда вам удобно записаться?')
    return TIME

def time(update: Update, context: CallbackContext) -> int:
    """Stores the preferred time, notifies the admin, writes to CSV, and ends the conversation."""
    context.user_data['time'] = update.message.text

    service_name = context.user_data.get('service')
    car_info = context.user_data.get('car')
    time_slot = context.user_data.get('time')

    # Notify the admin with the request details
    user = update.message.from_user
    admin_message = (
        f"Новая заявка:\n"
        f"Услуга: {service_name}\n"
        f"Авто: {car_info}\n"
        f"Время: {time_slot}\n"
        f"От: @{user.username if user.username else user.first_name}"
    )
    if ADMIN_CHAT_ID:
        try:
            context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)
        except Exception as e:
            logger.error('Failed to send message to admin: %s', e)

    # Save the request to a CSV file
    try:
        with open('requests.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([user.id, service_name, car_info, time_slot])
    except Exception as e:
        logger.error('Error writing to CSV: %s', e)

    # Acknowledge the user
    update.message.reply_text(
        'Спасибо! Ваш запрос принят. Мы свяжемся с вами в ближайшее время.',
        reply_markup=ReplyKeyboardRemove(),
    )

    # Clear user data
    context.user_data.clear()
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels the conversation."""
    update.message.reply_text(
        'Диалог отменён. Если понадобится помощь, просто отправьте команду /start.',
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END

def main() -> None:
    """Runs the bot."""
    # Ensure that the token is provided
    if not BOT_TOKEN:
        raise ValueError('BOT_TOKEN environment variable is not set')

    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Set up the conversation handler with the states SERVICE, CAR, TIME
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SERVICE: [MessageHandler(Filters.text & ~Filters.command, service)],
            CAR: [MessageHandler(Filters.text & ~Filters.command, car)],
            TIME: [MessageHandler(Filters.text & ~Filters.command, time)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
