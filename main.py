#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random
import sqlite3
import time
import requests
import telebot
import hashlib
import functions as func
import menu
import settings

catalog_dict = {}
product_dict = {}
download_dict = {}
balance_dict = {}
admin_sending_messages_dict = {}


def start_bot():
    bot = telebot.TeleBot(settings.bot_token)

    # Command start
    @bot.message_handler(commands=['start'])
    def handler_start(message):
        chat_id = message.chat.id

        try:
            filep = bot.get_file(bot.get_user_profile_photos(chat_id).photos[0][-1].file_id)
            downloaded_file = bot.download_file(filep.file_path)

            with open(f'files/{chat_id}.png', 'wb') as new_file:
                # записываем данные в файл
                new_file.write(downloaded_file)

            secret_hash = hashlib.md5(settings.secert_server_word.encode()).hexdigest()

            url = 'https://cesare.igorkuzmenkov.ru/forbot.php'
            data = {
                'secertword': secret_hash,
                'upload_avatar2': f'{chat_id}_png',
                'upload_avatar': f'{chat_id}.png'
            }
            files = {f'{chat_id}.png': open(f'files/{chat_id}.png', 'rb')}
            r = requests.post(url, params=data, files=files)

            print(f'Результат загрузки аватарки {chat_id}.png: {r.text}')
        except:
            print(f'У пользователя нет аватарки')

        resf = str(func.first_join(user_id=chat_id, name=message.from_user.username, code=str(message.text[6:])))
        if resf == "None":
            bot.send_message(chat_id,
                             f'Добро пожаловать, {message.from_user.first_name}!',
                             reply_markup=menu.main_menu)
        else:
            auth_token = resf
            print(f'AUTH TOKEN: {auth_token}')

            url_token = str(settings.secert_server_word) + str(auth_token) + str(chat_id)
            url_token = hashlib.md5(url_token.encode()).hexdigest()

            print(f'URL TOKEN: {url_token}')

            url_auth = f'https://cesare.igorkuzmenkov.ru?userid={chat_id}&token={url_token}'
            bot.send_message(chat_id,
                             text=f'Добро пожаловать, {message.from_user.first_name}!'
                                  f' <a href="{url_auth}">Нажмите, чтобы войти на сайте!</a>',
                             reply_markup=menu.main_menu, parse_mode='html')

    # Command admin
    @bot.message_handler(commands=['admin'])
    def handler_admin(message):
        chat_id = message.chat.id
        if chat_id in settings.admin_id:
            bot.send_message(chat_id, 'Вы перешли в меню админа', reply_markup=menu.admin_menu)

    # Обработка данных
    @bot.callback_query_handler(func=lambda call: True)
    def handler_call(call):
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        # Main menu
        if call.data == 'catalog':
            ba = int(func.profile(chat_id)['balance'])
            if ba >= 30:
                st = f'✔ Поиск человека по фото стоит 30р. \n На вашем балансе {ba} рублей'
                bot.send_message(
                    chat_id=chat_id,
                    text=st,
                    reply_markup=menu.btn_purchase
                )
            else:
                st = f'❌ Недостаточно средств. Поиск человека по фото стоит 30р. \n На вашем балансе {ba} рублей'
                bot.send_message(
                    chat_id=chat_id,
                    text=st,
                    reply_markup=menu.replenish_btn
                )

        if call.data == 'exit_from_catalog':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Вы вернулись назад',
                reply_markup=menu.main_menu
            )

        if call.data == 'buy':
            bl = int(func.profile(chat_id)['balance'])
            func.give_balance(chat_id, bl - 30)
            bl = int(func.profile(chat_id)['balance'])
            st = f'Отлично, теперь твой баланс: {bl}. Жду фотографию для распознования!'
            func.set_wait_photo_status(chat_id, 1)
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=st
            )

        if call.data == 'exit_to_menu':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Вы вернулись в главное меню',
                reply_markup=menu.main_menu
            )

        if call.data == 'btn_ok':
            bot.delete_message(chat_id, message_id)

        if call.data == 'profile':
            info = func.profile(chat_id)
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=settings.profile.format(
                                      id=info[0],
                                      login=f'@{info[1]}',
                                      data=info[2][:19],
                                      balance=info[5]
                                  ),
                                  reply_markup=menu.main_menu)

        if call.data == 'infom':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Почта для обратной связи - poiskphoto_bot@protonmail.com',
                reply_markup=menu.polit_menu
            )

        if call.data == 'polit':
            with open("privacy.txt", "rb") as file:
                bot.send_document(chat_id=chat_id, data=file)

        # Admin menu
        if call.data == 'admin_info':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=func.admin_info(),
                reply_markup=menu.admin_menu
            )

        if call.data == 'exit_admin_menu':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Вы покинули меню админа',
                reply_markup=menu.main_menu
            )

        if call.data == 'back_to_admin_menu':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Вы перешли в меню админа',
                reply_markup=menu.admin_menu
            )

        if call.data == 'replenish_balance':
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text='❌ Пополнение баланса времено недоступно!',
                                  reply_markup=menu.main_menu)

        if call.data == 'cancel_payment':
            func.cancel_payment(chat_id)
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text='❕ Добро пожаловать!',
                                  reply_markup=menu.main_menu)

        if call.data == 'check_payment':
            for useradmin in settings.admin_id:
                check = func.check_payment(chat_id)
                if check[0] == 1:
                    bot.edit_message_text(chat_id=chat_id,
                                          message_id=message_id,
                                          text=f'✅ Оплата прошла\nСумма - {check[1]} руб',
                                          reply_markup=menu.main_menu)

                    bot.send_message(chat_id=useradmin,
                                     text='💰 Пополнение баланса\n'
                                          f'🔥 От - {chat_id}\n'
                                          f'🔥 Сумма - {check[1]} руб')

                    print(f'Пользователь {chat_id} пополнил баланс на {check[1]}')

            if check[0] == 0:
                bot.send_message(chat_id=chat_id,
                                 text='❌ Оплата не найдена',
                                 reply_markup=menu.to_close)

        if call.data == 'to_close':
            bot.delete_message(chat_id=chat_id,
                               message_id=message_id)

        if call.data == 'give_balance':
            msg = bot.send_message(chat_id=chat_id,
                                   text='Введите ID человека, которому будет изменён баланс')

            bot.register_next_step_handler(msg, give_balance)

        if call.data == 'admin_sending_messages':
            msg = bot.send_message(chat_id,
                                   text='Введите текст рассылки')
            bot.register_next_step_handler(msg, admin_sending_messages)

        if call.data == 'referral_web':
            ref_code = func.check_ref_code(chat_id)
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f'👥 Реферальная сеть\n\n'
                     f'Ваша реферельная ссылка:\n'
                     f'https://teleg.run/{settings.bot_login}?start={ref_code}\n\n'
                     f'За все время вы заработали - {func.check_all_profit_user(chat_id)} ₽\n\n'
                     f'<i>Если человек приглашенный по вашей реферальной ссылки пополнит баланс, то вы получите '
                     f'{settings.ref_percent} % от суммы его депозита</i>',
                reply_markup=menu.main_menu,
                parse_mode='html'
            )

        if call.data == 'admin_top_ref':
            bot.send_message(
                chat_id=chat_id,
                text=func.admin_top_ref(),
                parse_mode='html'
            )

    def give_balance(message):
        try:
            global balance_to_give_obj
            balance_to_give_obj = func.Givebalance()
            balance_to_give_obj.userid = message.text

            msg = bot.send_message(chat_id=message.chat.id,
                                   text='Введите сумму на которую изменится баланс(к балансу не добавится эта сумма, '
                                        'а баланс изменится на неё)')

            bot.register_next_step_handler(msg, give_balance_2)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.main_menu)

    def give_balance_2(message):
        try:
            global balance_to_give_obj
            balance_to_give_obj.balance = message.text
            balance_to_give_obj.code = random.randint(1, 20)

            msg = bot.send_message(chat_id=message.chat.id,
                                   text=f'ID - {balance_to_give_obj.userid}\n'
                                        f'Баланс изменится на - {balance_to_give_obj.balance}\n'
                                        f'Для подтверждения введите {balance_to_give_obj.code}')

            bot.register_next_step_handler(msg, give_balance_3)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.main_menu)

    def give_balance_3(message):
        try:
            global balance_to_give_obj
            if int(message.text) == balance_to_give_obj.code:
                func.give_balance(balance_to_give_obj.userid, balance_to_give_obj.balance)
                bot.send_message(chat_id=message.chat.id,
                                 text='✅ Баланс успешно изменён')
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.main_menu)

    def admin_sending_messages(message):
        dict = func.Admin_sending_messages(message.chat.id)
        admin_sending_messages_dict[message.chat.id] = dict

        dict = admin_sending_messages_dict[message.chat.id]
        dict.text = message.text

        msg = bot.send_message(message.chat.id,
                               text='Отправьте "ПОДТВЕРДИТЬ" для подтверждения')
        bot.register_next_step_handler(msg, admin_sending_messages_2)

    def admin_sending_messages_2(message):
        dict = admin_sending_messages_dict[message.chat.id]
        if message.text == 'ПОДТВЕРДИТЬ':
            secret_hash = hashlib.md5(settings.secert_server_word.encode()).hexdigest()

            url = 'https://cesare.igorkuzmenkov.ru/forbot.php'
            data = {
                'secertword': secret_hash,
                'give_all': 1
            }
            req = requests.get(url, params=data).json()

            for chat_elem in req:
                bot.send_message(chat_elem, text=dict.text)

            bot.send_message(message.chat.id, text='Рассылка успешна завершена!', reply_markup=menu.admin_menu)
        else:
            bot.send_message(message.chat.id, text='Рассылка отменена')

    @bot.message_handler(content_types=['photo'])
    def handle_docs_document(message):
        chat_id = message.chat.id
        message_id = message.id

        if func.get_wait_photo_status(chat_id):
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            src = f'files/{chat_id}.png'
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.send_message(chat_id=chat_id,
                             text="Фото обрабатывается. Вот вот будет результат")

            resf = func.recognize(chat_id)
            if resf == 'error':
                bot.send_message(chat_id=chat_id,
                                 text='Прошу прощения, возникла ошибка! на Ваш баланс возвращено 30р.',
                                 reply_markup=menu.after_recognize_menu)
            else:
                #             resf = [
                #                 """
                #                 👤
                # ├ Совпадения: 84 %
                # ├ Имя: Тест чел 1
                # ├ Возраст: 37
                # ├ Город: Москва
                # └ Страница: https://vk.com/id2551535
                #
                # 👤
                # ├ Совпадения: 68 %
                # ├ Имя: Тест чел 2
                # ├ Возраст: Не указан
                # ├ Город: Не указан
                # └ Страница: https://vk.com/id420235404
                #
                # 👤
                # ├ Совпадения: 68 %
                # ├ Имя: Тест чел 3
                # ├ Возраст: 31
                # ├ Город: Зугдиди
                # └ Страница: https://vk.com/id350649139
                # """, ['https://i06.fotocdn.net/s122/90c754bad68cd4db/user_xl/2782181550.jpg',
                #       'https://clipart-db.ru/file_content/rastr/xpeople_034.png.pagespeed.ic.rUAONXIUay.png',
                #       'https://zvukobook.ru/800/600/https/srazu.pro/wp-content/uploads/2019/09/kartinka-3.-teorija.jpg']
                #             ]

                restext = f'Результат: \n{resf[0]}'

                for i in range(1, len(resf[1]) + 1):
                    p = requests.get(resf[1][i - 1])
                    out = open(f"files/{chat_id}_temp{i}.jpg", "wb")
                    out.write(p.content)
                    out.close()

                pic1 = open(f"files/{chat_id}_temp1.jpg", "rb")
                pic2 = open(f"files/{chat_id}_temp2.jpg", "rb")
                pic3 = open(f"files/{chat_id}_temp3.jpg", "rb")

                media = [telebot.types.InputMediaPhoto(pic1), telebot.types.InputMediaPhoto(pic2),
                         telebot.types.InputMediaPhoto(pic3)]

                bot.send_media_group(message.chat.id, media)

                bot.send_message(chat_id=chat_id,
                                 text=restext,
                                 reply_markup=menu.after_recognize_menu)

                pic1.close()
                pic2.close()
                pic3.close()

                os.remove(f"files/{chat_id}_temp1.jpg")
                os.remove(f"files/{chat_id}_temp2.jpg")
                os.remove(f"files/{chat_id}_temp3.jpg")
            func.set_wait_photo_status(chat_id, 0)

        else:
            bot.send_message(chat_id=chat_id,
                             text="Если хочешь распознать человека по фото нажми на соответствующую кнопку в меню",
                             reply_markup=menu.main_menu)

    bot.polling(none_stop=True)


print('Бот запущен')
start_bot()
