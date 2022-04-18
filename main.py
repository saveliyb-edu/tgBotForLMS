from time import time

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


async def message_counter(message: types.Message, flag=True):
    global df
    if len(df[(df["User_id"] == str(message.from_user.id)) & (df["Chat_id"] == str(message.chat.id))]) > 0:
        if flag:
            numb = int(df.loc[(df["User_id"] == str(message.from_user.id)) &
                             (df["Chat_id"] == str(message.chat.id)), "message_count"]) + 1
            df.loc[(df["User_id"] == str(message.from_user.id)) &
                   (df["Chat_id"] == str(message.chat.id)), "message_count"] = numb
    else:
        # if message.chat.id != додлать сравнение с id бота
        df2 = pd.DataFrame({
            "User_id": str(message.from_user.id),
            "Chat_id": str(message.chat.id),
            "message_count": 0,
            "lvl": 1,
            "karma": 0
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
    await message_counter(message.reply_to_message, flag=False)
    return True


async def update_karma(message: types.Message):
    global df
    if "+" in message.text and not("-" in message.text) and await check2karma(message):
        karma = int(df.loc[(df["User_id"] == str(message.reply_to_message.from_user.id)) &
                           (df["Chat_id"] == str(message.chat.id)), "karma"]) + 1
        df.loc[(df["User_id"] == str(message.reply_to_message.from_user.id)) &
               (df["Chat_id"] == str(message.chat.id)), "karma"] = karma
    elif "-" in message.text and not("+" in message.text) and await check2karma(message):
        karma = int(df.loc[(df["User_id"] == str(message.reply_to_message.from_user.id)) &
                           (df["Chat_id"] == str(message.chat.id)), "karma"]) - 1
        df.loc[(df["User_id"] == str(message.reply_to_message.from_user.id)) &
               (df["Chat_id"] == str(message.chat.id)), "karma"] = karma
    else:
        return


def read_df(name, sep=";"):
    if os.path.exists("./name"):
        df = pd.read_csv(f'{name}', sep=sep)
    else:
        df = pd.DataFrame(columns=[
            "User_id", "Chat_id", "message_count", "lvl"
        ])
    return df


df = read_df("chats.csv")


@dp.message_handler(content_types=["new_chat_members"])
async def on_user_joined(message: types.Message):
    # print(time)
    await bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=600)


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


@dp.message_handler(commands=["lvl", "lvl_up", "up"])
async def lvl_up(message: types.Message):
    await message_counter(message, flag=False)
    counter = int(df.loc[(df["User_id"] == str(message.from_user.id)) & (df["Chat_id"] == str(message.chat.id)),
                         "message_count"])
    lvl = int(df.loc[(df["User_id"] == str(message.from_user.id)) & (df["Chat_id"] == str(message.chat.id)), "lvl"])
    if lvl == Config.MAX_LEVEL:
        await message.reply(TEXT.MAX_LEVEL)
    elif Config.LEVELS[lvl + 1] <= counter:
        df.loc[(df["User_id"] == str(message.from_user.id)) & (df["Chat_id"] == str(message.chat.id)), "lvl"] = lvl + 1
        await message.reply(TEXT.lvl_up(lvl + 1))
    else:
        await message.reply(TEXT.not_suffice_to_level_up(Config.LEVELS[lvl + 1] - counter))


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

# bot.restrict_chat_member()
# bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time()+600)