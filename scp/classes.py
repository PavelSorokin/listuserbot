from telebot.handler_backends import State, StatesGroup

class create_list(StatesGroup):
    name = State()

class delete_list(StatesGroup):
    name = State()

class close_list(StatesGroup):
    name = State()

class write_user_list(StatesGroup):
    name = State()
    fio = State()

class read_list(StatesGroup):
    name = State()

class intdeadline(StatesGroup):
    deadline = State()

class answer(StatesGroup):
    answer1 = State()
    answer2 = State()
    answer3 = State()

class timeout(StatesGroup):
    timeout = State()