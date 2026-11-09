import telebot as t
from telebot import types
from datetime import date
from datetime import timedelta
import datetime
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

tok = os.getenv("TOK")


conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"  
    "DATABASE=ForTg1;"
    "Trusted_Connection=yes;"       
    "TrustServerCertificate=yes;"
)


bot = t.TeleBot(tok)

connection = pyodbc.connect(conn_str)
cursor = connection.cursor()


@bot.message_handler(commands=["start"])
def firstmessage(message):
    bot.send_message(message.chat.id, f'Yo')


def CheckDateForLogic(DateToday, DateForHw):
    if str(DateToday) < str(DateForHw):
        return 1
    else:
        return 0


def SqlCommands(DateYesterday, Date):
    cursor.execute(f"delete from Homeworks where DateOfExpire < '{DateYesterday}';")
    cursor.commit()
    cursor.execute(f"select * from homeworks where DateOfExpire = '{Date}';")
    return cursor.fetchall()


@bot.message_handler(commands=['choose'])  # выбор
def ChoseTheme(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("/dobavkatext")
    item2 = types.KeyboardButton("/vivod")
    item3 = types.KeyboardButton("/vivodbydate")
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)


@bot.message_handler(commands=['dobavkatext'])  # вводное для ввода дз текстового
def HomeworkAdd(message):
    bot.send_message(message.chat.id, 'Введи дз и дату в формате:'
            ' дата, предмет, дз; 2025-11-31, РЯ, dz'
    ' в дз не должно быть никаких знаков в дате тоже кроме точек; после , 1 пробел')
    bot.register_next_step_handler(message, HomeworkAdd2)


@bot.message_handler(commands=['vivod']) # вывод дз на завтра
def ShowHw(message):
    Date = str(datetime.date.today() + datetime.timedelta(days=1))
    DateYesterday = str(datetime.date.today() - datetime.timedelta(days=1))
    try:
        rows = SqlCommands(DateYesterday, Date)
        if rows:
            for row in rows:
                bot.send_message(message.chat.id, f"Предмет: {row[1]}; Само дз: {row[4]}")
        else:
            bot.send_message(message.chat.id, "Нет дз на завтра!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


@bot.message_handler(commands=['vivodbydate'])
def ShowHwByDate(message):
    bot.send_message(message.chat.id, "Введи дз на дату в формате: 2026-10-19")
    bot.register_next_step_handler(message, ShowHwByDate2)


@bot.message_handler(content_types=['text'])
def InputError(message):
    bot.send_message(message.chat.id, "Возможно ты ошибся с командой, попробуй еще раз")


@bot.message_handler(content_types=['text'])
def ShowHwByDate2(message1):
    Date = message1.text
    DateYesterday = DateYesterday = str(datetime.date.today() - datetime.timedelta(days=1))
    try:
        rows = SqlCommands(DateYesterday, Date)
        if rows:
            for row in rows:
                bot.send_message(message1.chat.id, f"Предмет: {row[1]};"
                f" Дата на которую задано дз: {row[3]}; Само дз: {row[4]}")
        else:
            bot.send_message(message1.chat.id, "Нет дз на эту дату!")
    except Exception as e:
        bot.send_message(message1.chat.id, f"Ошибка: {e}")


@bot.message_handler(content_types=['text'])
def HomeworkAdd2(message1):
    mes = message1.text
    try:
        DateToday = datetime.date.today()
        NewDate = mes[:mes.find(",")]
        NewSubject = mes[mes.find(",") + 2:mes.rfind(",")]
        NewHW = mes[mes.rfind(",") + 2:]
        Username = message1.from_user.username
        UserId = message1.from_user.id
        if CheckDateForLogic(DateToday, NewDate) == 1:
            cursor.execute(
            "insert into Homeworks(Subject, RecordingDate, DateOfExpire, Homework, Username, UserTgId)"
            " values (?, ?, ?, ?, ?, ?)", (NewSubject, DateToday, NewDate, NewHW, Username, UserId)
            )
            connection.commit()
            bot.send_message(message1.chat.id, "Дз добавленно ( ͠° ͟ʖ ͡°)")
        else:
            bot.send_message(message1.chat.id, "Сообщение не принято, дата неверная")
    except Exception as e:
        bot.send_message(message1.chat.id, "Вероятно, неверный формат данных, попробуй еще раз")


bot.polling(none_stop=True)