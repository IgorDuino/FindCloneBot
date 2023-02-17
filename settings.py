from decouple import config

bot_token = config("TOKEN")
admins_ids = config('ADMIN_IDS', cast=lambda x: [int(i) for i in x.split(',')])
bot_login = config('BOT_LOGIN')

ref_percent = config("REF_PERCENT", cast=int)
url = config("URL")
provider_token = config("PROVIDER_TOKEN")

secret_server_word = config("SECRET_WORD")

fc_login = config("FC_LOGIN")
fc_password = config("FC_PASSWORD")
