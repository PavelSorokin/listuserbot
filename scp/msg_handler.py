from datetime import datetime
import glob, os
from scp import keyboard
from config import timeout_seconds

def sends_doc(bot, message, doc):
    docs = open(doc, 'rb')
    bot.send_document(message.chat.id, docs)