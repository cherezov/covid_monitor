# @file covid_bot.py

from config import *
import csv
import telebot
from telebot import types
from covid import CovidStat, all_locales, load_updater
from datetime import datetime 
from threading import Timer

bot = telebot.TeleBot(token)

def chat_id(param):
    return param if isinstance(param, int) else param.chat.id

def is_admin(message):
    if isinstance(message, int):
        return message == my_id
    return message.from_user.id == my_id

def keyboard(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)

    updateBtn = types.KeyboardButton('/update')
    graphBtn = types.KeyboardButton('/graph')
    subscribeBtn = types.KeyboardButton('/subscribe')
    unsubscribeBtn = types.KeyboardButton('/unsubscribe')

    markup.add(updateBtn, graphBtn, subscribeBtn, unsubscribeBtn)

    #if is_admin(message):
    #    markup.add(graphBtn)
    return markup

def country_keyboard(action):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    for locale, s in stat.items():
        markup.add(types.KeyboardButton('{}: {} {}'.format(action, s.flag(), locale)))
    return markup


def send(to, msg, with_keyboard = True):
    to = chat_id(to)
    if with_keyboard:
        bot.send_message(to, msg, reply_markup=keyboard(chat_id(to)))
    else:
        bot.send_message(to, msg)

def send_admin(msg):
    send(my_id, msg)

def help():
    return """
Shortcuts:
/help        - this help info
/update      - last update
/graph       - daily statistics
/subscribe   - allow sending updates automatically
/unsubscribe - unsubscribe from automatic updates

Legend:
🧪  {}
🦠  {}
👍  {}
⚰️  {}
    """.format('tested', 'positive test result (infected)', 'recovered', 'dead')

def do_update(locale):
    def val(total, new):
        return '{:,}'.format(total) if new == 0 else '{:,} (+{})'.format(total, new)

    s = stat[locale]
    s.update()
    new_data = s.review_new_data()

    return """{}{}:
🧪  {}
🦠  {}
👍  {}
⚰️  {}
    """.format(s.flag(), locale, val(s.total_tested(), new_data.tested),       \
               val(s.total_positive(), new_data.positive),   \
               val(s.total_recovered(), new_data.recovered), \
               val(s.total_dead(), new_data.dead))

def last_update(uid = None):
    if uid is not None and uid in users and len(users[uid].subscribed_to) > 0: 
        updates = [do_update(locale) for locale in users[uid].subscribed_to]
    else:
        updates = [do_update(locale) for locale in locales]
    return '\n'.join(updates)

class User:
    def __init__(self, id, username, subscribed_to):
        self.id = id
        self.username = username
        if not subscribed_to:
            self.subscribed_to = []
        else:
            self.subscribed_to = subscribed_to.lower().split(';') if isinstance(subscribed_to, str) else subscribed_to

    def subscribed(self, locale):
        return locale.lower() in self.subscribed_to

    def __repr__(self):
        username = self.username if self.username else 'Unknown'
        return ','.join([str(self.id), username, ';'.join(self.subscribed_to)])

users = {}
def load_users(from_file = USERS_DATA):
    global users
    users = {}
    with open(from_file, 'r') as f:
        csv_file = csv.DictReader(f)
        for row in csv_file:
            user = dict(row)
            users[int(user['id'])] = User(int(user['id']), user['username'], user['subscribed_to'])

def save_users(to_file = USERS_DATA):
    with open(to_file, 'w') as f:
        f.write(','.join(['id', 'username', 'subscribed_to']))
        for id, user in users.items():
            f.write('\n')
            f.write(str(user))

def checkin_user(message):
    user = message.from_user
    if user.id not in users:
        users[user.id] = User(user.id, user.username, '')
        send_admin('New user: @{} id={}'.format(user.username, user.id))
        save_users()


def send_stat(message, locale,  params, title = None):
    s = stat[locale]
    f = s.save_plot(params, title)
    with open(f, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, reply_markup=keyboard(message))

# @name --- Subscribe ----
# @{
@bot.message_handler(commands=['subscribe', 'unsubscribe', 'graph'])
def on_subscribe(message):
    uid = chat_id(message)
    markup = types.ReplyKeyboardRemove(selective=True)
    bot.send_message(uid, "Choose location to {}".format(message.text), reply_markup=country_keyboard(message.text))

@bot.message_handler(regexp='/subscribe.+')
def on_location_subscribe(message):
    uid = chat_id(message) 
    'monitor <flag> <locale>'
    locale = message.text.split()
    if len(locale) == 3:
        locale = locale[2]
    else:
        print('[error] on_location_subscribe("{}") by uid={}'.format(message.text, uid))
        return

    if uid not in users:
        checkin_user(uid)
    if locale not in users[uid].subscribed_to:
        users[uid].subscribed_to.append(locale)
        save_users()
    bot.send_message(uid, 'Subscribed to {}'.format(locale), reply_markup=keyboard(uid))

@bot.message_handler(regexp='/unsubscribe.+')
def on_location_unsubscribe(message):
    uid = chat_id(message) 
    'unsubscribe <flag> <locale>'
    locale = message.text.split()
    if len(locale) == 3:
        locale = locale[2]
    else:
        print('[error] on_location_unsubscribe("{}") by uid={}'.format(message.text, uid))
        return

    if uid not in users:
        checkin_user(uid)
    if locale in users[uid].subscribed_to:
        users[uid].subscribed_to.remove(locale)
        save_users()
        bot.send_message(uid, 'Unsubscribed from {}'.format(locale), reply_markup=keyboard(uid))
    else:
        bot.send_message(uid, 'Not subscribed to {}'.format(locale), reply_markup=keyboard(uid))
# @}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    uid = chat_id(message)
    checkin_user(message)

    msg = """
This is a bot to check official COVID-19 stat in {}
{}
Last updates:
{}
    """.format(', '.join(['{}{}'.format(s.flag(), locale) for locale, s in stat.items()]), help(), last_update())
    send(message, msg)

@bot.message_handler(regexp='/graph.+')
def on_graph(message):
    uid = chat_id(message) 
    'unsubscribe <flag> <locale>'
    locale = message.text.split()
    if len(locale) == 3:
        locale = locale[2]
    else:
        print('[error] on_graph("{}") by uid={}'.format(message.text, uid))
        return

    send_stat(message, locale, ['tested', 'positive'])
    send_stat(message, locale, ['percent', 'average:percent'], 'positive / tested, %')
    send_stat(message, locale, ['recovered', 'dead'])

@bot.message_handler(commands=['update'])
def on_update(message):
    uid = chat_id(message)
    send(message, last_update(uid))

@bot.message_handler(commands=['reload'])
def on_reload(message):
    if not is_admin(message):
        return
    for locale, s in stat.items():
        s.load()
    load_users()
    send(message, "Reloaded")

@bot.message_handler(func=lambda m: True)
def default(message):
    send(message, help())

def notify_all(locale, msg):
    for id, user in users.items():
        if not user.subscribed(locale):
            continue
        send(user.id, msg)

def on_timer():
    for locale, s in stat.items():
        msg = do_update(locale)
        try:
            new_data = s.review_new_data()
            if not new_data.is_empty():
                notify_all(locale, msg)

                now = datetime.now()
                if now.hour < 11 and now.minute < 15: 
                    new_data.yesterday()
                s.add_new_data(new_data)
                s.save()
        except Exception as e:
            print(e)

    timer = Timer(PingTimeout, on_timer)
    timer.start()

if __name__ == '__main__':
    import sys

    stat = {}
    locales = all_locales()
    for locale in locales:
        updater = load_updater(locale)

        stat[locale] = CovidStat(updater)
        stat[locale].load()

    load_users()

    on_timer()
    bot.polling()
