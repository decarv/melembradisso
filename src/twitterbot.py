import os
import re
import logging
import json
import tweepy
import time
import datetime
import pickle
from dateutil import relativedelta
from pathlib import Path
from configparser import ConfigParser


class TwitterBot:

    logging.basicConfig(level=logging.INFO, format='TwitterBot - %(asctime)s - %(message)s')

    def __init__(self):
        logging.info('Loading configuration and variables.')

        # load bot configuration
        config = self.load_configuration()

        # load variables
        try:
            with open(Path('reminders.pyc'), 'rb') as fp:
                self.reminders = pickle.load(fp)
        except:
            self.reminders = {}
        try:
            with open(Path('lid.pyc'), 'rb') as fp:
                self.lid = pickle.load(fp)
        except:
            self.lid = None

        logging.info('Configuration and variables loaded.')
        
        # access API
        # MODIFY TO HANDLE POSSIBLE API ERRORS
        self.auth = tweepy.OAuthHandler(config['auth']['key'], 
                           config['auth']['secret_key'])
        self.auth.set_access_token(config['auth']['token'], 
                              config['auth']['secret_token'])
        self.api = tweepy.API(self.auth)

        # activate bot
        self.activate()

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

    def get_mtl(self):
        logging.info('Retrieving mentions_timeline.')
        self.mtl = self.api.mentions_timeline(since_id=self.lid)

    def set_reminders(self):
        logging.info('Running set_reminders.')
        for s in range(len(self.mtl)):
            if not self.mtl[s].retweeted:
                self.reminders[self.mtl[s].id_str] = {
                        'name': self.mtl[s].user.screen_name,
                        'reminder': self.get_reminder(self.mtl[s]),
                        'done': False
                }
                self.lid = self.mtl[s].id
        self.save_reminders()

    def remind(self):
        """Iterate date from text of a tweet status."""
        logging.info('RUNNING REMIND FUNCTION.')
        for k, v in self.reminders.items():
            if type(self.reminders[k].get('reminder')) is datetime.datetime: # CANNOT FIX THIS?
                if datetime.datetime.now() >= self.reminders[k].get('reminder') and self.reminders[k]['done'] == False:
                    logging.info(f'Reminder created for {k}.')
                    text = f'Oi @{self.reminders[k]["name"]}! Aqui está o seu lembrete!'
                    self.reply(text, status_id=k)
                    self.reminders[k]['done'] = True

    def reply(self, text, status_id):
        logging.info(f'Replying to Status ID {status_id}')
        try:
            self.api.update_status(text, in_reply_to_status_id=status_id)
        except tweepy.TweepError as e:
            print(e.reason)

    def get_reminder(self, status):
        """Returns date from text of a tweet status."""
        logging.info(f'Getting the reminder request for {status.id}.')
    
        expressions = {
            'years': r'(\d+)\s+an\w+',
            'months': r'(\d+)\s+me\w+',
            'days': r'(\d+)\s+di\w+',
            'hours': r'(\d+)\s+ho\w+',
            'minutes': r'(\d+)\s+mi\w+', 
            'date': r'(\d+)/(\d+)/(\d+)',
            'cancel': r'(cancel)'
            }

        dts = {}
        
        for k in expressions.keys():
            dts[k] = re.compile(expressions[k]).findall(status.text)

        if dts['cancel']:
            del self.reminders[status.id]
            text = (f'@{status.user.screen_name} Tudo certo! Seu lembrete foi cancelado.')
            self.reply(text, status_id=status.id)
        
        elif dts['date']:
            reminder = datetime.datetime(*map(lambda x: int(x), dts['date'][0][::-1]))
            reminder += relativedelta.relativedelta(
                hours=datetime.datetime.now().hour, 
                minutes=datetime.datetime.now().minute
            )
            logging.info(f'Got a date reminder for {reminder}.')
            if reminder > datetime.datetime.now():
                text = (f'@{status.user.screen_name} Claro! Lembrarei a você desse tweet no dia ' + self.to_str(reminder) + '.')
                self.reply(text, status_id=status.id)
                return reminder
            else:
                text = (f'@{status.user.screen_name} Certeza de que a data está correta?! Parece que esse lembrete já passou...')
                self.reply(text, status_id=status.id)
        
        elif dts['years'] or dts['months'] or dts['days'] or dts['hours'] or dts['minutes']:
            
            delta = relativedelta.relativedelta(
                years=int(*dts['years']), 
                months=int(*dts['months']), 
                days=int(*dts['days']),
                hours=int(*dts['days'])-3, # quick fix for GMT -3 
                minutes=int(*dts['minutes'])
            )
            reminder = status.created_at + delta
            logging.info(f'Got a dts reminder for {reminder}.')
            text = (f'@{status.user.screen_name} Claro! Lembrarei a você desse tweet no dia ' + self.to_str(reminder) + '.')
            self.reply(text, status_id=status.id)
            return reminder
        
        else:
            text = f'Me desculpe, @{status.user.screen_name}, mas a data que você escolheu nāo está clara.'
            logging.warning(f'ReminderError for id {status.id}.')
            self.reply(text, status_id=status.id)

    def to_str(self, date):
        return datetime.datetime.strftime(date, "%d/%m/%Y às %H:%M")

    def save_reminders(self):
        logging.info('Saving Reminders and Old Reminders.')
        
        with open(Path('reminders.pyc'), 'wb') as fp:
            pickle.dump(self.reminders, fp)
        with open(Path('lid.pyc'), 'wb') as fp:
            pickle.dump(self.lid, fp)

    def activate(self):
        iteration = 0
        wait = 10 # wait for 10 iterations before saving
        
        while True:
            self.get_mtl()
            self.set_reminders()
            self.remind()
            time.sleep(60)

            iteration += 1
            if iteration == wait:
                iteration = 0


if __name__ == '__main__':
    TwitterBot()