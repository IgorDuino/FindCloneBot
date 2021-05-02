import datetime
import json
import random
import sqlite3

import requests
from telebot import types

from FindCloneAPI import FindCloneAPI
import settings


class Catalog:
    def __init__(self, name):
        self.name = name


class Product:
    def __init__(self, user_id):
        self.user_id = user_id
        self.product = None
        self.section = None
        self.price = None
        self.amount = None
        self.amount_MAX = None
        self.code = None


class AddProduct:
    def __init__(self, section):
        self.section = section
        self.product = None
        self.price = None
        self.info = None


class DownloadProduct:
    def __init__(self, name_section):
        self.name_section = name_section
        self.name_product = None


class GiveBalance:
    def __init__(self, login):
        self.login = login
        self.balance = None
        self.code = None


class Admin_sending_messages:
    def __init__(self, user_id):
        self.user_id = user_id
        self.text = None


# Menu catalog
def menu_catalog():
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM catalog')
    row = cursor.fetchall()

    menu = types.InlineKeyboardMarkup(row_width=1)

    for i in row:
        menu.add(types.InlineKeyboardButton(text=f'{i[0]}', callback_data=f'{i[1]}'))

    menu.add(types.InlineKeyboardButton(text='Назад', callback_data='exit_to_menu'))

    cursor.close()
    conn.close()

    return menu


# Menu section
def menu_section(name_section):
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM '{name_section}' ")
    row = cursor.fetchall()

    menu = types.InlineKeyboardMarkup(row_width=1)

    for i in row:
        menu.add(types.InlineKeyboardButton(text=f'{i[0]}', callback_data=f'{i[2]}'))

    menu.add(types.InlineKeyboardButton(text='Назад', callback_data='exit_to_menu'))

    cursor.close()
    conn.close()

    return menu


# Menu product
def menu_product(product, dict):
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()

    row = cursor.execute(f'SELECT * FROM section WHERE code = "{product}"').fetchone()
    section = row[1]
    info = row[3]

    amount = len(cursor.execute(f'SELECT * FROM "{product}"').fetchall())

    cursor.execute(f'SELECT * FROM "{section}" WHERE code = "{product}"')
    row = cursor.fetchone()

    dict.section = section
    dict.product = product
    dict.amount_MAX = amount
    dict.price = row[1]

    text = settings.text_purchase.format(
        name=row[0],
        info=info,
        price=row[1],
        amount=amount
    )

    return text, dict


def basket(user_id):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()
    row = cursor.execute(f'SELECT * FROM purchase_information WHERE user_id = "{user_id}"').fetchall()

    text = ''

    for i in row:
        text = text + '💠 ' + i[2][:10:] + ' | ' + i[1] + '\n\n'

    return text


def first_join(user_id, name, code):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()
    row = cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"').fetchall()

    ref_code = code
    if ref_code == '':
        ref_code = 0

    if len(row) == 0:
        cursor.execute(
            f'INSERT INTO users VALUES ("{user_id}", "{name}", "{datetime.datetime.now()}", "{user_id}", "{ref_code}", "0", "0")')
        conn.commit()


def admin_info():
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()
    row = cursor.execute(f'SELECT * FROM users').fetchone()

    current_time = str(datetime.datetime.now())

    amount_user_all = 0
    amount_user_day = 0
    amount_user_hour = 0

    while row is not None:
        amount_user_all += 1
        if row[2][:-15:] == current_time[:-15:]:
            amount_user_day += 1
        if row[2][:-13:] == current_time[:-13:]:
            amount_user_hour += 1

        row = cursor.fetchone()

    msg = '❕ Информаци:\n\n' \
          f'❕ За все время - {amount_user_all}\n' \
          f'❕ За день - {amount_user_day}\n' \
          f'❕ За час - {amount_user_hour}'

    return msg


def check_payment(user_id):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()
    try:
        session = requests.Session()
        session.headers['authorization'] = 'Bearer ' + settings.QIWI_TOKEN
        parameters = {'rows': '5'}
        h = session.get(
            'https://edge.qiwi.com/payment-history/v1/persons/{}/payments'.format(settings.QIWI_NUMBER),
            params=parameters)
        req = json.loads(h.text)
        result = cursor.execute(f'SELECT * FROM check_payment WHERE user_id = {user_id}').fetchone()
        comment = result[1]

        for i in range(len(req['data'])):
            if comment in str(req['data'][i]['comment']):
                balance = cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"').fetchone()

                balance = int(float(balance[5]) + float(req["data"][i]["sum"]["amount"]))

                cursor.execute(f'UPDATE users SET balance = {balance} WHERE user_id = "{user_id}"')
                conn.commit()

                cursor.execute(f'DELETE FROM check_payment WHERE user_id = "{user_id}"')
                conn.commit()

                referral_web(user_id, float(req["data"][i]["sum"]["amount"]))

                return 1, req["data"][i]["sum"]["amount"]
    except Exception as e:
        print(e)

    return 0, 0


def replenish_balance(user_id):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()

    code = random.randint(1111111111, 9999999999)

    cursor.execute(f'SELECT * FROM check_payment WHERE user_id = "{user_id}"')
    row = cursor.fetchall()

    if len(row) > 0:
        cursor.execute(f'DELETE FROM check_payment WHERE user_id = "{user_id}"')
        conn.commit()

    cursor.execute(f'INSERT INTO check_payment VALUES ("{user_id}", "{code}", "0")')
    conn.commit()

    msg = settings.replenish_balance.format(
        number=settings.QIWI_NUMBER,
        code=code,
    )

    return msg


def cancel_payment(user_id):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()

    cursor.execute(f'DELETE FROM check_payment WHERE user_id = "{user_id}"')
    conn.commit()


def profile(user_id):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()

    row = cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"').fetchone()

    return row


def buy(dict):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()

    data = str(datetime.datetime.now())
    list = ''
    cursor.execute(f'SELECT * FROM "{dict.product}"')
    row = cursor.fetchmany(int(dict.amount))

    for i in range(int(dict.amount)):
        list = list + f'💠 {data[:19]} | {row[i][0]}\n'

        cursor.execute(f'INSERT INTO purchase_information VALUES ("{dict.user_id}", "{row[i][0]}", "{data}")')
        conn.commit()

        cursor.execute(f'DELETE FROM "{dict.product}" WHERE code = "{row[i][1]}"')
        conn.commit()

    balance = cursor.execute(f'SELECT * FROM users WHERE user_id = "{dict.user_id}"').fetchone()
    balance = float(balance[5]) - (float(dict.price) * float(dict.amount))
    cursor.execute(f'UPDATE users SET balance = "{balance}" WHERE user_id = "{dict.user_id}"')
    conn.commit()

    return list


def give_balance(dict):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()

    cursor.execute(f'UPDATE users SET balance = "{dict["balance"]}" WHERE user_id = "{dict["login"]}"')
    conn.commit()


def check_balance(user_id, price):
    conn = sqlite3.connect('base_ts.sqlite')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"')
    row = cursor.fetchone()

    if float(row[5]) >= float(price):
        return 1
    else:
        return 0


def list_sections():
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM catalog')
    row = cursor.fetchall()

    sections = []

    for i in row:
        sections.append(i[1])

    return sections


def list_product():
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM section')
    row = cursor.fetchall()

    list_product = []

    for i in row:
        list_product.append(i[2])

    return list_product


def check_ref_code(user_id):
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"')
    user = cursor.fetchone()

    if int(user[3]) == 0:
        cursor.execute(f'UPDATE users SET ref_code = {user_id} WHERE user_id = "{user_id}"')
        conn.commit()

    return user_id


def set_wait_photo_status(user_id, st):
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()

    cursor.execute(f'UPDATE users SET photo_status = {st} WHERE user_id = "{user_id}"')
    conn.commit()


def get_wait_photo_status(user_id):
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"')
    row = cursor.fetchone()

    return row[6]


def recognize(user_id):
    file = f'files/{user_id}.png'
    find = FindCloneAPI()
    find.login()
    find.upload(file)
    return find.out()


def referral_web(user_id, deposit_sum):
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"')
    user = cursor.fetchone()

    if user[4] == '0':
        return
    else:
        user2 = cursor.execute(f'SELECT * FROM users WHERE user_id = "{user[4]}"').fetchone()

        profit = (deposit_sum / 100) * float(settings.ref_percent)

        balance = float(user[5]) + profit

        cursor.execute(f'UPDATE users SET balance = {balance} WHERE user_id = "{user[4]}"')
        conn.commit()

        ref_log(user2[0], profit, user2[1])


def ref_log(user_id, profit, name):
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM ref_log WHERE user_id = "{user_id}"')
    user = cursor.fetchall()

    if len(user) == 0:
        cursor.execute(f'INSERT INTO ref_log VALUES ("{user_id}", "{profit}", "{name}")')
        conn.commit()
    else:
        all_profit = user[0][1]

        all_profit = float(all_profit) + float(profit)

        cursor.execute(f'UPDATE ref_log SET all_profit = {all_profit} WHERE user_id = "{user_id}"')
        conn.commit()


def check_all_profit_user(user_id):
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM ref_log WHERE user_id = "{user_id}"')
    user = cursor.fetchall()

    if len(user) == 0:
        return 0
    else:
        return user[0][1]


def admin_top_ref():
    conn = sqlite3.connect("base_ts.sqlite")
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM ref_log')
    users = cursor.fetchall()

    msg = '<b>Это топ рефералов за все время:</b>\n'

    for i in users:
        msg = msg + f'{i[0]}/{i[2]} - {i[1]} ₽\n'

    return msg
