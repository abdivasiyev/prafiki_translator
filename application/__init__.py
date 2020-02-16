from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import telebot
from telebot import types

from application.globals import TOKEN, URL, start_info, commands
from application.translator import translate
import datetime


server = Flask(__name__)
bot = telebot.TeleBot(token=TOKEN)

server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_bot.db'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(server)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, unique=True)
    username = db.Column(db.String(32))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    last_lang = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime)


@bot.message_handler(commands=['start'])
def command_start(message):
    oldUser = User.query.filter_by(chat_id=message.chat.id).first()
    new_message = start_info()
    if not oldUser:
        user = User()
        user.chat_id = message.chat.id
        if message.from_user.username is not None:
            user.username = message.from_user.username
        user.first_name = message.from_user.first_name
        if message.from_user.last_name is not None:
            user.last_name = message.from_user.last_name
        user.last_lang = '/uzen'
        db.session.add(user)
        db.session.commit()
    else:
        new_message = f"Yana ko'rishib turganimdan xursandman {oldUser.first_name}.\n" + new_message
    bot.send_chat_action(chat_id=message.chat.id, action='typing')
    bot.send_message(chat_id=message.chat.id, text=new_message)


@bot.message_handler(commands=['about'])
def command_about(message):
    bot.send_chat_action(chat_id=message.chat.id, action='upload_photo')
    bot.send_photo(chat_id=message.chat.id,
                   photo='https://tuit.uz/static/post/b/k/5a31155968143.jpeg',
                   caption='Toshkent axborot texnologiyalari universiteti.\nDasturchi: [Abdivasiyev Asliddin](https://t.me/s1_33_py_pr06r4_44_44_3r)\nGuruh: 317-18',
                   parse_mode='markdown')


@bot.message_handler(commands=list(commands.keys()))
def translate_command(message):
    oldUser = User.query.filter_by(chat_id=message.chat.id).first()
    if not oldUser:
        user = User()
        user.chat_id = message.chat.id
        if message.from_user.username is not None:
            user.username = message.from_user.username
        user.first_name = message.from_user.first_name
        if message.from_user.last_name is not None:
            user.last_name = message.from_user.last_name
        user.last_lang = message.text
        db.session.add(user)
        db.session.commit()
    else:
        oldUser.last_lang = message.text
        db.session.commit()

    msg = bot.reply_to(message=message, text="Iltimos, tarjima qilinishi kerak bo'lgan matningizni kiriting!")
    bot.register_next_step_handler(message=msg, callback=translate_text, lang=message.text)


def translate_text(message, lang):
    lang = lang[1:]
    lang1 = lang[:2]
    lang2 = lang[2:]
    translated = translate(message.text, lang1, lang2)
    if translated is not None:
        bot.send_chat_action(chat_id=message.chat.id, action='typing')
        bot.reply_to(message=message, text=translated)
    else:
        bot.send_chat_action(chat_id=message.chat.id, action='typing')
        bot.reply_to(message=message, text=f'Sizning matningizni tarjima qilishning iloji bo\'lmadi.')


@bot.message_handler(func=lambda message: True)
def translate_by_old_command(message):
    oldUser = User.query.filter_by(chat_id=message.chat.id).first()
    if not oldUser:
        bot.send_chat_action(chat_id=message.chat.id, action='typing')
        bot.send_message(chat_id=message.chat.id, text='Iltimos avval /start buyrug\'idan foydalaning.')
        return

    translate_text(message=message, lang=oldUser.last_lang)


@bot.inline_handler(lambda query: len(query.query) != 0)
def inline_query_translator(inline_query):
    try:
        # Query view: uz: Salom
        # r = types.InlineQueryResultArticle('1', 'Result1', types.InputTextMessageContent('hi'))
        # r2 = types.InlineQueryResultArticle('2', 'Result2', types.InputTextMessageContent('hi'))
        # bot.answer_inline_query(inline_query.id, [r, r2])
        query = inline_query.query.split(':', 1)
        lang = query[0].strip().lower()
        text = query[1].strip()
        r1 = types.InlineQueryResultArticle('1', 'Xatolik',
                                            types.InputTextMessageContent('Tarjima qilishning iloji bo\'lmadi.'))
        r2 = types.InlineQueryResultArticle('2', 'Xatolik',
                                            types.InputTextMessageContent('Tarjima qilishning iloji bo\'lmadi.'))
        if lang == 'uz':
            ru_text = translate(text, lang, 'ru')
            if ru_text is not None:
                r1 = types.InlineQueryResultArticle('1', 'Rus tilida', types.InputTextMessageContent(ru_text))
            en_text = translate(text, lang, 'en')
            if en_text is not None:
                r2 = types.InlineQueryResultArticle('2', 'Ingliz tilida', types.InputTextMessageContent(en_text))
        elif lang == 'ru':
            uz_text = translate(text, lang, 'uz')
            if uz_text is not None:
                r1 = types.InlineQueryResultArticle('1', 'O\'zbek tilida', types.InputTextMessageContent(uz_text))
            en_text = translate(text, lang, 'en')
            if en_text is not None:
                r2 = types.InlineQueryResultArticle('2', 'Ingliz tilida', types.InputTextMessageContent(en_text))
        elif lang == 'en':
            uz_text = translate(text, lang, 'uz')
            if uz_text is not None:
                r1 = types.InlineQueryResultArticle('1', 'O\'zbek tilida', types.InputTextMessageContent(uz_text))
            ru_text = translate(text, lang, 'ru')
            if ru_text is not None:
                r2 = types.InlineQueryResultArticle('2', 'Rus tilida', types.InputTextMessageContent(ru_text))

        bot.answer_inline_query(inline_query.id, [r1, r2])
    except Exception as e:
        print("Xatolik:", str(e))


@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode('utf-8'))])
    return 'Ok', 200


@server.route('/')
def set_web_hook():
    bot.remove_webhook()
    bot.set_webhook(url=URL + TOKEN)
