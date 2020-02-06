import os
import re
import logging
import json
import tweepy
import time
import datetime
import psycopg2
from dateutil import relativedelta
from pathlib import Path


class TwitterBot:

    logging.basicConfig(
        level=logging.INFO, 
        format='TwitterBot - %(asctime)s - %(message)s'
        )

    def __init__(self):

        # authenticate
        logging.info('Authenticating...')
        self.auth = tweepy.OAuthHandler(
            os.getenv('KEY'), 
            os.getenv('SECRET_KEY'))
        self.auth.set_access_token(
            os.getenv('TOKEN'), 
            os.getenv('SECRET_TOKEN'))
        self.api = tweepy.API(self.auth)
        logging.info('Authentication complete!')

        # connect to the database
        # set to False when running at heroku
        self.connect_to_db()

        # get instance variable

        logging.info('Getting the latest id.')
        self.cursor.execute(
            """SELECT max(id) 
                 FROM reminders"""
                 )
        query = self.cursor.fetchone()
        self.lid = query[0]
        self.conn.commit()
        logging.info(f"The latest id is {self.lid}")
        self.mtl = None # mentions timeline

        # actions
        logging.info('Activating TwitterBot.')
        while True:
            self.get_mtl()
            self.insert_to_reminders()
            self.remind()
            logging.info(f'Sleeping for 60 seconds.')
            time.sleep(60)

    def get_mtl(self):
        logging.info('Retrieving mentions from timeline.')
        self.mtl = self.api.mentions_timeline(since_id=self.lid)
        logging.info(f'Got {len(self.mtl)} new mentions.')

    def insert_to_reminders(self):
        insert_query = """INSERT INTO reminders (id, name, created_at, reminder, done)
                      VALUES (%s, %s, %s, %s, %s)"""
    
        for status in range(len(self.mtl)):
            insert = (
                self.mtl[status].id, 
                self.mtl[status].user.screen_name, 
                self.mtl[status].created_at, 
                self.get_reminder(status=self.mtl[status]), 
                False)
            try:
                self.cursor.execute(insert_query, insert)
                self.conn.commit()
                self.lid = self.mtl[status].id
            except:
                pass

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
                hours=int(*dts['hours']),
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

    def remind(self):

        logging.info('Checking reminders.')

        now = datetime.datetime.now()

        select_query = """SELECT id, name, reminder
                          FROM reminders
                          WHERE reminder <= %s AND done = false"""
        self.conn.commit()
        try:
            logging.info('Executing select_query.')
            self.cursor.execute(select_query, (now, ))
            reminders = self.cursor.fetchall() # returns a list of reminders
            self.conn.commit()
            logging.info(f'Got this list of reminders: {reminders}. Total of {len(reminders)}.')
        except psycopg2.OperationalError:
            self.connect_to_db(function=self.remind())

        for r in reminders:
            text = f'Oi @{r[1]}! Aqui está o seu lembrete!'
            self.reply(text, status_id=r[0])
            logging.info(f'Reminded tweet: {r[0]}')
            self.update_reminder(r_id=r[0])
            logging.info(f'Cleared reminder for: {r[0]} (done set to true).')

    def update_reminder(self, r_id):
        """clear reminder: set done to True"""
        update_query = f"""UPDATE reminders
                                  SET done = True
                                WHERE id = {r_id}"""

        try:
            self.cursor.execute(update_query)
            self.conn.commit()
        except psycopg2.OperationalError:
            self.connect_to_db(function=self.update_reminder(r_id))


    def reply(self, text, status_id):
        logging.info(f'Replying to Status ID {status_id}')
        try:
            self.api.update_status(text, in_reply_to_status_id=status_id)
        except tweepy.TweepError as e:
            print(e.reason)

    def to_str(self, date):
        date -= relativedelta.relativedelta(hours=3) # comment to GMT-3
        return datetime.datetime.strftime(date, "%d/%m/%Y às %H:%M")

    def connect_to_db(self, function=None):
        logging.info('Connecting to DB...')
        self.conn = psycopg2.connect(
            os.environ['DATABASE_URL'], 
            sslmode='require')
        self.cursor = self.conn.cursor()
        logging.info('Connected to the database.') 

        if function is not None:
            function()

if __name__ == '__main__':
    TwitterBot()