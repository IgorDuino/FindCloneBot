import telebot
from telebot.types import LabeledPrice

token = '860744169:AAGB5gIP-8aPaluCW-Sw4aib1mZE9BOt-WA'
provider_token = '381764678:TEST:26370'

bot = telebot.TeleBot(token)

prices = [LabeledPrice(label='Пополнение баланса', amount=10000)]


@bot.message_handler(commands=['start'])
def command_start(message):
    bot.send_message(message.chat.id,
                     "Привет, это мой бот для разных текстов"
                     "Сейчас я магу продать тебе ченить несуществующее"
                     "Напиши /buy чтобы протестить (ес че плати этой картой 1111 1111 1111 1026, 12/22, CVC 000 )")


@bot.message_handler(commands=['buy'])
def command_pay(message):
    bot.send_invoice(message.chat.id, title='Пополнение баланса',
                     description='1',
                     provider_token=provider_token,
                     currency='rub',
                     photo_url='https://cesare.ru/cesare.png',
                     photo_height=512,  # !=0/None or picture won't be shown
                     photo_width=512,
                     photo_size=512,
                     is_flexible=False,  # True If you need to set up Shipping Fee
                     prices=prices,
                     start_parameter='time-machine-example',
                     invoice_payload='HAPPY FRIDAYS COUPON')


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Попробуй еще раз позже!")


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(message.chat.id,
                     f'Вы успешно пополнили баланс на`'
                     f'{message.successful_payment.total_amount / 100} {message.successful_payment.currency}`')




bot.skip_pending = True
bot.polling(none_stop=True, interval=0)
