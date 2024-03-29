import json
import sqlite3
import requests
import hashlib
import settings
from FindCloneAPI import FindCloneAPI


class Catalog:
    def __init__(self, name):
        self.name = name


class SetBalance:
    def __init__(self):
        self.userid = 0
        self.balance = 0
        self.code = 0


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


class Admin_sending_messages:
    def __init__(self, user_id):
        self.user_id = user_id
        self.text = None


def first_join(user_id, name, code):
    print(f'Пользователь {user_id} запустил бота с атрибутом {code}')

    secret_hash = hashlib.md5(settings.secret_server_word.encode()).hexdigest()

    who_invite = '0'
    if code != '' and code[:5] != " auth":
        who_invite = code

    url = 'https://cesare.ru/forbot.php'
    data = {
        'secertword': secret_hash,
        'who_invite': who_invite,
        'name': name,
        'user_id': user_id
    }
    req = requests.get(url, params=data).json()

    if code[:5] == " auth":
        return code[5:]


def give_balance(chat_id, balance):
    secret_hash = hashlib.md5(settings.secret_server_word.encode()).hexdigest()

    url = 'https://cesare.ru/forbot.php'
    data = {
        'secertword': secret_hash,
        'givebalance': balance,
        'user_id': chat_id
    }
    req = requests.get(url, params=data).json()
    print(req)


def profile(user_id):
    secret_hash = hashlib.md5(settings.secret_server_word.encode()).hexdigest()

    url = 'https://cesare.ru/forbot.php'
    data = {
        'secertword': secret_hash,
        'user_id': user_id
    }
    row = requests.get(url, params=data).json()

    return row


def set_wait_photo_status(user_id, st):
    secret_hash = hashlib.md5(settings.secret_server_word.encode()).hexdigest()
    print(f'secret_hash: {secret_hash}')
    url = 'https://cesare.ru/forbot.php'
    data = {
        'secertword': secret_hash,
        'user_id': user_id,
        'give_photostat': st
    }
    req = requests.get(url, params=data).json()


def get_wait_photo_status(user_id):
    secret_hash = hashlib.md5(settings.secret_server_word.encode()).hexdigest()
    print(f'secret_hash: {secret_hash}')

    url = 'https://cesare.ru/forbot.php'
    data = {
        'secertword': secret_hash,
        'user_id': user_id,
    }

    req = requests.get(url, params=data).json()

    return int(req['photo_stat'])


def recognize(user_id):
    file = f'files/{user_id}.png'
    find = FindCloneAPI()
    find.login()
    find.upload(file)

    res_find = find.out()
    print(f'Пользователь {user_id} произвёл поиск с результатом: \n {res_find}')

    return res_find
