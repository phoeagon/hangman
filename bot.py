# -*- coding: utf-8 -*-
from pytg import Telegram
from pytg.utils import coroutine
import sys
from hangman import Bot
import hangman
import time
import logging
import random

logging.basicConfig()
HANGBOT = 'HangBot'
LOG_FILE = '/run/shm/hangbot.log'

def connect():
    global tg, receiver, sender
    tg = Telegram(
                #telegram="/home/phoeagon/TelegramCLI/bin/telegram-cli",
                telegram="/home/phoeagon/TelegramCLI/bin/ptg",
                    pubkey_file="/home/phoeagon/TelegramCLI/server.pub",
                    custom_cli_args=['-W'])
    receiver = tg.receiver
    sender = tg.sender


def parse(msg_text):
    life = 0
    word = ''
    for line in msg_text.splitlines():
        if line.startswith('Word:'):
            word = line.split(':')[-1].strip().replace(u'➖', '-').lower()
            word = word.encode('ascii', 'ignore')
        elif line.startswith('Lives:'):
            life = len(line.split(':')[-1].strip())
            #logging.warn(life)
            #logging.warn(word)
    return (word, life)

class Agent(object):

    def __init__(self):
        self.options = ''.join(hangman.LETTER_SET)
        self.last_choice = ''
        self.bot = Bot()
        self.flog = open(LOG_FILE, 'a')

    def append(self, text):
        for line in text.splitlines():
            if line.startswith('The word was: '):
                word = line.split(':')[-1].strip().lower()
                logging.warn(word)
                self.flog.write(word + '\n')
                self.flog.flush()
    
    def interact(self, msg):
        # print 'Agent::interact'
        text = msg.get('text', '')
        self.append(text)
        if text.startswith('There is already a game running'):
            logging.warn("/stop")
            return '/stop'
        elif text.startswith('Correct letter') or text.startswith('Incorrect letter') or text.startswith('Word:'):
            # logging.warn("/react")
            (word, life)= parse(text)
            print (word, life)
            for x in word:
                if x.isalpha():
                    self.options = self.options.replace(x, '')
            # Remove last from candidates
            self.options = self.options.replace(self.last_choice, '')
            # Ask bot
            (self.last_choice, i) = self.bot.next(word, life, self.options)
            logging.warn((self.last_choice, i))
            if i < 0.05 or life <= 1:
                return '/stop'
            return self.last_choice
        elif (text.startswith('You win!') or text.startswith('Game stopped')  or text.startswith('You lose')):
            self.last_choice = ''
            self.options = ''.join(hangman.LETTER_SET)
            return '/start'
        elif text.statswith('Your victories: '):
            return '/stop'
        else:
            logging.warn(msg)
            logging.warn("WTF")
            sys.exit(1)
        

@coroutine
def example_function(receiver):
    agent = Agent()
    msg_id_list = set()
    try:
        while True:
            msg = (yield)
            try:
                senderid = msg.get('sender', {})
                sender_cmd = senderid.get('cmd', '')
                senderid = senderid.get('username', '')
                text = msg.get('text', '')
                _id = msg.get('id', '')
                # print msg.get('sender', None), sender, HANGBOT
                if senderid == HANGBOT and _id not in msg_id_list:
                    # logging.warn(msg)
                    msg_id_list.add(_id)
                    choice = agent.interact(msg)
                    if choice[0] != '/':
                        choice = choice.upper()
                    logging.warn(choice)
                    time.sleep(random.randint(1,3))
                    sender.send_msg(sender_cmd, choice.decode('utf8'))
            except:
                logging.exception('')
                pass
    except KeyboardInterrupt:
        receiver.stop()
        logging.warn("KeyboardInterrupt received")


def main():
    try:
        connect()
        # start the Receiver, so we can get messages!
        receiver.start()

        # let "main_loop" get new message events.
        # You can supply arguments here, like main_loop(foo, bar).
        receiver.message(example_function(receiver)) # add "example_function" function as 
        # now it will call the main_loop function and yield the new messages.
        receiver.stop()
    except:
        return

def demo():
    a={'own': False, 'sender': {u'username': u'HangBot', u'first_name': u'HangBot', u'last_name': u'', u'flags': 4352, 'name': u'HangBot', 'cmd': u'user#121913006', u'type': u'user', u'id': 121913006}, u'service': False, u'text': u'Correct letter!\nWord: \u2796\u2796\u2796\u2796\u2796E\u2796\u2796\u2796\u2796\u2796\nLives: \u2764\U0001f49b\U0001f49a\U0001f499\U0001f49c\u2764\U0001f49b\U0001f49a\U0001f499\U0001f49c', 'peer': {u'username': u'HangBot', u'first_name': u'HangBot', u'last_name': u'', u'flags': 4352, 'name': u'HangBot', 'cmd': u'user#121913006', u'type': u'user', u'id': 121913006}, u'event': u'message', u'mention': True, u'flags': 273, 'receiver': {u'username': u'Phoeagon', u'first_name': u'Chit', 'name': u'Chit', 'cmd': u'user#38304327', u'phone': u'17068017280', u'last_name': u'Yau', u'flags': 264, u'type': u'user', u'id': 38304327}, u'date': 1443515837, u'reply_id': 355824, u'unread': True, u'id': 355825}
    print Agent().interact(a)

if __name__ == '__main__':
    main()
    # demo()
