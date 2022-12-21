import config as var
import deadline as lines
import telebot
import os
import importlib
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
    def empty_dir():       
        lists = os.listdir('./lists')
        if len(lists) == 0:
            return True
        else:
            return False
    def check_deadline(name):
        with open('./lists/'+name+'.txt','r+') as files:
            my_list = [x.rstrip() for x in files]
            number = len(my_list)
        return number

    @bot.message_handler(commands=['help'])
    def help_cmd(message):
        bot.send_message(message.chat.id, 'Привет, для работы с ботом отправь /start' , reply_markup=keyboard.keyboard_remove())

    @bot.message_handler(commands=['start'])
    def start_cmd(message):
        if message.chat.id in var.admins:
            bot.send_message(message.chat.id, 'Привет! Выбери, что мне сделать со списками на мероприятие:\nПоказать - Выводит сообщение о всех списках\nСоздать - Создает на сервере список, в который можно начинать вписывать людей\nЗакрыть - Отправляет готовый список,и переименовывает его с префиксом "close_"(чтобы ни кто его не видел, кроме тебя)\nУдалить - удалет навсегда список с сервера', reply_markup=keyboard.keyboard_admin())
            bot.delete_state(message.from_user.id, message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Привет! Ты хочешь записаться на мероприятие?\nСледуй командам ниже 😉 ', reply_markup=keyboard.keyboard_user())
            bot.delete_state(message.from_user.id, message.chat.id)

    @bot.message_handler(state="*", commands=['cancel'])
    def cancel_cmd(message):
        bot.send_message(message.chat.id, 'Удаляем состояния, если все еще не работает отправь мне /start', reply_markup=keyboard.keyboard_remove())
        bot.delete_state(message.from_user.id, message.chat.id) 

    @bot.message_handler(state="*", func=lambda message: message.text == "Назад")
    def back_to_start(message):
        start_cmd(message)
    
    @bot.message_handler(state=classes.intdeadline.deadline, is_digit=False)
    def noint(message):
        bot.send_message(message.chat.id,'Введи только число, без пробелов и символов', parse_mode='Markdown', reply_markup=keyboard.keyboard_back())
        bot.set_state(message.from_user.id, classes.intdeadline.deadline, message.chat.id) 

    @bot.message_handler(state=classes.intdeadline.deadline, is_digit=True)
    def yesint(message):  
        safes_state(bot, message, 'deadline')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                nd = data['deadline']   
                file = open('./deadline.py', 'r+')
                file.truncate(0)
                new_deadline = 'deadline = '+nd
                file.write(new_deadline)
                file.close()
        importlib.reload(lines)        
        msg_nd = 'Установлено новое количество проходок: '+str(lines.deadline)
        bot.send_message(message.chat.id, msg_nd, reply_markup=keyboard.keyboard_admin())
        bot.delete_state(message.from_user.id, message.chat.id)

    @bot.message_handler(state=classes.create_list.name)
    def admin_create_list(message):
        safes_state(bot, message, 'name')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            name = data['name']
        with open('./lists/'+ name +'.txt', 'w') as files:
            files.close
        bot.send_message(message.chat.id, 'Спиcок создан: '+ name, reply_markup=keyboard.keyboard_admin())
        bot.delete_state(message.from_user.id, message.chat.id)

    @bot.message_handler(state=classes.read_list.name)
    def admin_read_list(message):
        if empty_dir() == False:
            safes_state(bot, message, 'name')
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                doc = data['name']
                docs = open('./lists/'+doc, 'rb')
            if os.path.getsize('./lists/'+doc) == 0:
                bot.send_message(message.chat.id, 'Извини, файл пустой. Его можно только удалить.🤷‍♂️\nПопробуй заново, выбери с помощью всплывающей команды.\nНажни => /start', reply_markup=keyboard.keyboard_admin())
                bot.delete_state(message.from_user.id, message.chat.id)
            else:
                bot.send_document(message.chat.id, docs)
                bot.send_message(message.chat.id, 'Отправляю список: '+doc, reply_markup=keyboard.keyboard_admin())
                bot.delete_state(message.from_user.id, message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Извини, я не нашел список.🤷‍♂️\nПопробуй заново, выбери с помощью всплывающей команды.\nНажни => /start', reply_markup=keyboard.keyboard_admin())
            bot.delete_state(message.from_user.id, message.chat.id)

    @bot.message_handler(state=classes.close_list.name)
    def admin_close_list(message):
        if empty_dir() == False:
            safes_state(bot, message, 'name')
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                doc = data['name']
                docs = open('./lists/'+doc, 'rb')
            if os.path.getsize('./lists/'+doc) == 0:
                bot.send_message(message.chat.id, 'Извини, файл пустой. Его можно только удалить.🤷‍♂️\nПопробуй заново, выбери с помощью всплывающей команды.\nНажни => /start', reply_markup=keyboard.keyboard_admin())
                bot.delete_state(message.from_user.id, message.chat.id)
            else:
                bot.send_document(message.chat.id, docs)
                bot.send_message(message.chat.id, 'Отправляю список: '+doc, reply_markup=keyboard.keyboard_admin())
                bot.delete_state(message.from_user.id, message.chat.id)
                if doc.startswith('close') == False:    
                    os.rename('./lists/'+doc, './lists/close_'+doc)
        else:
            bot.send_message(message.chat.id, 'Извини, я не нашел список.🤷‍♂️\nПопробуй заново, выбери с помощью всплывающей команды.\nНажни => /start', reply_markup=keyboard.keyboard_admin())
            bot.delete_state(message.from_user.id, message.chat.id)

    @bot.message_handler(state=classes.delete_list.name)
    def admin_delete_list(message):
        if empty_dir() == False:
            safes_state(bot, message, 'name')
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                name = data['name']
                os.remove('./lists/'+ name)
            bot.send_message(message.chat.id, 'Список '+name+ ' удален' , reply_markup=keyboard.keyboard_admin())
            bot.delete_state(message.from_user.id, message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Извини, я не нашел список.🤷‍♂️\nПопробуй заново, выбери с помощью всплывающей команды.\nНажни => /start', reply_markup=keyboard.keyboard_admin())
            bot.delete_state(message.from_user.id, message.chat.id)
    @bot.message_handler(state=classes.answer.answer1)
    def __answer1(message):
        safes_state(bot, message, 'answer1')
        bot.send_message(message.chat.id, str(f'Вопрос 2:\n{var.question2}'), reply_markup=keyboard.keyboard_question2())
        bot.set_state(message.from_user.id, classes.answer.answer2, message.chat.id)

    @bot.message_handler(state=classes.answer.answer2)
    def __answer2(message):
        safes_state(bot, message, 'answer2')
        bot.send_message(message.chat.id, str(f'Вопрос 3:\n{var.question3}'), reply_markup=keyboard.keyboard_question3())
        bot.set_state(message.from_user.id, classes.answer.answer3, message.chat.id)

    @bot.message_handler(state=classes.answer.answer3)
    def __answer3(message):
        safes_state(bot, message, 'answer3')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            answer1 = data['answer1']
            answer2 = data['answer2']
            answer3 = data['answer3']
        print(answer1,answer2,answer3)
        if answer1 == '2' and answer2 == '1' and answer3 == 'Суббота':
                bot.delete_state(message.from_user.id, message.chat.id)
                bot.send_message(message.chat.id, 'Отлично! Тест пройден\nПожалуйста, выбери список по кнопке ниже⬇️', reply_markup=keyboard.keyboard_write())
                bot.set_state(message.from_user.id, classes.write_user_list.name, message.chat.id)
        else: 
            bot.delete_state(message.from_user.id, message.chat.id)
            bot.send_message(message.chat.id, 'Все плохо, ты завалил Тест 😱\nНо у тебя есть возможность попробовать снова! Вперед 💪', reply_markup=keyboard.keyboard_user())


    @bot.message_handler(state=classes.write_user_list.name)
    def user_write_list(message):
        # safes_state(bot, message, 'name')
        # if  bot.get_chat_member(var.zerkalo_chat_id,message.from_user.id).status == 'left':
        #         bot.send_message(message.chat.id, 'Для записи в список на вход, необходимо быть подписанным на канал\nhttps://t.me/zerkalotver 🤷‍♂️\nПопробуй заново, выбери с помощью всплывающей команды.\nНажни => /start', reply_markup=keyboard.keyboard_user())
        #         bot.delete_state(message.from_user.id, message.chat.id)
        
        # else:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                name = data['name']
                lists = os.listdir('./lists')
            if name+'.txt' in lists:
                if check_deadline(name) < lines.deadline:
                        bot.send_message(message.chat.id, 'Ты выбрал список: '+name+ '\nОтправь свою Фамилию и Имя, чтобы мы закрепили за тобой Номер\nЗапомни, его необходимо будет предъявить на входе🧐', reply_markup=keyboard.keyboard_remove())
                        bot.set_state(message.from_user.id, classes.write_user_list.fio, message.chat.id)
                else:
                        bot.send_message(message.chat.id, 'Извини, но количество проходок закончилось.🤷‍♂️\nНажни => /start', reply_markup=keyboard.keyboard_user())
                        bot.delete_state(message.from_user.id, message.chat.id)
                        bot.send_message(var.stas, 'Количество проходок закончилось, закрой список \nНажни => /start')
            else:
                    bot.send_message(message.chat.id, 'Извини, я не нашел список.🤷‍♂️\nПопробуй заново, выбери с помощью всплывающей команды.\nНажни => /start', reply_markup=keyboard.keyboard_user())
                    bot.delete_state(message.from_user.id, message.chat.id)
    
    @bot.message_handler(state=classes.write_user_list.fio)
    def user_write_lists(message):
        safes_state(bot, message, 'fio')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            name = data['name']
            fio = data['fio']
        with open('./lists/'+name+'.txt','r+') as files:
            fio = fio.replace('\n', ' ')
            my_list = [x.rstrip() for x in files]
            number = len(my_list) + 1
            files.write(str(number)+'. '+ fio+'\n')
            files.close
        bot.send_message(message.chat.id, 'Твой номер в списке: №'+str(number)+'\nПокажи его при входе' , reply_markup=keyboard.keyboard_remove())
        bot.delete_state(message.from_user.id, message.chat.id)

    @bot.message_handler(state="*", func=lambda message: message.chat.id in var.admins, content_types=['text'])
    def admin_msg(message):
        if message.text == 'Создать':

                bot.send_message(message.chat.id, 'Как назвать список?', reply_markup=keyboard.keyboard_back())
                bot.set_state(message.from_user.id, classes.create_list.name, message.chat.id)

        elif message.text == 'Закрыть':

            if  empty_dir() == False:

                    bot.send_message(message.chat.id, 'Какой список закрыть?', reply_markup=keyboard.keyboard_delete())
                    bot.set_state(message.from_user.id, classes.close_list.name, message.chat.id)

            else:
                    bot.send_message(message.chat.id, 'Извини, я ничего не нашел. Попробуй сначала создать🤷‍♂️\nНажни => /start', reply_markup=keyboard.keyboard_admin())
                    bot.delete_state(message.from_user.id, message.chat.id)
        
        elif message.text == 'Просмотреть':

            if  empty_dir() == False:

                    bot.send_message(message.chat.id, 'Какой список ты хочешь посмотреть?', reply_markup=keyboard.keyboard_delete())
                    bot.set_state(message.from_user.id, classes.read_list.name, message.chat.id)

            else:
                    bot.send_message(message.chat.id, 'Извини, я ничего не нашел. Попробуй сначала создать🤷‍♂️\nНажни => /start', reply_markup=keyboard.keyboard_admin())
                    bot.delete_state(message.from_user.id, message.chat.id)
        elif message.text == 'Удалить':

            if  empty_dir() == False:

                    bot.send_message(message.chat.id, 'Какой список удалить?', reply_markup=keyboard.keyboard_delete())
                    bot.set_state(message.from_user.id, classes.delete_list.name, message.chat.id)

            else:
                    bot.send_message(message.chat.id, 'Извини, я ничего не нашел. Попробуй сначала создать🤷‍♂️\nНажни => /start', reply_markup=keyboard.keyboard_admin())
                    bot.delete_state(message.from_user.id, message.chat.id)

        elif message.text == 'Кол-во проходок':
            msg_deadline = 'Количество проходок на списки: '+ str(lines.deadline) +'\nОтправь мне новое ЧИСЛО, чтобы изменить количество проходок на ВСЕ списки'
            bot.send_message(message.chat.id, msg_deadline, reply_markup=keyboard.keyboard_back())
            bot.set_state(message.from_user.id, classes.intdeadline.deadline, message.chat.id)
     

        elif message.text == 'Показать':
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
        if message.text == '🥳Записаться на мероприятие':
                if empty_dir() == False:
                    bot.send_message(message.chat.id, 'Вижу что хочешь записать на мероприятие.\nНо для начала пройди тест⬇️')
                    bot.send_message(message.chat.id, str(f'Вопрос 1:\n{var.question1}'), reply_markup=keyboard.keyboard_question1())
                    bot.set_state(message.from_user.id, classes.answer.answer1, message.chat.id)
                # if empty_dir() == False:
                #         bot.send_message(message.chat.id, 'Пожалуйста, выбери список по кнопке ниже⬇️', reply_markup=keyboard.keyboard_write())
                #         bot.set_state(message.from_user.id, classes.write_user_list.name, message.chat.id)
                else:
                        bot.send_message(message.chat.id, 'Извини, но сейчас нет открытых списков для записи 🤷‍♂️\nНажни => /start', reply_markup=keyboard.keyboard_user())
                        bot.delete_state(message.from_user.id, message.chat.id)
        else:
            start_cmd(message)

    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.add_custom_filter(custom_filters.IsDigitFilter())

    bot.infinity_polling(skip_pending=True)

if __name__ == '__main__':
    main()