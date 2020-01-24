import os
import re
import logging
import json
import tweepy
import time
import datetime
from dateutil import relativedelta
from pathlib import Path
from configparser import ConfigParser


class TwitterBot:

    def __init__(self):

        # load bot configuration
        self.config = self.load_configuration()
        self.auth_config = self.config['auth']
        
        # load reminders
        with open(Path('reminders.json')) as fp:
            self.reminders = json.load(fp)

        # authentication
        self.auth = tweepy.OAuthHandler(self.auth_config['key'], self.auth_config['secret_key'])
        self.auth.set_access_token(self.auth_config['token'], self.auth_config['secret_token'])
        self.api = tweepy.API(self.auth)

        logging.warning('API loaded.')

        self.last_id = None # VAI QUEBRAR

        # bot actions
        while True:
            self.actions()
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

    def get_mentions(self):
        logging.info('Getting mentions.')
        self.mentions = self.api.mentions_timeline(since_id=self.last_id)

    def set_reminder(self):
        for m in range(len(self.mentions)):
            if not self.mentions[m].retweeted:
                
                try:
                    logging.info(f'Replying to mention from @{self.mentions[m].user.screen_name}.')
                    date = self.interpret_mentions(self.mentions[m].text, self.mentions[m].created_at)
                    text = f'Claro @{self.mentions[m].user.screen_name}! Lembrarei a você desse tweet no dia ' + self.date_to_str(date) + '.'
                    self.api.update_status(text, in_reply_to_status_id=self.mentions[m].id)
                    self.reminders[self.mentions[m].id] = [self.mentions[m].user.screen_name, date]
                except:
                    self.last_id = self.mentions[m].id
                    logging.warning(f'Set Reminder exception raised.')
                    logging.warning(f'This is the last_id: {self.last_id}, from {self.mentions[m].user.screen_name}.')
                    break

    def date_to_str(self, date):
        return datetime.datetime.strftime(date, "%d/%m/%Y às %H:%M")

    def interpret_mentions(self, text, date):

        expressions = {'minutes': r'(\d+)\s+mi\w+', 
                       'hours': r'(\d+)\s+ho\w+',
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
                                                hours=int(*delta['days'])-3, # quick fix for GMT -3 
                                                minutes=int(*delta['minutes']))
            return date

    def reminder(self):
        for status_id, v in self.reminders.items():
            if datetime.datetime.now() >= v[1]:
                    try:
                        text = f'Oi, @{v[0]}! Aqui está o seu lembrete!'
                        self.api.update_status(text, in_reply_to_status_id=status_id)
                    except:
                        logging.warning(f'Reminder exception raised.')
                        break

    def get_cancel_requests(self):
        pass

    def upload_reminders(self):
        pass        

    def actions(self):
        """Sequence of actions taken by the robot"""
        self.get_mentions()
        self.set_reminder()
        self.reminder()

if __name__ == '__main__':
    TwitterBot()