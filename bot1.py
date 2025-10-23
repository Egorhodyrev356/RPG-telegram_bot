import random
import time
import datetime

from pyexpat.errors import messages
from telebot.types import Message, CallbackQuery
from telebot.types import InlineKeyboardButton as IB

import telebot
from telebot import TeleBot

import db
import fight
import text

bot = telebot.TeleBot('7495376376:AAGAQ4t7BL9eEP4lY42Y4DIwySG3foe9FUA')
temp = {}
clear = telebot.types.ReplyKeyboardRemove()


@bot.message_handler(content_types=["audio"])
def start(msg: telebot.types.Message):
    aud = msg.audio
    print(f"Бот получил аудиоi.\n"
          f"Продолжительность: {aud.duration / 60} мин.\n"
          f"Исполнитель: {aud.performer}\n"
          f"Name: {aud.title}\n"
          f"Размер файла: {aud.file_size / 1024000} МБайт")


@bot.message_handler(content_types=["photo"])
def start(msg: telebot.types.Message):
    photo_list = msg.photo
    print(photo_list)
    print(len(photo_list))
    for photo in photo_list:
        print(photo.__dict__)


@bot.message_handler(['start'])  # Обработчик команды /start
def start(msg: telebot.types.Message):
    if db.is_new_player(msg):
        reg_1(msg)
        temp[msg.chat.id] = {'name': None}
    else:
        pass


def reg_1(msg: Message):
    bot.send_message(msg.chat.id, text.reg % msg.from_user.username)
    bot.register_next_step_handler(msg, reg_2)


def reg_2(msg: Message):  # спрашиваем стихию
    # Сохраняем имя

    if not temp[msg.chat.id]["name"]:
        temp[msg.chat.id]["name"] = msg.text
    kb = telebot.types.ReplyKeyboardMarkup(True, True)
    kb.row('Земля ', 'Вода ', 'Огонь ', 'Воздух ')
    bot.send_message(msg.chat.id, "Выбери свою кнопку: ", reply_markup=kb)
    bot.register_next_step_handler(msg, reg_3)


def reg_3(msg: Message):
    if msg.text == 'Огонь':
        bot.send_message(msg.chat.id, 'Будь осторожен стихия врага не доступна')
        reg_2(msg)
        return

    temp[msg.chat.id]['power'] = msg.text
    hp, dmg = fight.power[msg.text]
    db.users.write([
        msg.chat.id, temp[msg.chat.id]["name"],
        msg.text, hp, dmg, 1, 0, False
    ])
    db.heals.write([
        msg.chat.id, {}
    ])
    print("Игрок добавлен в БД")
    bot.send_message(msg.chat.id, text.tren)
    time.sleep(2)
    menu(msg)


@bot.message_handler(['menu'])
def menu(msg: Message):
    # Если что создаём временную переменную
    try:
        print(temp[msg.chat.id])
    except KeyError:
        temp[msg.chat.id] = {}

    message = text.menu
    if db.users.read('userid', msg.chat.id)[7]:
        message += '\n/defend - защита города'
    bot.send_message(msg.chat.id, message, reply_markup=clear)


@bot.message_handler(['help'])
def help(msg: telebot.types.Message):
    bot.send_message(msg.chat.id, f'{msg.from_user.username} нужна помощь ')


# @bot.message_handler(content_types=['text'])
# def start(msg: telebot.types.Message):
#     print(msg.text)
#     print(msg.from_user.username)
#     # bot.reply_to(msg,'Ответить на сообщение')
#     bot.send_message(msg.chat.id, 'Ответить на сообщение', reply_to_message_id=msg.message_id)

@bot.message_handler(['square'])
def square(msg: Message):
    kb = telebot.types.ReplyKeyboardMarkup(True, True)
    kb.row('Тренироваться')
    kb.row('Проверить силы')
    bot.send_message(msg.chat.id, 'Ты на площади тренировок', reply_markup=kb)
    bot.register_next_step_handler(msg, square_handler)


def square_handler(msg: Message):
    if msg.text == 'Тренироваться':
        workout(msg)
    if msg.text == 'Проверить силы':
        exam(msg)


@bot.message_handler(['home'])
def home(msg: Message):
    kb = telebot.types.ReplyKeyboardMarkup(True, True)
    kb.row('Поесть')
    kb.row('Поспать')
    bot.send_message(msg.chat.id, 'Ты в своем доме. Выбери что будешь делать: ', reply_markup=kb)
    bot.register_next_step_handler(msg, home_handler)


def home_handler(msg: Message):
    if msg.text == 'Поесть':
        eat(msg)
    if msg.text == 'Поспать':
        sleep(msg)


@bot.message_handler(['healf'])
def healf(msg: Message):
    heals = db.heals.read('userid', msg.chat.id)
    heals[1]['Хлеб'] = [2, 20]
    heals[1]['Картошка'] = [3, 15]
    db.heals.write(heals)


def eat(msg: Message):
    kb = telebot.types.InlineKeyboardMarkup()
    _, food = db.heals.read('userid', msg.chat.id)
    for key in food:
        kb.row(IB(f"{key} {food[key][1]}❤️ -- {food[key][0]}шт.",
                  callback_data=f"food_{key}_{food[key][1]}"))
    if food == {}:
        bot.send_message(msg.chat.id, 'У тебя нет еды')
        menu(msg)
    else:
        bot.send_message(msg.chat.id, 'Что будешь есть?', reply_markup=kb)


@bot.callback_query_handler(func=lambda call: True)
def callback(call: CallbackQuery):
    print(call.data)
    if call.data.startswith('sleep_'):
        a = call.data.split('_')
        bot.send_message(call.message.chat.id, f'Вы легли спать на {a[1]} секунд')
        time.sleep(int(a[1]))
        fight.sleeping(call.message, a[1])
        bot.delete_message(call.message.chat.id, call.message.message_id)
        menu(call.message)
    if call.data == '0':
        menu(call.message)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.data.startswith('food_'):
        a = call.data.split('_')
        eating(call.message, a[1], a[2])
        kb = telebot.types.InlineKeyboardMarkup()
        _, food = db.heals.read('userid', call.message.chat.id)
        for key in food:
            kb.row(IB(f"{key} {food[key][1]}❤️ -- {food[key][0]}шт.",
                      callback_data=f"food_{key}_{food[key][1]}"))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb)
    if call.data == 'workout':
        player = db.users.read('userid', call.message.chat.id)
        player[4] += player[5] / 10
        player[4] = round(player[4], 4)
        db.users.write(player)
        bot.answer_callback_query(call.id, "Ты тренируешься и твоя сила увеличивается! \n"
                                           f"Теперь ты наносишь {player[4]}⚔️", True)


def eating(msg, fd, hp):
    _, food = db.heals.read('userid', msg.chat.id)
    player = db.users.read('userid', msg.chat.id)
    if food[fd][0] == 1:
        del food[fd]
    else:
        food[fd][0] -= 1
    db.heals.write([msg.chat.id, food])

    player[3] += int(hp)
    db.users.write(player)


def sleep(msg: Message):
    player = db.users.read("userid", msg.chat.id)
    low = int(fight.power[player[2]][0] * player[5]) // 2 - player[3]
    high = int(fight.power[player[2]][0] * player[5]) - player[3]
    kb = telebot.types.InlineKeyboardMarkup()
    if low > 0:
        kb.row(IB(f"Вздремнуть — +{low}❤️", callback_data=f"sleep_{low}"))
    if high > 0:
        kb.row(IB(f"Поспать — +{high}❤️", callback_data=f"sleep_{high}"))
    if len(kb.keyboard) == 0:
        kb.row(IB('Спать не хочется ', callback_data='0'))

    bot.send_message(msg.chat.id, "Выбери, сколько будешь отдыхать:", reply_markup=kb)


@bot.message_handler(['stats'])
def stats(msg: Message):
    player = db.users.read("userid", msg.chat.id)
    t = f" {player[1]}:\n" \
        f"Здоровье: {player[3]}❤️\n" \
        f"Урон: {player[4]}⚔️\n" \
        f"LVL: {player[5]}.{player[6]}⚜️\n\n" \
        f"Еда:\n"
    _, food = db.heals.read("userid", msg.chat.id)

    for f in food:
        t += f"{f} ❤️{food[f][1]} — {food[f][0]}шт.\n"
    bot.send_message(msg.chat.id, t)
    time.sleep(3)
    menu(msg)

@bot.message_handler(['defend'])
def defend(msg: Message):
   bot.send_message(msg.chat.id, text.def_1)
   time.sleep(2)
   bot.send_message(msg.chat.id, text.def_2)
   temp[msg.chat.id]["defend"] = 0
   new_enemy(msg)


def workout(msg: Message):
    kb = telebot.types.InlineKeyboardMarkup()
    kb.row(IB('Тренироваться', callback_data='workout'))
    kb.row(IB('Назад', callback_data='0'))
    bot.send_message(msg.chat.id, 'Жми чтобы тренироваться!', reply_markup=kb)


def exam(msg: Message):
    player = db.users.read('userid', msg.chat.id)
    temp[msg.chat.id]['exam_count'] = 0
    bot.send_message(msg.chat.id, f"Приготовься к испытанию, {player[1]}!", reply_markup=clear)
    time.sleep(2)
    start_exam(msg)


def start_exam(msg: Message):
    player = db.users.read('userid', msg.chat.id)
    if temp[msg.chat.id]['exam_count'] == 10 and player[4] >= 40:
        bot.send_message(msg.chat.id, 'Поздравляю! Теперь ты готов защищать город!')
        player[7] = True
        db.users.write(player)
        menu(msg)
        return
    random.choice((block, attack))(msg)


def block(msg: Message):
    sides = ['Слева', 'Справа', 'Сверху', 'Снизу']
    random.shuffle(sides)

    kb = telebot.types.ReplyKeyboardMarkup(True, True)
    kb.row(sides[0], sides[2])
    kb.row(sides[1], sides[3])

    right = random.choice(sides)
    bot.send_message(msg.chat.id, f'Защищайся тренер нападает с {right}!', reply_markup=kb)
    temp[msg.chat.id]['block_start'] = datetime.datetime.now().timestamp()
    bot.register_next_step_handler(msg, block_handler, right)


def block_handler(msg: Message, side: str):
    final = datetime.datetime.now().timestamp()
    player = db.users.read('userid', msg.chat.id)
    if final - temp[msg.chat.id]['block_start'] > player[4] / 10 or side != msg.text:
        bot.send_message(msg.chat.id, 'Твоя реакция недостаточно быстрая!')
        time.sleep(5)
        menu(msg)
        return
    else:
        bot.send_message(msg.chat.id, 'Ты справился! Продолжим')
        temp[msg.chat.id]['exam_count'] += 1
        start_exam(msg)


def attack(msg: Message):
    sides = ['Слева', 'Справа', 'Сверху', 'Снизу']
    random.shuffle(sides)

    kb = telebot.types.ReplyKeyboardMarkup(True, True)
    kb.row(sides[0], sides[2])
    kb.row(sides[1], sides[3])

    right = random.choice(sides)
    bot.send_message(msg.chat.id, f'Выбери с какой стороны напасть!', reply_markup=kb)
    bot.register_next_step_handler(msg, attack_handler, right)


def attack_handler(msg: Message, side: str):
    if msg.text == side:
        bot.send_message(msg.chat.id, 'Тренер смог защититься от твоего удара.')
        start_exam(msg)
        return
    else:
        bot.send_message(msg.chat.id, 'Тренер пропустил твой джеб')
        temp[msg.chat.id]['exam_count'] += 1
        start_exam(msg)
        return


def new_enemy(msg: Message):
    enemy = fight.Enemy()
    kb = telebot.types.ReplyKeyboardMarkup(True, True)
    kb.row("Напасть", "Отойти в сторону")
    kb.row("Сбежать в город")
    bot.send_message(msg.chat.id, text.enemy_desk(enemy), reply_markup=kb)
    bot.register_next_step_handler(msg, fight_choice, enemy)


def fight_choice(msg: Message, enemy: fight.Enemy):
    if msg.text == 'Напасть':
        fight_handler(msg, enemy)
    elif msg.text == 'Сбежать в город':
        bot.send_message(msg.chat.id, 'Повезет в другой раз')
        xp_check(msg)
        menu(msg)
    else:
        bot.send_message(msg.chat.id, 'Ты увернулся и отошел в сторону!')
        new_enemy(msg)


def fight_handler(msg: Message, enemy: fight.Enemy):
    loser = player_attack(msg, enemy)
    if loser:
        loser = enemy_attack(msg, enemy)
        if loser:
            bot.send_message(msg.chat.id, "Ты получил сильное ранение! "
                                          "Твои братья оттащили тебя в деревню.")
            temp[msg.chat.id]['defend'] = 0
            menu(msg)
            return
        else:
            fight_handler(msg,enemy)
    else:
        temp[msg.chat.id]['defend'] += enemy.dmg // 2
        bot.send_message(msg.chat.id, 'Ты победил!!!')
        new_enemy(msg)




def player_attack(msg: Message, enemy: fight.Enemy):
    player = db.users.read('userid', msg.chat.id)
    enemy.hp -= player[4]
    bot.send_message(msg.chat.id, f"Ты ударил врага на {player[4]} урона!\n"
                                  f"Теперь у него {round(enemy.hp, 2)}❤️")
    if enemy.hp <= 0:
        bot.send_message(msg.chat.id, f"Ты победил врага {enemy.name}")
        return False
    else:
        return True


def enemy_attack(msg: Message, enemy: fight.Enemy):
    player = db.users.read('userid', msg.chat.id)
    player[3] -= enemy.dmg
    bot.send_message(msg.chat.id, f"{enemy.name} ударил тебя на {enemy.dmg} урона!\n"
                                  f"Теперь у тебя {player[3]}❤️")
    db.users.write(player)
    if player[3] <= 0:
        return True
    else:
        return False


def xp_check(msg: Message):
    player = db.users.read('userid', msg.chat.id)
    player[6] += temp[msg.chat.id]['defend']
    temp[msg.chat.id]['defend'] = 0
    if player[6] >= 100:
        player[5] += 1
        player[6] = 0
        player[4] += 5
        player[3] += 50
        bot.send_message(msg.chat.id, text.new_lvl(player))
    db.users.write(player)



bot.infinity_polling()