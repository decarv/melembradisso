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
        
        # authentication
        self.auth_config = config['auth']
        self.auth()


        self.action()

    def load_configuration(self):
        config = ConfigParser()
        config_p = Path('../config.ini')
        try:
            config.read(config_p)
            return config
        except FileNotFoundError:
            logging.warning('File config.ini not found.')
            configuration.create_config_file()
        except KeyError:
            logging.warning(f'File config.ini does not contain configuration for {__class__.__name__}.')
            configuration.append_config_file()

    def auth(self):
        
        self.auth = tweepy.OAuthHandler(self.auth_config['key'], self.auth_config['secret_key'])
        self.auth.set_access_token(self.auth_config['token'], self.auth_config['secret_token'])

    def load_data(self):
        """In case it is shut down, loads all the data for the reminders."""
        pass

    def check_reminder(self):
        pass

    def check_mention(self):
        """For every minute, check for mentions."""
        pass

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