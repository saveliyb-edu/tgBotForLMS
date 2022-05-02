import time

import pandas as pd

HELLO = """Привет я бот, подсчитывающий ссобщения и выдающий определенные права"""
MAX_LEVEL = """О, похоже вы уже достигли максимального уровня"""
REPLY_ANSWER = "Эта команда должна быть ответом на сообщение!"

dct_lvl_up = {
    1: "сообщение",
    2: "сообщения",
    3: "сообщения",
    4: "сообщения"
}

HELP = "Вот всё что я умею\n\n/help - узнать что я умею\n\n/lvl - повысить свой уровень\n" + \
       "\n/karma - узнать уровень своей кармы\n\n/ban - забанить человека\n(только для админов)"


def lvl_up(lvl: int):
    return f"Ваш уровень повышен до {lvl}!✨"


def not_suffice_to_level_up(count):
    if count in dct_lvl_up.keys():
        return f"До повышения уровня вам не хватает ещё {count} {dct_lvl_up[count]}!"
    else:
        return f"До повышения уровня вам не хватает ещё {count} сообщений!"


def you_karma(karma):
    if karma <= 0:
        return f"Мне жаль, сейчас ваша карма {karma}"
    else:
        return f"Сейчас ваша карма равна {karma}"


def info(quantity_messages: int, quantity_people: int, mean_lvl: int, mean_karma: int):
    return f"💬На данный момент в чате {quantity_messages} сообщений.💬\n" +\
        f"👤Сейчас в чате {quantity_people} активных пользователей👤\n" +\
        f"🔝Средний уровень всех активных пользователей: {mean_lvl}🔝\n" +\
        f"☠Средний уровень кармы всех пользователейй: {mean_karma}👼"


def not_update_karma(karma_time, timing):
    return "Вы можете использовать карму не чаще, чем раз в час\n" + \
        f"PS. Следующий раз через {karma_time + timing - int(time.time())}"


def most_activity_people_in_chat(df: pd.DataFrame):
    text = "Самые активные люди чата:\n"
    lst = list(df.columns)
    name = lst.index("name")
    # print(name)
    count = lst.index("message_count")
    k = 0
    for i in df.itertuples(index=False):
        k += 1
        if k == 1:
            text += f"🥇){i[name].capitalize()} - {i[count]}\n"
        elif k == 2:
            text += f"🥈){i[name].capitalize()} - {i[count]}\n"
        elif k == 3:
            text += f"🥉){i[name].capitalize()} - {i[count]}\n"
        else:
            text += f"{k}){i[name].capitalize()} - {i[count]}\n"
    return text


def reply_update_action_points(point):
    return f"Ваши очки действий обнавлены до {point}"


def reply_no_update_action_points(time_):
    if time_ % 24:
        return f"Ваши очки действий смогут обновиться через {time_ // 3600} часов и {time_ % 3660 // 60} минут {time_ % 60}"
    if time_ % 60:
        return f"Ваши очки действий смогут обновиться через {time_ % 3600 // 60} минут и {time_ % 60} секунд"
    else:
        return f"Ваши очки действий смогут обновиться через {time_ % 60} секунд"