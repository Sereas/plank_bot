import datetime
from datetime import timedelta
import pandas as pd


min_plank_time = 135

users_db_path = '~/plank_bot/users_db.h5'
logs_db_path = '~/plank_bot/logs_db.h5'

# users_db_path = 'D:/Python projects/PlankBot/users_db.h5'
# logs_db_path = 'D:/Python projects/PlankBot/logs_db.h5'


class User:
    def __init__(self, user_id, chat_id, name=None):
        self.name = name
        self.user_id = user_id
        self.chat_id = chat_id
        self.current_time = min_plank_time
        self.time_increase = 15
        self.increase_in_days = 14
        self.increase_day = datetime.datetime.today().date() + timedelta(days=14)
        self.times_missed = 0
        self.planked_today = False
        self.vacation = False

    def load(self):
        users = pd.read_hdf(users_db_path, key='df')
        print(users)
        user_line = users.loc[(users['user_id'] == self.user_id) & (users['chat_id'] == self.chat_id)]
        if user_line.shape[0] > 0:
            self.current_time = user_line['min_plank_time'].iloc[0]
            self.times_missed = user_line['times_missed'].iloc[0]
            self.name = user_line['name'].iloc[0]
            self.time_increase = user_line['time_increase'].iloc[0]
            self.increase_in_days = user_line['increase_in_days'].iloc[0]
            self.increase_day = user_line['increase_day'].iloc[0]
            self.vacation = user_line['vacation'].iloc[0]
            print('Loaded existing user')
            self.describe()
        else:
            print('No such user exists. Creating new one')
            self.write()

    def write(self):
        users_df = pd.read_hdf(users_db_path, key='df')
        '''if self.user_id not in users_df.user_id:'''
        row = pd.Series({'chat_id': self.chat_id,
                         'user_id': self.user_id,
                         'name': self.name,
                         'min_plank_time': self.current_time,
                         'time_increase': self.time_increase,
                         'increase_in_days': self.increase_in_days,
                         'increase_day': self.increase_day,
                         'times_missed': self.times_missed,
                         'vacation': self.vacation})
        users_df = users_df.append(row, ignore_index=True)
        users_df.to_hdf(users_db_path, key='df'
)

    def amend(self):
        users_df = pd.read_hdf(users_db_path, key='df')
        '''update all'''
        users_df.loc[(users_df['user_id'] == self.user_id) & (users_df['chat_id'] == self.chat_id),
                     'min_plank_time'] = self.current_time
        users_df.loc[(users_df['user_id'] == self.user_id) & (users_df['chat_id'] == self.chat_id),
                     'times_missed'] = self.times_missed
        users_df.loc[(users_df['user_id'] == self.user_id) & (users_df['chat_id'] == self.chat_id),
                     'name'] = self.name
        users_df.loc[(users_df['user_id'] == self.user_id) & (users_df['chat_id'] == self.chat_id),
                     'time_increase'] = self.time_increase
        users_df.loc[(users_df['user_id'] == self.user_id) & (users_df['chat_id'] == self.chat_id),
                     'increase_in_days'] = self.increase_in_days
        users_df.loc[(users_df['user_id'] == self.user_id) & (users_df['chat_id'] == self.chat_id),
                     'increase_day'] = self.increase_day
        users_df.loc[(users_df['user_id'] == self.user_id) & (users_df['chat_id'] == self.chat_id),
                     'vacation'] = self.vacation
        '''save'''
        users_df.to_hdf(users_db_path, key='df')

    def describe(self):
        print('Chat ID:', self.chat_id)
        print('User ID:', self.user_id)
        print('Name:', self.name)
        print('Current plank time:', self.current_time)
        print('Time increase in seconds:', self.time_increase)
        print('Increase every # of days:', self.increase_in_days)
        print('Next increase:', self.increase_day)
        print('Times missed:', self.times_missed)
        print('Vacation:', self.vacation)

    def check_if_user_exists(self):
        self.load()

    def write_planked_today(self, date):
        logs_df = pd.read_hdf(logs_db_path, key='df')
        print(logs_df)
        user_line = logs_df.loc[(logs_df['user_id'] == self.user_id) &
                                (logs_df['chat_id'] == self.chat_id) &
                                (logs_df['date'] == date)]
        if user_line.shape[0] > 0:
            print('User already planked on ' + date)
        else:
            row = pd.Series({'chat_id': self.chat_id,
                             'user_id': self.user_id,
                             'date': date})
            logs_df = logs_df.append(row, ignore_index=True)
            logs_df.to_hdf(logs_db_path, key='df')

    def check_planked_today(self, date):
        logs_df = pd.read_hdf(logs_db_path, key='df')
        user_line = logs_df.loc[(logs_df['user_id'] == self.user_id) &
                                (logs_df['chat_id'] == self.chat_id) &
                                (logs_df['date'] == date)]
        if user_line.shape[0] > 0:
            self.planked_today = True

    def get_users_dict(self, chat_id):
        print('')

    def change_increase_date(self, date=None):
        if date is None:
            self.increase_day = self.increase_day + timedelta(days=self.increase_in_days)
            self.amend()
            self.describe()
        else:
            self.increase_day = date
            self.amend()

    def change_current_time(self, time=None):
        if time is None:
            self.current_time = int(self.current_time) + int(self.time_increase)
            self.amend()
            self.describe()
        else:
            self.current_time = int(time)
            self.amend()

    def change_time_increase(self, time):
        self.time_increase = int(time)
        self.amend()

    def change_increase_in_days(self, days):
        self.increase_in_days = int(days)
        self.amend()

    def change_vacation(self, value):
        if value == 'True':
            self.vacation = True
        else:
            self.vacation = False
        self.amend()

