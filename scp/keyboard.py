import os
from telebot import types
from telebot.types import KeyboardButton

def keyboard_remove():

    markup = types.ReplyKeyboardRemove()
    return markup

def keyboard_admin():
    rest = ['Создать список','Закрыть список','Удалить список']
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    markup.add('Показать списки')
    row = [KeyboardButton(x) for x in rest]
    markup.add(*row)
    return markup

def keyboard_user():

    rest = ['Записаться']
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
    row = [KeyboardButton(x) for x in rest]
    markup.add(*row)
    return markup

def keyboard_delete():

    rest = os.listdir('./lists')
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
    row = [KeyboardButton(x) for x in rest]
    markup.add(*row)
    return markup

def keyboard_write():
    rest = []

    lists = os.listdir('./lists')
    for i in lists:
        if (i.startswith('close')) == False:
            l = len(i)
            i = i[:l-4]
            rest.append(i)
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
    row = [KeyboardButton(x) for x in rest]
    markup.add(*row)
    return markup