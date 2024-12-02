import random
import sqlalchemy
from sqlalchemy import insert
from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
from sqlalchemy.orm import sessionmaker
from data.models import Users, User_translation, Words, Translations
from dotenv import load_dotenv
import os


DSN = "postgresql://postgres:Mb20041995@localhost:5432/Tg_Bot_translation"
engine = sqlalchemy.create_engine(DSN)
Session = sessionmaker(bind=engine)
session = Session()

print('Бот запущен')

load_dotenv()
state_storage = StateMemoryStorage()
token_bot = os.getenv('TOKEN')
bot = TeleBot(token_bot, state_storage=state_storage) #независимое хранилище в памяти

@bot.message_handler(commands= ['start'])
def echo_all(message):  # Добавление id пользователя в базу
    user_id = message.from_user.id
    print(f"Пользователь с ID: {user_id} отправил сообщение: {message.text}")
    try:
        user = session.query(Users).filter_by(telegram_id=str(user_id)).first()
        if not user:
            stmt = insert(Users).values(telegram_id=str(user_id))
            session.execute(stmt)
            session.commit()
            print(f"Пользователь с ID: {user_id} добавлен в базу данных.")
        else:
            print(f"Пользователь с ID: {user_id} уже существует.")
    except Exception as e:
        session.rollback()
        print(f"Ошибка добавления пользователя в базу данных: {e}")
    finally:
        session.close()
    bot.send_message(message.chat.id, f"Введи команду /Go чтоб начать")

buttons = []

# Функция для получения случайного слова и его переводов
def get_random_word_and_translations():
    word_entry = session.query(Words).order_by(sqlalchemy.func.random()).first()
    translations = session.query(Translations).filter_by(word_id=word_entry.id).all()

    # Разделяем переводы на основной и неправильные
    correct_translation = [t.translation for t in translations if t.is_primary][0]
    incorrect_translations = [t.translation for t in translations if not t.is_primary]

    # Возвращаем словосочетание из верного и нескольких случайных неправильных
    chosen_incorrect = random.sample(incorrect_translations, 3)
    return word_entry.word, correct_translation, chosen_incorrect

class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'

class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()

class AddWordStates(StatesGroup):
    entering_word = State()
    entering_translations = State()

class DeleteWordStates(StatesGroup):
    delete_word = State()

def show_hint(*lines):
    return '\n'.join(lines)

def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"

@bot.message_handler(commands=['Go'])
def create_cards(message):
    cid = message.chat.id
    user_id = message.from_user.id

    # Проверяем, существует ли пользователь в базе данных
    user = session.query(Users).filter_by(telegram_id=str(user_id)).first()
    if user:
        bot.send_message(cid, "Привет. Давай начнём учить английский")
    else:
        bot.send_message(cid, "Ошибка: вы не зарегистрированы. Пожалуйста, используйте /start для регистрации.")
        return

    global buttons
    target_word, correct_translation, incorrect_translations = get_random_word_and_translations()
    all_options = [correct_translation] + incorrect_translations
    random.shuffle(all_options)
    markup = types.ReplyKeyboardMarkup(row_width=2)
    buttons = [types.KeyboardButton(option) for option in all_options]

    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    greeting = f"Выбери перевод слова:\n🇷🇺 {target_word}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = correct_translation
        data['translate_word'] = target_word
        data['other_words'] = incorrect_translations
def get_user_step(uid):
    user = session.query(Users).filter_by(telegram_id=str(uid)).first()
    if user:
        return user.user_step
    else:
        return 0  # Если пользователь не найден, возвращаем 0

@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)

@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def start_delete_word(message):
    bot.send_message(message.chat.id, "Введите слово для удаления:")
    bot.set_state(message.from_user.id, DeleteWordStates.delete_word, message.chat.id)

@bot.message_handler(state=DeleteWordStates.delete_word)
def delete_word_translation(message):
    word_to_delete = message.text

    # Проверяем, есть ли такое слово в базе данных
    word_entry = session.query(Words).filter_by(word=word_to_delete).first()

    if not word_entry:
        bot.send_message(message.chat.id, f"Слово '{word_to_delete}' нет в вашем списке.")
    else:
        # Удаляем переводы, связанные с этим словом
        session.query(Translations).filter_by(word_id=word_entry.id).delete()
        # Удаляем само слово
        session.delete(word_entry)
        session.commit()
        bot.send_message(message.chat.id, f"Слово '{word_to_delete}' и его переводы успешно удалены.")
    bot.delete_state(message.from_user.id, message.chat.id)

@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    bot.send_message(message.chat.id, "Введите новое русское слово:")
    bot.set_state(message.from_user.id, AddWordStates.entering_word, message.chat.id)
    print(message.text)  # сохранить в БД

@bot.message_handler(state=AddWordStates.entering_word)
def entering_word(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['new_word'] = message.text
    bot.send_message(message.chat.id, "Введите четыре варианта перевода (первый должен быть правильным), разделенных запятыми. Пример: 'hello,great,car,house'")
    bot.set_state(message.from_user.id, AddWordStates.entering_translations, message.chat.id)

@bot.message_handler(state=AddWordStates.entering_translations)
def entering_translations(message):
    translations = message.text.split(',')
    if len(translations) != 4:
        bot.send_message(message.chat.id, "Пожалуйста, введите ровно четыре варианта перевода.")
        return

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        new_word = data['new_word']
        primary_translation = translations[0]  # Первый вариант будет считаться правильным

        # Создайте новое слово и переводы в базе данных
        new_word_entry = Words(word=new_word)
        session.add(new_word_entry)
        session.commit()

        translation_entries = [
            Translations(word_id=new_word_entry.id, translation=translations[i], is_primary=(i == 0))
            for i in range(len(translations))
        ]
        session.add_all(translation_entries)
        session.commit()

        bot.send_message(message.chat.id, f"Слово '{new_word}' и его переводы успешно добавлены.")

    bot.delete_state(message.from_user.id, message.chat.id)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']

        if text == target_word:
            hint = show_target(data)
            hint_text = ["Отлично!❤", hint]
            next_btn = types.KeyboardButton(Command.NEXT)
            buttons.extend([next_btn])
            hint = show_hint(*hint_text)
        else:
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            hint = show_hint("Допущена ошибка!",
                             f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}")

    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)
    # Обновляем шаг пользователя в базе данных
    user = session.query(Users).filter_by(telegram_id=str(message.from_user.id)).first()
    if user:
        user.user_step += 1
        session.commit()
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling(skip_pending=True)