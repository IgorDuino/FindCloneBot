#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random
import requests
import telebot
import hashlib
import functions as func
import menu
import settings
from telebot.types import LabeledPrice

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

            url = f'{settings.url}/forbot.php'
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

            url_auth = f'{settings.url}?userid={chat_id}&token={url_token}'
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

    @bot.pre_checkout_query_handler(func=lambda query: True)
    def checkout(pre_checkout_query):
        bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                      error_message="Попробуй еще раз позже!")

    @bot.message_handler(content_types=['successful_payment'])
    def got_payment(message: telebot.types.Message):
        old_balance = int(func.profile(message.chat.id)['balance'])
        func.give_balance(message.chat.id, old_balance + message.successful_payment.total_amount // 100)

        profile1 = func.profile(message.chat.id)

        new_balance = int(profile1['balance'])
        who_invite = profile1['who_invite']

        for admin_id in settings.admin_id:
            bot.send_message(chat_id=admin_id,
                             text=f'Пользователь {message.chat.id} успешно пополнил баланс на'
                                  f' {message.successful_payment.total_amount / 100} руб')

        if int(who_invite) != 0:
            ref_sum = int(message.successful_payment.total_amount / 10000 * settings.ref_percent)
            bot.send_message(chat_id=who_invite,
                             text=f'Пользователь, перешедший по вашей реферальной ссылке, пополнил баланс на  '
                                  f'{message.successful_payment.total_amount // 100} руб. Вы получили '
                                  f'{ref_sum}'
                                  f' руб ({settings.ref_percent} %).')
            old_balance_ref = int(func.profile(message.chat.id)['balance'])
            func.give_balance(who_invite, old_balance_ref + ref_sum)

        bot.send_message(chat_id=message.chat.id, text=
        f'Вы успешно пополнили баланс на`'
        f'{message.successful_payment.total_amount // 100} руб`.'
        f'Теперь ваш баланс {new_balance}', reply_markup=menu.main_menu)

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
                                  text=f'🧾 Профиль\n\n' \
                                       f'❕ Ваш id - {info["user_id"]}\n' \
                                       f'❕ Ваш логин - {info["name"]}\n' \
                                       f'❕ Дата регистрации - {info["date"]}\n\n' \
                                       f'💰 Ваш баланс - {info["balance"]} рублей',
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
            msg = bot.send_message(chat_id=chat_id,
                                   text='Введите сумму для пополнения (мин 100р)')

            bot.register_next_step_handler(msg, selecting_the__deposit_amount)

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
            profile1 = func.profile(chat_id)
            ref_code = profile1['ref_code']

            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f'👥 Реферальная сеть\n\n'
                     f'Ваша реферельная ссылка:\n'
                     f'https://teleg.run/{settings.bot_login}?start={ref_code}\n\n'
                     f'<i>Если человек приглашенный по вашей реферальной ссылки пополнит баланс, то вы получите '
                     f'{settings.ref_percent} % от суммы его депозита</i>',
                reply_markup=menu.main_menu,
                parse_mode='html'
            )

    def selecting_the__deposit_amount(message):
        if not str(message.text).isdigit():
            msg = bot.send_message(chat_id=message.chat.id,
                                   text='Вы отправили не число! Пожалуйста напишите сумму для пополнения (мин 100р)')

            bot.register_next_step_handler(msg, selecting_the__deposit_amount)

        else:
            amount = int(message.text)

            if amount < 100:
                msg = bot.send_message(chat_id=message.chat.id,
                                       text='Вы отправили число меньше 100! Пожалуйста напишите сумму для пополнения (мин 100р)')

                bot.register_next_step_handler(msg, selecting_the__deposit_amount)
            elif amount > 500000:
                msg = bot.send_message(chat_id=message.chat.id,
                                       text='Вы отправили число больше 500000! Пожалуйста напишите сумму для пополнения (мин 100р)')

                bot.register_next_step_handler(msg, selecting_the__deposit_amount)

            else:
                prices = [LabeledPrice(label='Пополнение баланса', amount=amount * 100)]
                bot.send_invoice(message.chat.id, title='Пополнение баланса',
                                 description=f'Пополнение баланса на {amount} RUB',
                                 provider_token=settings.provider_token,
                                 currency='rub',
                                 photo_url=f'{settings.url}/cesare.png',
                                 photo_height=512,  # !=0/None or picture won't be shown
                                 photo_width=512,
                                 photo_size=512,
                                 is_flexible=False,  # True If you need to set up Shipping Fee
                                 prices=prices,
                                 start_parameter='time-machine-example',
                                 invoice_payload='HAPPY FRIDAYS COUPON')

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

            url = f'{settings.url}/forbot.php'
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
