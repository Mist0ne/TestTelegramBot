# Разумеется, возможностей у бота гораздо больше.
# Модерить чат, выдавать промо-коды, новые стикеры, обмениваться контактами и локациями и т.д.
# В рамках тестового кейса это не реализовано, но потенциально возможно в течение короткого времени

import work_with_DB
import config
import hashlib
import random
import telebot
from telebot import types

bot = telebot.TeleBot(token=config.token)

# Custom Keyboards
RegisterMarkup = types.ReplyKeyboardMarkup()
RegisterMarkup.row('Зарегистрироваться')

hide = types.ReplyKeyboardRemove()

MainMarkup = types.ReplyKeyboardMarkup()
MainMarkup.row('Скинуть картиночку', 'Обработать картиночку')
MainMarkup.row('Скинуть песню', 'Послушать голосовое', 'Сделать рассылку')
MainMarkup.row('Сыграть', 'Добавить вопрос')

# BotHandlers

# Registration functions
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Отлично! Давай начнем\n"
                                      "Нажми на кнопку 'Зарегистрироваться' для регистрации в боте",
                                       reply_markup=RegisterMarkup)
    bot.register_next_step_handler(message, register)


def register(message):
    if message.text == 'Зарегистрироваться' or message.text == 'зарегистрироваться':
        bot.send_message(message.chat.id, "Молодец!\n"
                                          "Теперь введи свой уникальный логин",
                                          reply_markup=hide)
        bot.register_next_step_handler(message, login)
    else:
        bot.send_message(message.chat.id, "Извини, но я тебя не понимаю(( Попробуй еще раз")
        bot.register_next_step_handler(message, register)


def login(message):
    try:
        all_users = work_with_DB.select("SELECT Login FROM users")
        flag = False
        for i in all_users:
            if i[0] == message.text:
                flag = True
                break
        if not flag:
            bot.send_message(message.chat.id, "Супер! Теперь придумай пароль!")
            bot.register_next_step_handler(message, password, message.text)
        else:
            bot.send_message(message.chat.id, "Извини, но этот логин уже занят(( Попробуй еще раз")
            bot.register_next_step_handler(message, login)
    except:
        print("Troubles with DB in func 'login'")


# Save password in DB as hash
def password(message, login):
    if len(message.text) > 4:
        try:
            pwd = message.text
            salt = hashlib.md5(pwd.encode())
            work_with_DB.register(login, salt.hexdigest(), message.chat.id)
            bot.send_message(message.chat.id, "Готово! Теперь ты можешь пользоваться ботом", reply_markup=MainMarkup)
        except:
            print("Trouble with DB if func 'password'")
    else:
        bot.send_message(message.chat.id, "Слишком короткий пароль(( Попробуй еще")
        bot.register_next_step_handler(message, password, login)


# Возможности бота:
# ToDo Сделать проверку авторизации
@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id, "Вот, что я умею:\n"
                                      "/img - скинуть картиночку\n"
                                      "/filter_img - обработаю твою картиночку\n"
                                      "/music - скину песню\n"
                                      "/voice - прослушаю твое голосовое\n"
                                      "/quiz - сыграем с тобой в викторину\n"
                                      "/add_quiz - добавит мини-quiz\n"
                                      "/send_all - сделаю рассылку всем авторизованным пользователям")


@bot.message_handler(commands=["img", "filter_img", "music", "voice", "quiz", "add_quiz", "send_all"])
def Distributor(message):
    mes = message.text[1:]
    if mes == 'img':
        send_img(message)
    elif mes == 'filter_img':
        filter_img(message)
    elif mes == 'music':
        music(message)
    elif mes == 'voice':
        voice(message)
    elif mes == 'send_all':
        send_all(message)
    elif mes == 'quiz':
        quiz(message)
    elif mes == 'add_quiz':
        add_quiz(message)


def send_img(message):
    bot.send_photo(message.chat.id, 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Papirus-64-apps-icq.svg/1200px-Papirus-64-apps-icq.svg.png')


def filter_img(message):
    bot.send_message(message.chat.id, 'Отправь ссылку на фотографию для обработки')
    bot.register_next_step_handler(message, filter_img_request)


def filter_img_request(message):
    bot.send_message(message.chat.id, 'if I am allowed to use API, I will send you a filtered photo')
    try:
        bot.send_photo(message.chat.id, message.text)
    except:
        print('message.text != photo_url')


def music(message):
    bot.send_audio(message.chat.id, 'http://d.zaix.ru/ic9z.mp3')


def voice(message):
    bot.send_message(message.chat.id, 'Скинь голосовое сообщение')
    bot.register_next_step_handler(message, voice_request)


def voice_request(message):
    bot.send_message(message.chat.id, 'Я тебя услышал')


def send_all(message):
    try:
        all_users = work_with_DB.select("SELECT TelegramID FROM users")
        users_send = []
        for i in all_users:
            if i[0] not in users_send:
                bot.send_message(i[0], 'Рассылка')
                users_send.append(i[0])
    except:
        print('Mailing errors')


def quiz(message):
    try:
        all_quiz = work_with_DB.select("SELECT * FROM quiz")
        rand = random.randint(0, len(all_quiz) -1)
        bot.send_message(message.chat.id, 'Вот твой вопрос:\n"'
                         + all_quiz[rand][0] +
                         '"\nТеперь жду ответ')
        bot.register_next_step_handler(message, answer_quiz, all_quiz[rand][0])
    except:
        print('Troubles in quiz')


def answer_quiz(message, question):
    try:
        answer = work_with_DB.select("SELECT Answer FROM `quiz` WHERE `Question` = {}".format("'" + str(question) + "'"))
        if message.text == answer[0]:
            bot.send_message(message.chat.id, 'Congratulations')
        else:
            bot.send_message(message.chat.id, 'Попробуй еще раз')
            bot.register_next_step_handler(message, answer_quiz)
    except:
        print('Trouble in answer_quiz')


def add_quiz(message):
    bot.send_message(message.chat.id, 'Введи вопрос')
    bot.register_next_step_handler(message, set_question)


def set_question(message):
    question = message.text
    bot.send_message(message.chat.id, 'Отлчино, теперь ответ')
    bot.register_next_step_handler(message, set_answer, question)


def set_answer(message, question):
    try:
        work_with_DB.new_quiz(question, message.text)
        bot.send_message(message.chat.id, 'Успех!')
    except:
        print('Trouble in set_answer')


# Distributor
@bot.message_handler(content_types=["text"])
def distributor(message):
    mes = message.text
    if mes == 'Скинуть картиночку':
        send_img(message)
    elif mes == 'Обработать картиночку':
        filter_img(message)
    elif mes == 'Скинуть песню':
        music(message)
    elif mes == 'Послушать голосовое':
        voice(message)
    elif mes == 'Сделать рассылку':
        send_all(message)
    elif mes == 'Сыграть':
        quiz(message)
    elif mes == 'Добавить вопрос':
        add_quiz(message)


bot.polling(none_stop=True)