import telebot

bot = telebot.TeleBot("TOKEN", parse_mode="MARKDOWN")

@bot.message_handler(commands=['start'])
def start(msg):
	bot.reply_to(msg, 'Working')