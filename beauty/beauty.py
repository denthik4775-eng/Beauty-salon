import telebot
from telebot import types

BOT_TOKEN = '8216114774:AAHvmxCht79fVCFMnM14WqO2FOkBF5QxLx4'
DIRECTOR_CHAT_ID = 640876100  

bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}  

studios = ['Студия 1', 'Студия 2', 'Студия 3'] 
masters = ['Мастер А', 'Мастер Б', 'Мастер В']   
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('📝 Подать жалобу'))
    bot.send_message(message.chat.id, 
                    '👋 Добро пожаловать! Нажмите кнопку для подачи жалобы.',
                    reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == '📝 Подать жалобу')
def ask_name(message):
    bot.send_message(message.chat.id, 'Введите ваше имя:')
    bot.register_next_step_handler(message, process_name_step)

def process_name_step(message):
    user_id = message.from_user.id
    user_data[user_id] = {'name': message.text}
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for studio in studios:
        markup.add(types.KeyboardButton(studio))
    markup.add(types.KeyboardButton('❌ Отмена'))
    bot.send_message(message.chat.id, 'Выберите студию:', reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text in studios + ['❌ Отмена'])
def process_studio_step(message):
    if message.text == '❌ Отмена':
        cleanup_user_data(message.from_user.id)
        bot.send_message(message.chat.id, 'Жалоба отменена.', reply_markup=types.ReplyKeyboardRemove())
        return
    
    user_id = message.from_user.id
    user_data[user_id]['studio'] = message.text
    
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for master in masters:
        markup.add(types.KeyboardButton(master))
    markup.add(types.KeyboardButton('❌ Отмена'))
    bot.send_message(message.chat.id, 'Выберите мастера:', reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text in masters + ['❌ Отмена'])
def process_master_step(message):
    if message.text == '❌ Отмена':
        cleanup_user_data(message.from_user.id)
        bot.send_message(message.chat.id, 'Жалоба отменена.', reply_markup=types.ReplyKeyboardRemove())
        return
    
    user_id = message.from_user.id
    user_data[user_id]['master'] = message.text
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('📅 Выбрать время'))
    markup.add(types.KeyboardButton('❌ Отмена'))
    bot.send_message(message.chat.id, 'Нажмите для ввода времени визита:', reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == '📅 Выбрать время')
def process_time_step(message):
    bot.send_message(message.chat.id, 'Введите время визита (дата и время, например: 2025-11-28 15:00):')
    bot.register_next_step_handler(message, process_time_input)

def process_time_input(message):
    user_id = message.from_user.id
    user_data[user_id]['time'] = message.text
    bot.send_message(message.chat.id, 'Опишите суть жалобы:')
    bot.register_next_step_handler(message, process_complaint)

def process_complaint(message):
    user_id = message.from_user.id
    user_data[user_id]['complaint'] = message.text
    
    # Формируем сообщение для директора
    data = user_data[user_id]
    full_msg = f"""🚨 Новая жалоба!

👤 Имя: {data['name']}
🏢 Студия: {data['studio']}
👨‍💼 Мастер: {data['master']}
⏰ Время визита: {data['time']}
📝 Жалоба: {data['complaint']}

📱 Контакт: @{message.from_user.username or 'нет username'}
ID: {user_id}"""
    
    bot.send_message(DIRECTOR_CHAT_ID, full_msg)
    
    bot.send_message(message.chat.id, 
                    '✅ Спасибо! Жалоба отправлена директору.',
                    reply_markup=types.ReplyKeyboardRemove())
    
    cleanup_user_data(user_id)

def cleanup_user_data(user_id):
    if user_id in user_data:
        del user_data[user_id]

if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)
