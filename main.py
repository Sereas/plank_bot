import telebot
from telebot import types
import datetime
from datetime import timedelta
import pandas as pd
import schedule
from threading import Thread
from time import sleep
from classes import User

bot = telebot.TeleBot('1088985217:AAHXJF3KofCRj1rkgpRURce8pYl4Ow1Zlu8')

'''# proxy
login = 'olegdylevich'
pwd = 'W1o7SqQ'
ip = '89.191.230.201'
port = '65233'


telebot.apihelper.proxy = {
  'https': 'https://{}:{}@{}:{}'.format(login, pwd, ip, port)
}'''

users_db_path = '~/plank_bot/users_db.h5'
logs_db_path = '~/plank_bot/logs_db.h5'

print('Bot started')


def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)


def send_daily_stats():
    users_df = pd.read_hdf(users_db_path, key='df')
    for chat in users_df['chat_id'].drop_duplicates():
        message = 'Daily check list as of ' + \
                  str((datetime.datetime.today().date() - timedelta(days=1)).strftime("%d %b %Y")) + ': \n '
        for user in users_df.loc[users_df['chat_id'] == chat]['user_id']:
            check_user = User(user_id=user, chat_id=chat)
            check_user.check_if_user_exists()
            check_user.check_planked_today((datetime.datetime.today().date() - timedelta(days=1)).strftime("%d %b %Y"))
            message = message + str(check_user.name) + ' - ' + str(check_user.planked_today) +\
                      ' ' + str(datetime.datetime.today().date().strftime("%d %b %Y")) + ' \n '

        bot.send_message(chat, message)


def check_increase_date():
    users_df = pd.read_hdf(users_db_path, key='df')
    for chat in users_df['chat_id'].drop_duplicates():
        message = ''
        for user in users_df.loc[users_df['chat_id'] == chat]['user_id']:
            check_user = User(user_id=user, chat_id=chat)
            check_user.check_if_user_exists()
            if check_user.increase_day == datetime.datetime.today().date():
                check_user.change_increase_date()
                check_user.change_current_time()
                message = message + check_user.name +\
                        ' , congrats! Today is your increase day! Your new time is ' +\
                        str(int(check_user.current_time)) + ' seconds! Your next' \
                        ' increase date is ' +\
                        str(check_user.increase_day.strftime("%d %b %Y"))
                if message != '':
                    bot.send_message(chat, message)


if __name__ == "__main__":
    schedule.every().day.at("05:00").do(send_daily_stats)
    schedule.every().day.at("13:15").do(check_increase_date)
    Thread(target=schedule_checker).start()


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Hi, plankers! I am very happy to greet you all here! I was created to help you'
                                      ' track your progress. Right now I am a bit retarded and can not do much, but'
                                      ' hopefully soon I will be able to remind you about mandatory time increases and'
                                      ' track who planked each day and who missed, and other stuff like that. Please'
                                      ' do not hesitate to write your suggestions to my creator. May the force to plank'
                                      ' be always with you!')


@bot.message_handler(commands=['set_min_plank_time'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Everybody', 'Me', 'Other user')
    msg = bot.reply_to(message, 'Who do you want set up time for?', reply_markup=markup)
    bot.register_next_step_handler(msg, find_users_to_set_up_time_to_step)


def find_users_to_set_up_time_to_step(message):
    if message.text == 'Everybody':
        bot.send_message(message.chat.id, 'Ok, will set new time for everybody.')
        reply_time = bot.reply_to(message, 'Please specify new time (in seconds) for ' + message.text + ':')
    elif message.text == 'Me':
        bot.send_message(message.chat.id, 'No problem mate, will adjust only your time.')
    else:
        get_user = bot.send_message(message.chat.id, 'Who is the poor fella you want to torture?')
        bot.register_next_step_handler(get_user, set_up_time_step)


def set_up_time_step(message):
    print('you are in step 2')
    for entity in message.entities:
        print(entity)


@bot.message_handler(content_types=['video'])
def handle_docs_video(message):
    user = User(user_id=message.from_user.id, chat_id=message.chat.id, name=message.from_user.first_name)
    user.check_if_user_exists()

    if int(datetime.datetime.fromtimestamp(message.date).strftime("%H")) > 5:
        user.check_planked_today(datetime.datetime.fromtimestamp(message.date).strftime("%d %b %Y"))
    else:
        user.check_planked_today((datetime.datetime.fromtimestamp(message.date) - timedelta(days=1)).strftime("%d %b %Y"))

    if user.planked_today is False:
        if int(datetime.datetime.fromtimestamp(message.date).strftime("%H")) > 5:

            if message.video.duration >= user.current_time:
                bot.send_message(message.chat.id, 'Hooray! ' + message.from_user.first_name + ' planked on, '
                             + str(datetime.datetime.fromtimestamp(message.date).strftime("%d %b %Y"))+'! Good job =)')
                user.write_planked_today(datetime.datetime.fromtimestamp(message.date).strftime("%d %b %Y"))
            else:
                bot.send_message(message.chat.id,
                                 'Dear ' + message.from_user.first_name + ', your current minimum planking time is '
                                 + str(user.current_time) + ' seconds. Your video is ' + str(message.video.duration) +
                                 ' seconds, which is less.')
        else:

            if message.video.duration >= user.current_time:
                bot.send_message(message.chat.id, 'Hooray! ' + message.from_user.first_name + ' planked on, '
                    + str((datetime.datetime.fromtimestamp(message.date) - timedelta(days=1)).strftime("%d %b %Y")) +
                                 '! Good job =)')
                user.write_planked_today((datetime.datetime.fromtimestamp(message.date) - timedelta(days=1)).strftime("%d %b %Y"))
            else:
                bot.send_message(message.chat.id,
                                 'Dear ' + message.from_user.first_name + ', your current minimum planking time is '
                                 + str(user.current_time) + ' seconds. Your video is ' + str(message.video.duration) +
                                 ' seconds, which is less.')
    else:
        bot.send_message(message.chat.id,
                         'Bro, you already planked today! You can stop)')


bot.polling()



