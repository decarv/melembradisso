# import os
import json
import tweepy
import time
import datetime
from pathlib import Path
from configparser import ConfigParser


class TwitterBot:

    def __init__(self):

        # load bot configuration
        self.config = self.load_configuration()
        self.auth_config = config['auth']
        self.bot_config = config['TwitterBot']
        
        # authentication

        self.api = tweepy.API(self.auth())


        self.reminders = json.load(Path('reminders.json'))


        while True:
            self.action()
            time.sleep(60)

    def load_configuration(self):
        config = ConfigParser()
        try:
            config.read(Path('../config.ini'))
            return config
        except FileNotFoundError:
            logging.warning('File config.ini not found.')
            configuration.create_config_file()
        except KeyError:
            logging.warning(f'File config.ini does not contain configuration file.')
            configuration.append_config_file()

    def auth(self):
        auth = tweepy.OAuthHandler(self.auth_config['key'], self.auth_config['secret_key'])
        auth = self.auth.set_access_token(self.auth_config['token'], self.auth_config['secret_token'])
        return auth

    def get_mentions(self):
        with open(Path('./last_id.txt'), 'w') as file:
            self.mentions = self.api.mentions_timeline(last_id=int(file.read())) # FIX THIS: this can cause trouble if file.read() is empty.
            file.write(mentions[0].id_str)

    def set_reminder(self):
        for m in len(self.mentions):
            if not self.mentions[m].retweeted: # MAYBE FIXED: Returns the 20 most recent mentions, including retweets.
                date = self.interpret_mentions(self.mentions[m].text, self.mentions[m].created_at)
                self.reply(self.mentions[m], date)
                self.reminders[self.mentions[m]] = date

    def reply(self, mention, date):
        # CANCEL_REMINDER FUNCTION
        # if not date:
        #     text = 'Tudo certo! Seu lembrete foi cancelado!'
        # else:
        text = 'Claro! Lembrarei a você desse tweet no dia ' + dt.datetime.strftime(date, "%d/%m/%Y às %H:%M") + '.'
        self.api.update_status(text, in_reply_to_status_id=mention.id)

    def interpret_mentions(self, text, date):

        expressions = {'minutes': r'(\d+)\s+mi\w+', 
                       'days': r'(\d+)\s+di\w+', 
                       'months': r'(\d+)\s+me\w+',
                       'years': r'(\d+)\s+an\w+',
                       'date': r'(\d+)/(\d+)/(\d+)',
                       'cancel': r'(cancelar)'}

        delta = {}

        for k in expressions.keys():
            delta[k] = re.compile(expressions[k]).findall(text)

        if delta['cancel']:
            return None
        elif delta['date']:
            delta = delta['date']
            date = datetime.datetime(*map(lambda x: int(x), delta[0][::-1]))
            return date
        else:
            date += relativedelta.relativedelta(years=int(*delta['years']),
                                                months=int(*delta['months']),
                                                days=int(*delta['days']),
                                                minutes=int(*delta['minutes']))
            return date

    def check_reminder(self):
        for k, v in self.reminders.items():
            if datetime.datetime.now() >= self.reminders[k]:
                self.reminder(k)

    def reminder(self, k):
        text = 'Oi! Aqui está o seu lembrete!'
        self.api.update_status(text, in_reply_to_status_id=k)

    def get_cancel_requests(self):
        pass

    def upload_reminders(self):
        pass        

    def action(self):
        """Sequence of actions taken by the robot"""
        self.get_mentions()
        self.set_reminder()
        self.check_reminders()
        self.reminder()