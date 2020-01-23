# import os
import json
import tweepy
import time
import datetime as dt
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
            mentions = self.api.mentions_timeline(last_id=int(file.read())) # this can cause trouble if file.read() is empty    
            file.write(mentions[0].id_str)
            mentions_ids = [mentions[m].id for m in range(len(mentions))]

        return mentions_ids

    def set_reminder(self):
        """If there is a mention, create a reminder."""
        pass

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
        self.mentions = self.check_mentions()
        self.set_reminder()
        self.reminders = self.check_reminders()
        self.reminder()