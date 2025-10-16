import s_taper
from s_taper.consts import *
from telebot.types import Message

def is_new_player(msg: Message):
   result = users.read_all()
   for user in result:
      if user[0] == msg.chat.id:
         return False
   return True

user_scheme = {
   "userid": INT + KEY,
   "name": TEXT,
   "power": TEXT,
   "hp": INT,
   "dmg": INT,
   "lvl": INT,
   "xp": INT,
   "defend": BLN
}
users = s_taper.Taper('users', 'data.db').create_table(user_scheme)

heal_scheme = {
   'userid': INT + KEY,
   'food':TEXT
}
heals = s_taper.Taper('heals', 'data.db').create_table(heal_scheme)
