import config as var
import telebot
import os
from telebot import custom_filters
from datetime import datetime
from art import tprint
from scp import msg_handler, keyboard, classes
import logging
from logging.handlers import RotatingFileHandler

def main():
    log = logging.getLogger("bots.doc")
    log.setLevel(logging.INFO)
    handler = RotatingFileHandler('./log/main.log', maxBytes=10000, backupCount=10)
    log_format = f"%(asctime)s | [%(levelname)s] | %(name)s | (%(filename)s).%(funcName)s(%(lineno)d) | %(message)s"
    handler.setFormatter(logging.Formatter(log_format))
    log.addHandler(handler)
    print("is started!")

    bot = telebot.TeleBot(var.main_bot_token, state_storage=var.state_storage)

    def safes_state(bot, message, state):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data[state] = message.text

    @bot.message_handler(commands=['help'])
    def help_cmd(message):
        bot.send_message(message.chat.id, 'Отправь /start' , reply_markup=keyboard.keyboard_remove())

    @bot.message_handler(commands=['start'])
    def start_cmd(message):
        if message.chat.id in var.admins:
            bot.send_message(message.chat.id, 'Выбери что мне сделать', reply_markup=keyboard.keyboard_admin())
        else:
            bot.send_message(message.chat.id, 'Выбери что мне сделать', reply_markup=keyboard.keyboard_user())

    @bot.message_handler(state="*", commands=['cancel'])
    def cancel_cmd(message):
        bot.send_message(message.chat.id, 'Перезапуск', reply_markup=keyboard.keyboard_remove())
        bot.delete_state(message.from_user.id, message.chat.id) 

    @bot.message_handler(state=classes.create_list.name)
    def admin_create_list(message):
        safes_state(bot, message, 'name')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            name = data['name']
        with open('./lists/'+ name +'.txt', 'w') as files:
            files.close
        bot.send_message(message.chat.id, 'Спиок создан:'+ name, reply_markup=keyboard.keyboard_admin())
        bot.delete_state(message.from_user.id, message.chat.id)

    @bot.message_handler(state=classes.close_list.name)
    def admin_close_list(message):
        safes_state(bot, message, 'name')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            doc = data['name']
            docs = open('./lists/'+doc, 'rb')
        bot.send_document(message.chat.id, docs)
        bot.send_message(message.chat.id, 'Отправляю список '+doc, reply_markup=keyboard.keyboard_admin())
        bot.delete_state(message.from_user.id, message.chat.id)
        os.rename('./lists/'+doc, './lists/close_'+doc)

    @bot.message_handler(state=classes.delete_list.name)
    def admin_delete_list(message):
        safes_state(bot, message, 'name')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            name = data['name']
            os.remove('./lists/'+ name)
        bot.send_message(message.chat.id, 'Список '+name+ ' удален' , reply_markup=keyboard.keyboard_admin())
        bot.delete_state(message.from_user.id, message.chat.id)

    @bot.message_handler(state=classes.write_user_list.name)
    def user_write_list(message):
        safes_state(bot, message, 'name')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            name = data['name']
            lists = os.listdir('./lists')
        if name+'.txt' in lists:
                bot.send_message(message.chat.id, 'Напиши нам свое ФИО. Мы внесем тебя в список и привоим номер', reply_markup=keyboard.keyboard_remove())
                bot.set_state(message.from_user.id, classes.write_user_list.fio, message.chat.id)
        else:
                bot.send_message(message.chat.id, 'Такого списка нет. Поробуй заново, выбери с помощью всплывающей команды', reply_markup=keyboard.keyboard_user())
                bot.delete_state(message.from_user.id, message.chat.id)
    
    @bot.message_handler(state=classes.write_user_list.fio)
    def user_write_lists(message):
        safes_state(bot, message, 'fio')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            name = data['name']
            fio = data['fio']
        with open('./lists/'+name+'.txt','r+') as files:
            my_list = [x.rstrip() for x in files]
            number = len(my_list) + 1
            files.write(str(number)+'. '+ fio+'\n')
            files.close
        bot.send_message(message.chat.id, 'Твой номер в списке: №'+str(number)+'\nПокажи его при входе' , reply_markup=keyboard.keyboard_remove())
        bot.delete_state(message.from_user.id, message.chat.id)

    @bot.message_handler(state="*", func=lambda message: message.chat.id in var.admins, content_types=['text'])
    def admin_msg(message):
        if message.text == 'Создать список':

                bot.send_message(message.chat.id, 'Как назвать список?', reply_markup=keyboard.keyboard_remove())
                bot.set_state(message.from_user.id, classes.create_list.name, message.chat.id)

        elif message.text == 'Закрыть список':
                bot.send_message(message.chat.id, 'Какой список закрыть?', reply_markup=keyboard.keyboard_delete())
                bot.set_state(message.from_user.id, classes.close_list.name, message.chat.id)

        elif message.text == 'Удалить список':
                bot.send_message(message.chat.id, 'Какой список удалить?', reply_markup=keyboard.keyboard_delete())
                bot.set_state(message.from_user.id, classes.delete_list.name, message.chat.id)

        elif message.text == 'Показать списки':
                files = os.listdir('./lists')
                msg = 'Списки:\n'
                msg1 = ''
                for i in files:  
                    msg1 = msg1 + i + '\n'
                bot.send_message(message.chat.id, msg+msg1, reply_markup=keyboard.keyboard_admin())
        else:
            start_cmd(message)

    @bot.message_handler(state="*", func=lambda message: message.chat.type == 'private', content_types=['text'])
    def user_msg(message):
        if message.text == 'Записаться':
                bot.send_message(message.chat.id, 'В какой список вас записать?', reply_markup=keyboard.keyboard_write())
                bot.set_state(message.from_user.id, classes.write_user_list.name, message.chat.id)
        else:
            start_cmd(message)

    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.add_custom_filter(custom_filters.IsDigitFilter())

    bot.infinity_polling(skip_pending=True)

if __name__ == '__main__':
    main()