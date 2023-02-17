from telebot import types

# Main menu
main_menu = types.InlineKeyboardMarkup(row_width=2)

main_menu.add(
    types.InlineKeyboardButton(text='🔎 Найти человека по фото', callback_data='catalog'),
)

main_menu.add(
    types.InlineKeyboardButton(text='💸 Пополнить баланс', callback_data='replenish_balance'),
)
main_menu.add(
    types.InlineKeyboardButton(text='💸 Реферальная система', callback_data='referral_web'),
)

main_menu.add(
    types.InlineKeyboardButton(text='👤 Профиль', callback_data='profile'),
    types.InlineKeyboardButton(text='ℹ Информация', callback_data='infom'),
)

replenish_btn = types.InlineKeyboardMarkup(row_width=1)
replenish_btn.add(
    types.InlineKeyboardButton(text='💸 Пополнить баланс', callback_data='replenish_balance'),
)

# Admin menu
admin_menu = types.InlineKeyboardMarkup(row_width=2)
admin_menu.add(types.InlineKeyboardButton(text='💸 Изменить баланс', callback_data='give_balance'))
admin_menu.add(types.InlineKeyboardButton(text='📧 Рассылка', callback_data='admin_sending_messages'))
admin_menu.add(
    types.InlineKeyboardButton(text='◀ Выйти', callback_data='exit_admin_menu')
)

polit_menu = types.InlineKeyboardMarkup(row_width=2)
polit_menu.add(
    types.InlineKeyboardButton(text='🤝 Политика конфиденциальности', callback_data='polit')
)
polit_menu.add(
    types.InlineKeyboardButton(text='◀ Назад', callback_data='exit_to_menu')
)

# Back to admin menu
back_to_admin_menu = types.InlineKeyboardMarkup(row_width=1)
back_to_admin_menu.add(
    types.InlineKeyboardButton(text='◀ Вернуться в админ меню', callback_data='back_to_admin_menu')
)

after_recognize_menu = types.InlineKeyboardMarkup(row_width=2)
after_recognize_menu.add(
    types.InlineKeyboardButton(text='🔃 Повторить', callback_data='catalog'),
    types.InlineKeyboardButton(text='◀ В главное меню', callback_data='exit_to_menu'),
)

btn_purchase = types.InlineKeyboardMarkup(row_width=2)
btn_purchase.add(
    types.InlineKeyboardButton(text='💸 Оплатить', callback_data='buy'),
    types.InlineKeyboardButton(text='◀ Выйти', callback_data='exit_to_menu')
)

btn_ok = types.InlineKeyboardMarkup(row_width=3)
btn_ok.add(
    types.InlineKeyboardButton(text='🆗 Понял', callback_data='btn_ok')
)

to_close = types.InlineKeyboardMarkup(row_width=3)
to_close.add(
    types.InlineKeyboardButton(text='❌', callback_data='to_close')
)
