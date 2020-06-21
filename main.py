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

# users_db_path = 'D:/Python projects/PlankBot/users_db.h5'
# logs_db_path = 'D:/Python projects/PlankBot/logs_db.h5'

print('Bot started')
global user_to_change


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
            print('Checker', check_user.vacation is False)
            if check_user.vacation is False:
                check_user.check_planked_today((datetime.datetime.today().date() - timedelta(days=1)).strftime("%d %b %Y"))
                message = message + str(check_user.name) + ' - ' + str(check_user.planked_today) + ' \n '

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
    schedule.every().day.at("02:00").do(send_daily_stats)
    schedule.every().day.at("08:08").do(check_increase_date)
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
    '''markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Everybody', 'Me', 'Other user')
    msg = bot.reply_to(message, 'Who do you want set up time for?', reply_markup=markup)'''
    msg = bot.reply_to(message, 'Feeling brave today?) Ok, Please specify new time in seconds please.')
    bot.register_next_step_handler(msg, set_up_time_step)


@bot.message_handler(commands=['my_stats'])
def start_message(message):
    user = User(user_id=message.from_user.id, chat_id=message.chat.id, name=message.from_user.first_name)
    user.check_if_user_exists()
    bot.send_message(message.chat.id, 'Your current statistics: \n'
                                      'Name: ' + str(user.name) + ' \n'
                                      'Current minimum planking time: ' + str(user.current_time) + ' seconds. \n'
                                      'Time increase: ' + str(user.time_increase) + ' seconds \n'
                                      'Increase in days: ' + str(user.increase_in_days) + ' days \n'
                                      'Next increase on: ' + str(user.increase_day) + '\n'
                                      'Vacation: ' + str(user.vacation))


@bot.message_handler(commands=['set_increase_time'])
def start_message(message):
    msg = bot.reply_to(message, 'This is the amount in seconds your time will increase on next increase date. '
                                'Choose wisely')
    bot.register_next_step_handler(msg, set_up_time_increase_step)


@bot.message_handler(commands=['set_increase_periods'])
def start_message(message):
    msg = bot.reply_to(message, 'This is the amount in days until your next next increase day. '
                                'Does not change nearest increase day))')
    bot.register_next_step_handler(msg, set_up_increase_periods_step)


@bot.message_handler(commands=['vacation_mode'])
def start_message(message):
    users = load_chat_users(chat_id=message.chat.id)
    print(users)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for user in users:
        markup.add(user)
    msg = bot.reply_to(message, 'Ok, who is going on vacation??', reply_markup=markup)
    bot.register_next_step_handler(msg, set_up_vacation_step)


@bot.message_handler(commands=['planked_with'])
def start_message(message):
    users = load_chat_users(chat_id=message.chat.id)
    print(users)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for user in users:
        markup.add(user)
    msg = bot.reply_to(message, 'Planking together is always more fun ;) Who did you plank with?', reply_markup=markup)
    bot.register_next_step_handler(msg, set_up_planked_with_step)


def set_up_planked_with_step(message):
    users = load_chat_users(chat_id=message.chat.id)
    user_to_change_plank = User(user_id=users[message.text], chat_id=message.chat.id)
    user_to_change_plank.check_if_user_exists()
    user_to_check = User(user_id=message.from_user.id, chat_id=message.chat.id)
    user_to_check.check_if_user_exists()

    if int(datetime.datetime.fromtimestamp(message.date).strftime("%H")) > 2:
        user_to_check.check_planked_today(datetime.datetime.fromtimestamp(message.date).strftime("%d %b %Y"))
        if user_to_check.planked_today is True:
            user_to_change_plank.check_planked_today(datetime.datetime.fromtimestamp(message.date).strftime("%d %b %Y"))
            if user_to_change_plank.planked_today is False:
                bot.send_message(message.chat.id,
                                'Great! Hope you and ' + str(user_to_change_plank.name) + ' had a wonderful time!')
                user_to_change_plank.write_planked_today(datetime.datetime.fromtimestamp(message.date).strftime("%d %b %Y"))
            else:
                bot.send_message(message.chat.id, 'I see that this user already planked today. '
                                'Did you get drunk together and you forgot that you have already tagged your friend?)')
        else:
            bot.send_message(message.chat.id,
                             'Hmmm... It looks like you have not planked yourself today.. Do not believe you.')
    else:
        user_to_check.check_planked_today(
            (datetime.datetime.fromtimestamp(message.date) - timedelta(days=1)).strftime("%d %b %Y"))
        if user_to_check.planked_today is True:
            user_to_change_plank.check_planked_today(
            (datetime.datetime.fromtimestamp(message.date) - timedelta(days=1)).strftime("%d %b %Y"))
            if user_to_change_plank.planked_today is False:
                bot.send_message(message.chat.id,
                                'Great! Hope you and ' + str(user_to_change_plank.name) + ' had a wonderful time!')
                user_to_change_plank.write_planked_today(
                    (datetime.datetime.fromtimestamp(message.date) - timedelta(days=1)).strftime("%d %b %Y"))
            else:
                bot.send_message(message.chat.id, 'I see that this user already planked today. '
                                'Did you get drunk together and you forgot that you have already tagged your friend?)')
        else:
            bot.send_message(message.chat.id,
                             'Hmmm... It looks like you have not planked yourself today.. Do not believe you.')


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
    try:
        var = int(message.text)

        if isinstance(var, int):
            user = User(user_id=message.from_user.id, chat_id=message.chat.id, name=message.from_user.first_name)
            user.check_if_user_exists()
            old_time = user.current_time
            user.change_current_time(time=message.text)
            bot.send_message(message.chat.id,
                             'Done. Your old time was ' + str(old_time) + ' seconds . Your new time is ' +
                             str(user.current_time) + ' seconds')

    except ValueError:
        bot.send_message(message.chat.id, 'You idiot, it is not an integer! Try again, moron')


def set_up_time_increase_step(message):
    try:
        var = int(message.text)

        if isinstance(var, int):
            user = User(user_id=message.from_user.id, chat_id=message.chat.id, name=message.from_user.first_name)
            user.check_if_user_exists()
            old_time = user.time_increase
            user.change_time_increase(time=message.text)
            bot.send_message(message.chat.id,
                             'Done. Your old increase time was ' + str(old_time) + ' seconds . Your new increase time is ' +
                             str(user.time_increase) + ' seconds')

    except ValueError:
        bot.send_message(message.chat.id, 'You idiot, it is not an integer! Try again, moron')


def set_up_increase_periods_step(message):
    try:
        var = int(message.text)

        if isinstance(var, int):
            user = User(user_id=message.from_user.id, chat_id=message.chat.id, name=message.from_user.first_name)
            user.check_if_user_exists()
            old_time = user.increase_in_days
            user.change_increase_in_days(days=message.text)
            bot.send_message(message.chat.id,
                             'Done. Your old increase in days was ' + str(old_time) + ' days. Your new increase in days is ' +
                             str(user.increase_in_days) + ' days')

    except ValueError:
        bot.send_message(message.chat.id, 'You idiot, it is not an integer! Try again, moron')


def set_up_vacation_step(message):
    global user_to_change
    user_to_change = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('True', 'False')
    bot.send_message(message.chat.id, 'Ok, will amend vacation status for ' + str(user_to_change) + '.')
    msg = bot.reply_to(message,  'Which status is it?', reply_markup=markup)
    bot.register_next_step_handler(msg, set_up_vacation_step2)


def set_up_vacation_step2(message):
    global user_to_change
    users = load_chat_users(chat_id=message.chat.id)
    user = User(user_id=users[user_to_change], chat_id=message.chat.id)
    user.check_if_user_exists()
    user.change_vacation(value=message.text)
    bot.send_message(message.chat.id, 'Done')
    user_to_change = ""


def load_chat_users(chat_id):
    users_df = pd.read_hdf(users_db_path, key='df')
    chat_df = users_df.loc[users_df['chat_id'] == chat_id]
    users_dict = {}
    for user in chat_df['user_id']:
        user_line = chat_df.loc[chat_df['user_id'] == user]
        users_dict[user_line['name'].iloc[0]] = user
    return users_dict


@bot.message_handler(content_types=['video'])
def handle_docs_video(message):
    user = User(user_id=message.from_user.id, chat_id=message.chat.id, name=message.from_user.first_name)
    user.check_if_user_exists()
    print('Server time ', datetime.datetime.today())

    if int(datetime.datetime.fromtimestamp(message.date).strftime("%H")) > 2:
        user.check_planked_today(datetime.datetime.fromtimestamp(message.date).strftime("%d %b %Y"))
    else:
        user.check_planked_today((datetime.datetime.fromtimestamp(message.date) - timedelta(days=1)).strftime("%d %b %Y"))

    if user.planked_today is False:
        if int(datetime.datetime.fromtimestamp(message.date).strftime("%H")) > 2:
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



