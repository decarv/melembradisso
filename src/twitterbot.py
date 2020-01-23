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


        self.action()

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

    def load_data(self):
        """In case it is shut down, loads all the data for the reminders."""
        pass

    def check_reminder(self):
        pass

    def get_mentions(self):

        with open(Path('./last_id.txt'), 'w') as file:
            self.mentions = self.api.mentions_timeline(last_id=int(file.read())) # this can cause trouble if file.read() is empty
            file.write(mentions[0].id_str)

    def set_reminder(self):
        self.reminders = {}
        for m in len(self.mentions):
            date = interpret_mentions(self.mentions[m].text, self.mentions[m].created_at)
            reminders[self.mentions[m].id_str] = date
            reply(self.mentions[m], date)


    def reply(self, mention, date):

        text = 'Claro! Lembrarei você desse tweet no dia ' + dt.datetime.strftime(date, "%d/%m/%Y às %H:%M") '.'
        self.api.update_status(text, in_reply_to_status_id=mention.id)
        

    def interpret_mentions(self, text, date):

        expressions = {'minutes': r'(\d+)\s+mi\w+', 
                       'days': r'(\d+)\s+di\w+', 
                       'months': r'(\d+)\s+me\w+',
                       'years': r'(\d+)\s+an\w+',
                       'date': r'(\d+)/(\d+)/(\d+)'}

        delta = {}

        for k in expressions.keys():
            delta[k] = re.compile(expressions[k]).findall('10 meses')

        if delta['date']:
            delta = delta['date']
            date = datetime.datetime(*map(lambda x: int(x), delta[0][::-1]))
        else:
            date += relativedelta.relativedelta(years=int(*delta['years']),
                                                months=int(*delta['months']),
                                                days=int(*delta['days']),
                                                minutes=int(*delta['minutes']))
        return date

    def reminder(self):
        pass

    def cancel_reminder(self):
        pass

    def save_reminder(self):
        pass

    def upload_data(self):
        pass
    
    def load_bot(self):
        while True:
            time.sleep(self.bot_sleep)
            self.action()

    def action(self):
        """Set of actions taken by the robot"""
        self.get_mentions()
        self.set_reminder()
        self.reminders = self.check_reminders()
        self.reminder()