# ---- Imports and Initial Setup ----
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackQueryHandler
import logging
from src import bingoBook, libgenBook

# Logging Setup
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

TOKEN = "5111390761:AAGd2eg0BWAwURt0VPL4ZGkuKyyXvzmwB_g"
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


# ---- Command Functions ----
def command_start(update: Update, context: CallbackContext):
    keyboard = [
        ["/start", "/test"],
        ["/bing", "/libgen"],
        ["/bookmark", "/viewbookmarks"],
        ["/annotate", "/viewannotations"],
        ["/viewdownloaded", "/help"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    start_text = """
Hello! I'm your book bot 📚
Here's what you can do:

/start - Restart the bot.
/test - Check if the bot is alive.
/bing [book_name] - Search for a book on BingoBook.
/libgen [book_name] - Search for a book on LibGen.
/bookmark [book_name] [page] - Bookmark a page in a book.
/viewbookmarks - View all your bookmarks.
/annotate [book_name] [page] [note] - Add an annotation to a book page.
/viewannotations - View all your annotations.
/viewdownloaded - View the books you've downloaded.
/help - Display detailed help.

For the /bing and /libgen commands, just replace [book_name] with the name of the book you're looking for.
"""
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=start_text, reply_markup=reply_markup)



def command_bing(update: Update, context: CallbackContext):
    if not context.args:  # Check if the user provided a book name as an argument
        update.message.reply_text(
            "Please provide the name of the book you're looking for.")
        # This will transition to the BING_BOOK_NAME state in the conversation handler
        return BING_BOOK_NAME
    book_name = ' '.join(context.args)
    send_bing_response(update, context, book_name)
    return ConversationHandler.END  # This will end the conversation


def command_libgen(update: Update, context: CallbackContext):
    if not context.args:  # Check if the user provided a book name as an argument
        update.message.reply_text(
            "Please provide the name of the book you're looking for.")
        # This will transition to the LIBGEN_BOOK_NAME state in the conversation handler
        return LIBGEN_BOOK_NAME
    book_name = ' '.join(context.args)
    send_libgen_response(update, context, book_name)
    return ConversationHandler.END  # This will end the conversation

def command_check(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="I am working!")


def command_help(update: Update, context: CallbackContext):
    help_text = """
Here are the commands you can use:

/start - Restart the bot.
/test - Check if the bot is alive.
/bing [book_name] - Search for a book on BingoBook.
/libgen [book_name] - Search for a book on LibGen.
/bookmark [book_name] [page] - Bookmark a page in a book.
/viewbookmarks - View all your bookmarks.
/annotate [book_name] [page] [note] - Add an annotation to a book page.
/viewannotations - View all your annotations.
/viewdownloaded - View the books you've downloaded.
/help - Display detailed help.

"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)


# ---- Utility Functions ----
def send_bing_response(update: Update, context: CallbackContext, book_name: str):
    user_id = update.effective_user.id
    books = bingoBook(book_name)
    if len(books) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Sorry for the inconvenience, we couldn't find the book.")
        return
    try:
        context.bot.send_document(chat_id=update.effective_chat.id,
                              caption=books[0]['title'], document=books[0]['url'])
    except:
        logging.info("Couldn't send the document. Sending the link instead.")
        context.bot.send_message(chat_id=update.effective_chat.id,
                                text=f"Couldn't send the document. Sending the link instead: {books[0]['url']}")
    # Store the downloaded book in the database
    store_downloaded_book(user_id, books[0]['title'], books[0]['url'])


def send_libgen_response(update: Update, context: CallbackContext, book_name: str):
    user_id = update.effective_user.id
    books = libgenBook(book_name)
    if len(books) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Sorry for the inconvenience, we couldn't find the book.")
        return
    randomizer = "&random=1" if '?' in books[0]['url'] else "?random=1"
    print(books[0]['url'])
    try:
        context.bot.send_document(chat_id=update.effective_chat.id,
                              caption=books[0]['title'], document=f"{books[0]['url']}{randomizer}")
    except:
        logging.info("Couldn't send the document. Sending the link instead.")
        context.bot.send_message(chat_id=update.effective_chat.id,
                                text=f"Couldn't send the document. Sending the link instead: {books[0]['url']}")
    # Store the downloaded book in the database
    store_downloaded_book(user_id, books[0]['title'], books[0]['url'])


def get_book_name_for_bing(update: Update, context: CallbackContext):
    book_name = update.message.text
    send_bing_response(update, context, book_name)
    return ConversationHandler.END


def get_book_name_for_libgen(update: Update, context: CallbackContext):
    book_name = update.message.text
    send_libgen_response(update, context, book_name)
    return ConversationHandler.END


# ---- Handlers and Dispatcher ----
BING_BOOK_NAME, LIBGEN_BOOK_NAME = range(2)

bing_handler = ConversationHandler(
    entry_points=[CommandHandler('bing', command_bing)],
    states={BING_BOOK_NAME: [MessageHandler(
        Filters.text & ~Filters.command, get_book_name_for_bing)]},
    fallbacks=[]
)
dispatcher.add_handler(bing_handler)

libgen_handler = ConversationHandler(
    entry_points=[CommandHandler('libgen', command_libgen)],
    states={LIBGEN_BOOK_NAME: [MessageHandler(
        Filters.text & ~Filters.command, get_book_name_for_libgen)]},
    fallbacks=[]
)
dispatcher.add_handler(libgen_handler)

dispatcher.add_handler(CommandHandler('start', command_start))
dispatcher.add_handler(CommandHandler('test', command_check))
dispatcher.add_handler(CommandHandler('help', command_help))


# SQLite setup
conn = sqlite3.connect('user_data.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS downloaded_books (
    user_id INTEGER,
    title TEXT,
    url TEXT,
    PRIMARY KEY(user_id, title)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS bookmarks (
    user_id INTEGER,
    title TEXT,
    page INTEGER,
    PRIMARY KEY(user_id, title, page)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS annotations (
    user_id INTEGER,
    title TEXT,
    page INTEGER,
    note TEXT,
    PRIMARY KEY(user_id, title, page)
)
''')
conn.commit()


def store_downloaded_book(user_id, title, url):
    cursor.execute(
        'INSERT OR IGNORE INTO downloaded_books (user_id, title, url) VALUES (?, ?, ?)', (user_id, title, url))
    conn.commit()

def send_downloaded_books(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    books = cursor.execute(
        'SELECT title FROM downloaded_books WHERE user_id = ?', (user_id,)).fetchall()
    if books:
        books_list = [book[0] for book in books]
        keyboard = [[book] for book in books_list]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Select a book to bookmark:", reply_markup=reply_markup)
        return SELECT_BOOK  # Transition to the SELECT_BOOK state
    else:
        update.message.reply_text("You haven't downloaded any books yet.")
        return ConversationHandler.END

# Add this function to handle the selected book for bookmarking


def bookmark_selected_book(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    selected_book = update.message.text
    context.user_data['selected_book'] = selected_book
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"Enter the page number for {selected_book}:")
    return ENTER_PAGE  # Transition to the ENTER_PAGE state


def bookmark_entered_page(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    selected_book = context.user_data['selected_book']
    page = int(update.message.text)
    cursor.execute(
        'INSERT OR IGNORE INTO bookmarks (user_id, title, page) VALUES (?, ?, ?)', (user_id, selected_book, page))
    conn.commit()
    update.message.reply_text(
        f"Bookmark added for {selected_book} on page {page}")
    return ConversationHandler.END

# ---- Handlers and Dispatcher ----


SELECT_BOOK, ENTER_PAGE = range(3, 5)  # Add new states

# Modify the bookmark handler to use the new functions
bookmark_handler = ConversationHandler(
    entry_points=[CommandHandler('bookmark', send_downloaded_books)],
    states={
        SELECT_BOOK: [MessageHandler(Filters.text & ~Filters.command, bookmark_selected_book)],
        ENTER_PAGE: [MessageHandler(
            Filters.text & ~Filters.command, bookmark_entered_page)]
    },
    fallbacks=[CommandHandler('start', command_start)]
)
dispatcher.add_handler(bookmark_handler)


# Define new states for ConversationHandler
SELECT_ACTION, SELECT_DOWNLOAD_OR_DELETE = range(6, 8)

# Add the /viewdownloaded command function to view downloaded books

def view_downloaded_books(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    books = cursor.execute(
        'SELECT title FROM downloaded_books WHERE user_id = ?', (user_id,)).fetchall()

    if books:
        books_list = [book[0] for book in books]
        keyboard = [[InlineKeyboardButton(
            book, callback_data=book)] for book in books_list]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Select a book:", reply_markup=reply_markup)
        return SELECT_ACTION
    else:
        update.message.reply_text("You haven't downloaded any books yet.")
        return ConversationHandler.END


def book_selected(update: Update, context: CallbackContext):
    query = update.callback_query
    selected_book = query.data
    context.user_data['selected_book'] = selected_book
    keyboard = [
        [InlineKeyboardButton("Download", callback_data="download"),
         InlineKeyboardButton("Delete", callback_data="delete")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_text(
        text=f"Selected: {selected_book}. What do you want to do?",
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=reply_markup
    )
    return SELECT_DOWNLOAD_OR_DELETE


def download_or_delete_book(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    query = update.callback_query
    action = query.data
    selected_book = context.user_data['selected_book']

    if action == "download":
        url = cursor.execute('SELECT url FROM downloaded_books WHERE user_id = ? AND title = ?',
                             (user_id, selected_book)).fetchone()[0]
        context.bot.send_document(
            chat_id=update.effective_chat.id, document=url)
        context.bot.edit_message_text(
            text=f"You chose to download: {selected_book}",
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
    elif action == "delete":
        cursor.execute(
            'DELETE FROM downloaded_books WHERE user_id = ? AND title = ?', (user_id, selected_book))
        conn.commit()
        context.bot.edit_message_text(
            text=f"{selected_book} has been deleted from your list.",
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

    return ConversationHandler.END

# ---- Handlers and Dispatcher ----


download_delete_handler = ConversationHandler(
    entry_points=[CommandHandler('viewdownloaded', view_downloaded_books)],
    states={
        SELECT_ACTION: [CallbackQueryHandler(book_selected)],
        SELECT_DOWNLOAD_OR_DELETE: [
            CallbackQueryHandler(download_or_delete_book)]
    },
    fallbacks=[CommandHandler('start', command_start)]
)
dispatcher.add_handler(download_delete_handler)


# Define new states for ConversationHandler
SELECT_BOOK_FOR_ANNOTATION, ENTER_PAGE_AND_NOTE = range(8, 10)


def send_downloaded_books_for_annotation(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    books = cursor.execute(
        'SELECT title FROM downloaded_books WHERE user_id = ?', (user_id,)).fetchall()

    if books:
        books_list = [book[0] for book in books]
        keyboard = [[book] for book in books_list]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Select a book to annotate:", reply_markup=reply_markup)
        return SELECT_BOOK_FOR_ANNOTATION
    else:
        update.message.reply_text("You haven't downloaded any books yet.")
        return ConversationHandler.END


def annotation_book_selected(update: Update, context: CallbackContext):
    selected_book = update.message.text
    context.user_data['selected_book_for_annotation'] = selected_book
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"Enter the page number and note for {selected_book} in the format 'page - note':")
    return ENTER_PAGE_AND_NOTE


def annotation_entered_page_and_note(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    selected_book = context.user_data['selected_book_for_annotation']
    page_note_data = update.message.text.split('-')

    if len(page_note_data) < 2:
        update.message.reply_text(
            "Please provide the input in the format 'page - note'.")
        return ENTER_PAGE_AND_NOTE

    page = int(page_note_data[0].strip())
    note = page_note_data[1].strip()

    cursor.execute('INSERT OR IGNORE INTO annotations (user_id, title, page, note) VALUES (?, ?, ?, ?)',
                   (user_id, selected_book, page, note))
    conn.commit()
    update.message.reply_text(
        f"Annotation added for {selected_book} on page {page}")
    return ConversationHandler.END

# ---- Handlers and Dispatcher ----


annotate_handler = ConversationHandler(
    entry_points=[CommandHandler(
        'annotate', send_downloaded_books_for_annotation)],
    states={
        SELECT_BOOK_FOR_ANNOTATION: [MessageHandler(Filters.text & ~Filters.command, annotation_book_selected)],
        ENTER_PAGE_AND_NOTE: [MessageHandler(
            Filters.text & ~Filters.command, annotation_entered_page_and_note)]
    },
    fallbacks=[CommandHandler('start', command_start)]
)
dispatcher.add_handler(annotate_handler)

# Define new states for ConversationHandler
SELECT_BOOKMARK, DELETE_BOOKMARK, SELECT_ANNOTATION, DELETE_ANNOTATION = range(
    10, 14)


def view_bookmarks(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    bookmarks = cursor.execute(
        'SELECT title, page FROM bookmarks WHERE user_id = ?', (user_id,)).fetchall()

    if bookmarks:
        bookmarks_list = [
            f"{title} - Page {page}" for title, page in bookmarks]
        keyboard = [[bookmark] for bookmark in bookmarks_list]
        keyboard.append(["Cancel"])
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Select a bookmark to delete or 'Cancel' to exit:", reply_markup=reply_markup)
        return SELECT_BOOKMARK
    else:
        update.message.reply_text("You have no bookmarks.")
        return ConversationHandler.END


def delete_bookmark(update: Update, context: CallbackContext):
    if update.message.text == "Cancel":
        update.message.reply_text("Action canceled.")
        return ConversationHandler.END

    user_id = update.effective_user.id
    title, _, page_str = update.message.text.partition(" - Page ")
    page = int(page_str)
    cursor.execute(
        'DELETE FROM bookmarks WHERE user_id = ? AND title = ? AND page = ?', (user_id, title, page))
    conn.commit()
    update.message.reply_text(f"Bookmark for {title} on page {page} deleted.")
    return ConversationHandler.END


def view_annotations(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    annotations = cursor.execute(
        'SELECT title, page, note FROM annotations WHERE user_id = ?', (user_id,)).fetchall()

    if annotations:
        annotations_list = [
            f"{title} - Page {page}: {note}" for title, page, note in annotations]
        keyboard = [[annotation] for annotation in annotations_list]
        keyboard.append(["Cancel"])
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Select an annotation to delete or 'Cancel' to exit:", reply_markup=reply_markup)
        return SELECT_ANNOTATION
    else:
        update.message.reply_text("You have no annotations.")
        return ConversationHandler.END


def delete_annotation(update: Update, context: CallbackContext):
    if update.message.text == "Cancel":
        update.message.reply_text("Action canceled.")
        return ConversationHandler.END

    user_id = update.effective_user.id
    title, _, rest = update.message.text.partition(" - Page ")
    page_str, _, note = rest.partition(": ")
    page = int(page_str)
    cursor.execute('DELETE FROM annotations WHERE user_id = ? AND title = ? AND page = ? AND note = ?',
                   (user_id, title, page, note))
    conn.commit()
    update.message.reply_text(
        f"Annotation for {title} on page {page} deleted.")
    return ConversationHandler.END

# ---- Handlers and Dispatcher ----


bookmarks_handler = ConversationHandler(
    entry_points=[CommandHandler('viewbookmarks', view_bookmarks)],
    states={
        SELECT_BOOKMARK: [MessageHandler(
            Filters.text & ~Filters.command, delete_bookmark)]
    },
    fallbacks=[CommandHandler('start', command_start)]
)
dispatcher.add_handler(bookmarks_handler)

annotations_handler = ConversationHandler(
    entry_points=[CommandHandler('viewannotations', view_annotations)],
    states={
        SELECT_ANNOTATION: [MessageHandler(
            Filters.text & ~Filters.command, delete_annotation)]
    },
    fallbacks=[CommandHandler('start', command_start)]
)
dispatcher.add_handler(annotations_handler)

# ---- Polling ----
updater.start_polling()
