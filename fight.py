import random

import db

power = {
    'Вода': (120, 15),
    'Воздух': (100, 25),
    'Земля': (100, 20),
    'Аватар': (200, 50),
}


def sleeping(msg, hp):
    player = db.users.read('userid', msg.chat.id)
    player[3] += int(hp)
    db.users.write(player)
    print('Игрок поспал')


class Enemy:
    profs = {
        "Огненный элементаль 🪬": (30, 5),
        "Огненный проказник 🤪": (35, 8),
        "Стена Огня 🔥": (40, 15),
        "Ученик Огня 🧑‍🎓": (80, 20),
        "Студент Огня 👨‍🎓": (100, 25),
        "Заклинатель Огня 🧙": (120, 30),
        "Маг Огня 🧙‍♂️": (135, 35),
        "ОГНЕННЫЙ СМЕРЧ 🔥🌪️": (200, 80),
    }

    def __init__(self):
       self.name = random.choice(list(self.profs.keys()))
       self.hp, self.dmg = self.profs[self.name]