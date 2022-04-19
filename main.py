# from time import time
import time

import aiogram
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import pandas as pd
import os
import TEXT

from filters import IsAdminFilter

from CONFIG import Config

import logging

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()

bot = aiogram.Bot(token=Config.TOKEN)

dp = aiogram.Dispatcher(bot, storage=storage)
# activate filters


dp.filters_factory.bind(IsAdminFilter)


def read_df(name, sep=";"):
    global df
    if os.path.exists("./name"):
        df = pd.read_csv(f'{name}', sep=sep)
    else:
        df = pd.DataFrame(columns=[
            "User_id", "Chat_id", "message_count", "lvl", "karma", "karma_time", "action_points"
        ])
    return df


df = read_df("chats.csv")


async def message_counter(message: types.Message, flag=True):
    global df
    if len(df[(df["User_id"] == str(message.from_user.id)) & (df["Chat_id"] == str(message.chat.id))]) > 0:
        if flag:
            numb = int(df.loc[(df["User_id"] == str(message.from_user.id)) &
                              (df["Chat_id"] == str(message.chat.id)), "message_count"]) + 1
            karma = int(df.loc[(df["User_id"] == str(message.from_user.id)) &
                               (df["Chat_id"] == str(message.chat.id)), "karma"])
            if karma > 10:
                numb += karma // 10
            df.loc[(df["User_id"] == str(message.from_user.id)) &
                   (df["Chat_id"] == str(message.chat.id)), "message_count"] = numb
    else:
        # if message.chat.id != додлать сравнение с id бота
        df2 = pd.DataFrame({
            "User_id": str(message.from_user.id),
            "Chat_id": str(message.chat.id),
            "message_count": 0,
            "lvl": 1,
            "karma": 0,
            "karma_time": int(time.time()),
            "action_points": 2
        }, index=[0])
        df = pd.concat((df, df2), ignore_index=True)
    print(df[:])


async def check2karma(message: types.Message):
    if not message.reply_to_message:
        await message.reply(TEXT.REPLY_ANSWER)
        return False

    if message.reply_to_message.from_user.id == message.from_user.id:
        await message.reply("Нельзя отмечать себя!")
        return False
    karma_time = int(df.loc[(df["User_id"] == str(message.from_user.id)) &
                            (df["Chat_id"] == str(message.chat.id)), "karma_time"])
    timing = 60
    print(karma_time, karma_time + timing, int(time.time()))
    if karma_time + timing > int(time.time()):
        print("True")
        await message.reply(TEXT.not_update_karma(karma_time, timing))
        return False
    await message_counter(message.reply_to_message, flag=False)
    df.loc[(df["User_id"] == str(message.from_user.id)) &
           (df["Chat_id"] == str(message.chat.id)), "karma_time"] = int(time.time())
    return True


async def check2lvl_up(message: types.Message) -> str:
    counter = int(df.loc[(df["User_id"] == str(message.from_user.id)) & (df["Chat_id"] == str(message.chat.id)),
                         "message_count"])
    lvl = int(df.loc[(df["User_id"] == str(message.from_user.id)) & (df["Chat_id"] == str(message.chat.id)), "lvl"])
    if lvl == Config.MAX_LEVEL:
        return TEXT.MAX_LEVEL
    elif Config.LEVELS[lvl + 1] <= counter:
        df.loc[(df["User_id"] == str(message.from_user.id)) & (df["Chat_id"] == str(message.chat.id)), "lvl"] = lvl + 1
        await bot.restrict_chat_member(chat_id=message.chat.id,
                                       user_id=message.from_user.id,
                                       permissions=Config.LEVELS_for_PERMISIONS[lvl + 1]
                                       )
        return TEXT.lvl_up(lvl + 1)
    else:
        return TEXT.not_suffice_to_level_up(Config.LEVELS[lvl + 1] - counter)


async def check2lvl_up_for_admin(message: types.Message) -> str:
    counter = int(df.loc[(df["User_id"] == str(message.from_user.id)) & (df["Chat_id"] == str(message.chat.id)),
                         "message_count"])
    lvl = int(df.loc[(df["User_id"] == str(message.from_user.id)) & (df["Chat_id"] == str(message.chat.id)), "lvl"])
    if lvl == Config.MAX_LEVEL:
        return TEXT.MAX_LEVEL
    elif Config.LEVELS[lvl + 1] <= counter:
        df.loc[(df["User_id"] == str(message.from_user.id)) & (df["Chat_id"] == str(message.chat.id)), "lvl"] = lvl + 1
        return TEXT.lvl_up(lvl + 1)
    else:
        return TEXT.not_suffice_to_level_up(Config.LEVELS[lvl + 1] - counter)


async def update_karma(message: types.Message):
    global df
    if "+" in message.text and not ("-" in message.text) and await check2karma(message):
        karma = int(df.loc[(df["User_id"] == str(message.reply_to_message.from_user.id)) &
                           (df["Chat_id"] == str(message.chat.id)), "karma"]) + 1
        df.loc[(df["User_id"] == str(message.reply_to_message.from_user.id)) &
               (df["Chat_id"] == str(message.chat.id)), "karma"] = karma
    elif "-" in message.text and not ("+" in message.text) and await check2karma(message):
        karma = int(df.loc[(df["User_id"] == str(message.reply_to_message.from_user.id)) &
                           (df["Chat_id"] == str(message.chat.id)), "karma"]) - 1
        df.loc[(df["User_id"] == str(message.reply_to_message.from_user.id)) &
               (df["Chat_id"] == str(message.chat.id)), "karma"] = karma
    else:
        return


@dp.message_handler(content_types=["new_chat_members"])
async def on_user_joined(message: types.Message):
    await message_counter(message, flag=False)
    await bot.restrict_chat_member(chat_id=message.chat.id,
                                   user_id=message.from_user.id,
                                   permissions=Config.LEVELS_for_PERMISIONS[1]
                                   )


@dp.message_handler(is_admin=True, commands=["ban"])
async def cmd_ban(message: types.Message):
    if not message.reply_to_message:
        await message.reply(TEXT.REPLY_ANSWER)
        return

    await message.bot.delete_message(message.chat.id, message.message_id)
    await message.bot.kick_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id)

    await message.reply_to_message.reply("Пользоавтель забанен\nПарвосудие свершилось :3")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(TEXT.HELLO)


@dp.message_handler(is_admin=True, commands=["lvl", "lvl_up", "up"])
async def lvl_up(message: types.Message):
    """костыль для админов"""
    await message_counter(message, flag=False)
    await message.reply(await check2lvl_up_for_admin(message))


@dp.message_handler(commands=["lvl", "lvl_up", "up"])
async def lvl_up(message: types.Message):
    await message_counter(message, flag=False)
    await message.reply(await check2lvl_up(message))


@dp.message_handler(commands=["karma"])
async def check_my_karma(message: types.Message):
    global df
    await message_counter(message, flag=False)
    karma = int(df.loc[(df["User_id"] == str(message.from_user.id)) & (df["Chat_id"] == str(message.chat.id)), "karma"])
    await message.reply(TEXT.you_karma(karma))


@dp.message_handler(commands=["help", "h"])
async def help(message: types.Message):
    await message.answer(TEXT.HELP)


@dp.message_handler(commands=["info", "i"])
async def info(message: types.Message):
    count = df.loc[(df["Chat_id"] == str(message.chat.id)), "message_count"].sum()
    active_users = len(df.loc[(df["Chat_id"] == str(message.chat.id)), "message_count"])
    mean_lvl = df.loc[(df["Chat_id"] == str(message.chat.id)), "lvl"].mean()
    mean_karma = df.loc[(df["Chat_id"] == str(message.chat.id)), "karma"].mean()
    print(count, active_users, mean_lvl, mean_karma)
    await message.answer(TEXT.info(count, active_users, round(mean_lvl, 2), round(mean_karma, 2)))


@dp.message_handler()
async def echo(message: types.Message):
    await update_karma(message)
    await message_counter(message)


if __name__ == '__main__':
    aiogram.executor.start_polling(dp)
