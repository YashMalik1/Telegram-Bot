from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, Updater
from telegram import Update
import logging
from src import bingoBook, libgenBook


updater = Updater(
    token="5043185876:AAFKFXMhfdqlnhHOpdd9EYZxa2f_PMcUk1E", use_context=True)

dispatcher = updater.dispatcher

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def file_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    # retrieve file_id from document sent by user
    fileID = update.message['document']['file_id']
    context.bot.sendDocument(
        chat_id=chat_id, caption=f"This is the file that you've sent to bot, it's file ID is - {fileID}",
        document=fileID
    )

def book_bing(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    # retrieve file_id from document sent by user
    book_name = str(context.args)
    books = bingoBook(book_name)
    context.bot.sendDocument(
        chat_id=chat_id, caption=f"{books[0]['title']}",
        document=books[0]['url']
    )


def book_libgen(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    # retrieve file_id from document sent by user
    book_name = str(context.args)
    books = libgenBook(book_name)
    add = ""
    if('?' in books[0]['url']):
        add="&random=1"
    else:
        add="?random=1"
    context.bot.sendMessage(
        chat_id=chat_id, text=f"{books[0]['title']} , download link for the book is {books[0]['url']} ... this is just a temp measure .. the thing is that sometimes the telegram api throws an error")
    context.bot.sendDocument(
        chat_id=chat_id, caption=f"{books[0]['title']}",
        document=f"{books[0]['url']}{add}"
    )


def check(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="I am working vro :)")


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(CommandHandler('test', check))
dispatcher.add_handler(CommandHandler('bing', book_bing))
dispatcher.add_handler(CommandHandler('libgen', book_libgen))
dispatcher.add_handler(MessageHandler(Filters.document, file_handler))

updater.start_polling()
