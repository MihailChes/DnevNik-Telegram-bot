from logic import DB_Manager
from config import *
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telebot import types

bot = TeleBot(TOKEN)
hideBoard = types.ReplyKeyboardRemove() 

cancel_button = "Отмена 🚫"
def cansel(message):
    bot.send_message(message.chat.id, "Чтобы посмотреть команды, используй - /info", reply_markup=hideBoard)
  
def no_notes(message):
    bot.send_message(message.chat.id, 'У тебя пока нет записей!\nМожешь добавить их с помошью команды /new_note')

def gen_inline_markup(rows):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for row in rows:
        markup.add(InlineKeyboardButton(row, callback_data=row))
    return markup

def gen_markup(rows):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 1
    for row in rows:
        markup.add(KeyboardButton(row))
    markup.add(KeyboardButton(cancel_button))
    return markup

attributes_of_notes = {'Имя записи' : ["Введите новое имя проекта", "note_name"],
                          'Дата' : ["Введите новую дату создания записи", "date"],
                          "Содержимое" : ["Введите новое содержимое дневника", "soda"],
                          "Статус" : ["Выберите новый статус задачи", "status_id"]}

def info_note(message, user_id, note_name):
    info = manager.get_note_info(user_id, note_name)[0]
    themes = manager.get_note_themes(note_name)
    if not themes:
        themes = 'Навыки пока не добавлены'
    bot.send_message(message.chat.id, f"""Note name: {info[0]}
Date: {info[1]}
themes: {themes}
status: {info[3]}
Content: {info[2]}

""")

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, """Привет!👋 Я бот-дневник!
Помогу тебе сохранить твои записи и информацию о них!👌
Забыл книжный дневник? Хочется пользоваться функциональным приложением, вместо заметок? Этот бот для вас!✔️
Темы, дата, даже статус записи здесь есть!❗
""")
    bot.send_photo(message.chat.id, open("images/dnevnik.png", "rb"))
    info(message)
    
@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id,
"""
Вот команды которые могут тебе помочь:

/new_note - создаёт новую запись по вашим предпочтениям
/notes - отображает все записи дневника
/update_notes - изменяет содержимое какой-либо записи
/themes - привязывает темы для записей
/delete - удаляет какую-нибудь запись

Также ты можешь ввести имя записи и узнать информацию о ней!""")
    

@bot.message_handler(commands=['new_note'])
def addtask_command(message):
    bot.send_message(message.chat.id, "Введите название записи1️⃣:")
    bot.register_next_step_handler(message, name_note)

def name_note(message):
    name = message.text
    user_id = message.from_user.id
    data = [user_id, name]
    bot.send_message(message.chat.id, "Введите содержимое записи2️⃣:")
    bot.register_next_step_handler(message, status_note, data=data)

def status_note(message, data):
    data.append(message.text)
    statuses = [x[0] for x in manager.get_statuses()] 
    bot.send_message(message.chat.id, "Введите текущий статус записи (Необязательно)3️⃣:", reply_markup=gen_markup(statuses))
    bot.register_next_step_handler(message, callback_note, data=data, statuses=statuses)

def callback_note(message, data, statuses):
    status = message.text
    if message.text == cancel_button:
        cansel(message)
        return
    if status not in statuses:
        bot.send_message(message.chat.id, "Ты выбрал статус не из списка, попробуй еще раз❌!)", reply_markup=gen_markup(statuses))
        bot.register_next_step_handler(message, callback_note, data=data, statuses=statuses)
        return
    status_id = manager.get_status_id(status)
    data.append(status_id)
    manager.insert_note([tuple(data)])
    bot.send_message(message.chat.id, "Проект сохранен✔️!")


@bot.message_handler(commands=['themes'])
def skill_handler(message):
    user_id = message.from_user.id
    notes = manager.get_notes(user_id)
    if notes:
        notes = [x[2] for x in notes]
        bot.send_message(message.chat.id, 'Выбери проект для которого нужно выбрать навык1️⃣:', reply_markup=gen_markup(notes))
        bot.register_next_step_handler(message, genre_note, notes=notes)
    else:
        no_notes(message)


def genre_note(message, notes):
    note_name = message.text
    if message.text == cancel_button:
        cansel(message)
        return
        
    if note_name not in notes:
        bot.send_message(message.chat.id, 'У тебя нет такого проекта, попробуй еще раз❌! Выбери проект для которого нужно выбрать навык.', reply_markup=gen_markup(notes))
        bot.register_next_step_handler(message, genre_note, notes=notes)
    else:
        genre = [x[1] for x in manager.get_themes()]
        bot.send_message(message.chat.id, 'Выбери навык2️⃣:', reply_markup=gen_markup(genre))
        bot.register_next_step_handler(message, set_genre, note_name=note_name, skills=genre)

def set_genre(message, note_name, skills):
    skill = message.text
    user_id = message.from_user.id
    if message.text == cancel_button:
        cansel(message)
        return
        
    if skill not in skills:
        bot.send_message(message.chat.id, 'Видимо, ты выбрал навык. не из списка, попробуй еще раз!) Выбери навык', reply_markup=gen_markup(skills))
        bot.register_next_step_handler(message, set_genre, note_name=note_name, skills=skills)
        return
    manager.insert_themes(user_id, note_name, skill )
    bot.send_message(message.chat.id, f'Навык {skill} добавлен проекту✔️ {note_name}')


@bot.message_handler(commands=['notes'])
def get_notes(message):
    user_id = message.from_user.id
    notes = manager.get_notes(user_id)
    if notes:
        text = "\n".join([f"note name:{x[2]} \nContent:{x[4]}\n" for x in notes])
        bot.send_message(message.chat.id, text, reply_markup=gen_inline_markup([x[2] for x in notes]))
    else:
        no_notes(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    note_name = call.data
    info_note(call.message, call.from_user.id, note_name)


@bot.message_handler(commands=['delete'])
def delete_handler(message):
    user_id = message.from_user.id
    notes = manager.get_notes(user_id)
    if notes:
        text = "\n".join([f"note name:{x[2]} \nContent:{x[4]}\n" for x in notes])
        notes = [x[2] for x in notes]
        bot.send_message(message.chat.id, text, reply_markup=gen_markup(notes))
        bot.register_next_step_handler(message, delete_note, notes=notes)
    else:
        no_notes(message)

def delete_note(message, notes):
    note = message.text
    user_id = message.from_user.id

    if message.text == cancel_button:
        cansel(message)
        return
    if note not in notes:
        bot.send_message(message.chat.id, 'У тебя нет такого проекта, попробуй выбрать еще раз❌!', reply_markup=gen_markup(notes))
        bot.register_next_step_handler(message, delete_note, notes=notes)
        return
    note_id = manager.get_note_id(note, user_id)
    manager.delete_note(user_id, note_id)
    bot.send_message(message.chat.id, f'Проект {note} удален❗✔️!')


@bot.message_handler(commands=['update_notes'])
def update_note(message):
    user_id = message.from_user.id
    notes = manager.get_notes(user_id)
    if notes:
        notes = [x[2] for x in notes]
        bot.send_message(message.chat.id, "Выбери проект, который хочешь изменить1️⃣:", reply_markup=gen_markup(notes))
        bot.register_next_step_handler(message, update_note_step_2, notes=notes )
    else:
        no_notes(message)

def update_note_step_2(message, notes):
    note_name = message.text
    if message.text == cancel_button:
        cansel(message)
        return
    if note_name not in notes:
        bot.send_message(message.chat.id, "Что-то пошло не так❌! Выбери проект, который хочешь изменить еще раз:", reply_markup=gen_markup(notes))
        bot.register_next_step_handler(message, update_note_step_2, notes=notes )
        return
    bot.send_message(message.chat.id, "Выбери, что требуется изменить в проекте2️⃣:", reply_markup=gen_markup(attributes_of_notes.keys()))
    bot.register_next_step_handler(message, update_note_step_3, note_name=note_name)

def update_note_step_3(message, note_name):
    attribute = message.text
    reply_markup = None 
    if message.text == cancel_button:
        cansel(message)
        return
    if attribute not in attributes_of_notes.keys():
        bot.send_message(message.chat.id, "Кажется, ты ошибся, попробуй еще раз❌!)", reply_markup=gen_markup(attributes_of_notes.keys()))
        bot.register_next_step_handler(message, update_note_step_3, note_name=note_name)
        return
    elif attribute == "Статус":
        rows = manager.get_statuses()
        reply_markup=gen_markup([x[0] for x in rows])
    bot.send_message(message.chat.id, attributes_of_notes[attribute][0], reply_markup = reply_markup)
    bot.register_next_step_handler(message, update_note_step_4, note_name=note_name, attribute=attributes_of_notes[attribute][1])

def update_note_step_4(message, note_name, attribute): 
    update_info = message.text
    if attribute== "status_id":
        rows = manager.get_statuses()
        if update_info in [x[0] for x in rows]:
            update_info = manager.get_status_id(update_info)
        elif update_info == cancel_button:
            cansel(message)
        else:
            bot.send_message(message.chat.id, "Был выбран неверный статус, попробуй еще раз❌!)", reply_markup=gen_markup([x[0] for x in rows]))
            bot.register_next_step_handler(message, update_note_step_4, note_name=note_name, attribute=attribute)
            return
    user_id = message.from_user.id
    data = (update_info, note_name, user_id)
    manager.update_notes(attribute, data)
    bot.send_message(message.chat.id, "Готово✔️! Обновления внесены✔️!)")


@bot.message_handler(func=lambda message: True)
def text_handler(message):
    user_id = message.from_user.id
    notes =[ x[2] for x in manager.get_notes(user_id)]
    note = message.text
    if note in notes:
        info_note(message, user_id, note)
        return
    bot.reply_to(message, "Тебе нужна помощь❤️?")
    info(message)

    
if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    bot.infinity_polling()
