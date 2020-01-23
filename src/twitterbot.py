import os
import json
import tweepy
import time
import datetime as dt
from configparser import ConfigParser

class TwitterBot:

    def __init__(self):

        config = self.load_configuration()
        self.bot_sleep = config['bot_sleep']
        self.auth(config['consumer_key'], config['consumer_secret'], 
                  config['access_token'], config['access_secret'])


        self.action()

    def auth(self, consumer_key, consumer_secret, access_token, access_secret):
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_secret)

    def load_configuration(self):
        config = ConfigParser()
        try:
            config.read('config.ini')
            return config[__class__.__name__]
        except FileNotFoundError:
            logging.warning('File config.ini not found.')
            configuration.create_config_file()
        except KeyError:
            logging.warning(f'File config.ini does not contain configuration for {__class__.__name__}.')
            configuration.append_config_file()

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