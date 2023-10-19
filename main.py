from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, Updater
from telegram import ReplyKeyboardMarkup
from telegram import Update
import logging
from src import bingoBook, libgenBook

import http.server as server


updater = Updater(
    token="5111390761:AAGd2eg0BWAwURt0VPL4ZGkuKyyXvzmwB_g", use_context=True)

dispatcher = updater.dispatcher

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def start(update: Update, context: CallbackContext):
    keyboard = [
        ["/start", "/test"],
        ["/bing", "/libgen"],
        ["/help"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    start_text = """
I'm a bot, please talk to me!
To see a list of available commands, type /help.
"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=start_text, reply_markup=reply_markup)


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


def help_command(update: Update, context: CallbackContext):
    help_text = """
Here are the commands you can use:

/start - Start the bot.
/test - Check if the bot is working.
/bing [book_name] - Search for a book on BingoBook.
/libgen [book_name] - Search for a book on LibGen.
/help - Display this help message.
And you can also send a document to the bot to retrieve its file ID.

Note: For /bing and /libgen commands, replace [book_name] with the name of the book you're looking for.
"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)



from telegram.ext import ConversationHandler

# Define states for the conversation
WAITING_FOR_BING_BOOKNAME, WAITING_FOR_LIBGEN_BOOKNAME = range(2)

def book_bing(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Please provide the name of the book you're looking for.")
        return WAITING_FOR_BING_BOOKNAME
    book_name = ' '.join(context.args)
    send_bing_book_response(update, context, book_name)
    return ConversationHandler.END

def book_libgen(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Please provide the name of the book you're looking for.")
        return WAITING_FOR_LIBGEN_BOOKNAME
    book_name = ' '.join(context.args)
    send_libgen_book_response(update, context, book_name)
    return ConversationHandler.END

def send_bing_book_response(update: Update, context: CallbackContext, book_name: str):
    books = bingoBook(book_name)
    update.message.reply_document(caption=f"{books[0]['title']}", document=books[0]['url'])

def send_libgen_book_response(update: Update, context: CallbackContext, book_name: str):
    books = libgenBook(book_name)
    add = "&random=1" if '?' in books[0]['url'] else "?random=1"
    update.message.reply_text(f"{books[0]['title']} , download link for the book is {books[0]['url']}")
    update.message.reply_document(caption=f"{books[0]['title']}", document=f"{books[0]['url']}{add}")

def get_bing_bookname(update: Update, context: CallbackContext):
    book_name = update.message.text
    send_bing_book_response(update, context, book_name)
    return ConversationHandler.END

def get_libgen_bookname(update: Update, context: CallbackContext):
    book_name = update.message.text
    send_libgen_book_response(update, context, book_name)
    return ConversationHandler.END

# Create conversation handler for Bing
bing_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('bing', book_bing)],
    states={
        WAITING_FOR_BING_BOOKNAME: [MessageHandler(Filters.text & ~Filters.command, get_bing_bookname)]
    },
    fallbacks=[]
)

# Create conversation handler for LibGen
libgen_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('libgen', book_libgen)],
    states={
        WAITING_FOR_LIBGEN_BOOKNAME: [MessageHandler(Filters.text & ~Filters.command, get_libgen_bookname)]
    },
    fallbacks=[]
)

# Add handlers to the dispatcher
dispatcher.add_handler(bing_conversation_handler)
dispatcher.add_handler(libgen_conversation_handler)


start_handler = CommandHandler('start', start)

help_handler = CommandHandler('help', help_command)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(CommandHandler('test', check))
dispatcher.add_handler(CommandHandler('bing', book_bing))
dispatcher.add_handler(CommandHandler('libgen', book_libgen))
dispatcher.add_handler(MessageHandler(Filters.document, file_handler))

updater.start_polling()
