import time

import aiogram
import requests
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import CONFIG
import TEXT

from filters import IsAdminFilter

from CONFIG import Config
from func import *

import logging

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()

bot = aiogram.Bot(token=Config.TOKEN)

dp = aiogram.Dispatcher(bot, storage=storage)

# activate filters
dp.filters_factory.bind(IsAdminFilter)

df = read_df("chats.csv")
columns = ["User_id", "name", "message_count", "karma"]
df_global = pd.DataFrame(columns=columns)

# new_cat()


async def message_counter(message: types.Message, flag=True):
    global df, df_global
    if len(df[(df["User_id"] == str(message.from_user.id)) & (df["Chat_id"] == str(message.chat.id))]) > 0:
        if flag:
            numb = int(df.loc[(df["User_id"] == str(message.from_user.id)) &
                              (df["Chat_id"] == str(message.chat.id)), "message_count"]) + 1
            karma = int(df.loc[(df["User_id"] == str(message.from_user.id)) &
                               (df["Chat_id"] == str(message.chat.id)), "karma"])

            numb_ = numb

            if karma > 10:
                numb_ += karma // 10

            df.loc[(df["User_id"] == str(message.from_user.id)) &
                   (df["Chat_id"] == str(message.chat.id)), "message_count"] = numb_
            df.loc[(df["User_id"] == str(message.from_user.id)) &
                   (df["Chat_id"] == str(message.chat.id)), "message_count_in_fact"] = numb

            df_global.loc[(df["User_id"] == str(message.from_user.id)), "message_count"] = numb
    else:
        df2 = pd.DataFrame({
            "User_id": str(message.from_user.id),
            "Chat_id": str(message.chat.id),
            "name": str(message.from_user.first_name),
            "message_count": 0,
            "message_count_in_fact": 0,
            "lvl": 1,
            "karma": 0,
            "karma_time": int(time.time()),
            "action_points": 2,
            "action_time": int(time.time())
        }, index=[0])
        df = pd.concat((df, df2), ignore_index=True)

        df2 = pd.DataFrame({
            "User_id": str(message.from_user.id),
            "name": str(message.from_user.first_name),
            "message_count": 0,
            "karma": 0
        }, index=[0])
        df_global = pd.concat((df_global, df2), ignore_index=True)
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
    timing = CONFIG.Config.TIMING
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
    # df2 = df.loc[(df["User_id"] == str(message.from_user.id)) &
    #                    (df["Chat_id"] == str(message.chat.id))]
    # if not df2.empty:
    #     action = int(df.loc[(df["User_id"] == str(message.from_user.id)) &
    #                 (df["Chat_id"] == str(message.chat.id)), "action_points"])
    #     print(f"action: {action}")
    #     if action > 0:
            # if await check2karma(message):
                # df.loc[(df["User_id"] == str(message.from_user.id)) &
                #        (df["Chat_id"] == str(message.chat.id)), "action_points"] = action - 1
    if "+" in message.text and not ("-" in message.text) and await check2karma(message):
        df2 = df.loc[(df["User_id"] == str(message.from_user.id)) &
                     (df["Chat_id"] == str(message.chat.id))]
        if not df2.empty:
            action = int(df.loc[(df["User_id"] == str(message.from_user.id)) &
                                (df["Chat_id"] == str(message.chat.id)), "action_points"])
            print(f"action: {action}")
            if action > 0:
                df.loc[(df["User_id"] == str(message.from_user.id)) &
                       (df["Chat_id"] == str(message.chat.id)), "action_points"] = action - 1
                karma = int(df.loc[(df["User_id"] == str(message.reply_to_message.from_user.id)) &
                                   (df["Chat_id"] == str(message.chat.id)), "karma"]) + 1
                df.loc[(df["User_id"] == str(message.reply_to_message.from_user.id)) &
                       (df["Chat_id"] == str(message.chat.id)), "karma"] = karma
            else:
                await message.reply("у вас не достаточно очков действий. обновите их")
    elif "-" in message.text and not ("+" in message.text and await check2karma(message)):
        df2 = df.loc[(df["User_id"] == str(message.from_user.id)) &
                     (df["Chat_id"] == str(message.chat.id))]
        if not df2.empty:
            action = int(df.loc[(df["User_id"] == str(message.from_user.id)) &
                                (df["Chat_id"] == str(message.chat.id)), "action_points"])
            print(f"action: {action}")
            if action > 0:
                df.loc[(df["User_id"] == str(message.from_user.id)) &
                       (df["Chat_id"] == str(message.chat.id)), "action_points"] = action - 1
                karma = int(df.loc[(df["User_id"] == str(message.reply_to_message.from_user.id)) &
                                   (df["Chat_id"] == str(message.chat.id)), "karma"]) - 1
                df.loc[(df["User_id"] == str(message.reply_to_message.from_user.id)) &
                       (df["Chat_id"] == str(message.chat.id)), "karma"] = karma
            else:
                await message.reply("у вас не достаточно очков действий. обновите их")
    #         else:
    #             return
    #     else:
    #         await message.reply("у вас не достаточно очков действий. обновите их")
    #         return
    # return


@dp.message_handler(content_types=["new_chat_members"])
async def on_user_joined(message: types.Message):
    await message_counter(message, flag=False)
    await bot.restrict_chat_member(chat_id=message.chat.id,
                                   user_id=message.from_user.id,
                                   permissions=Config.LEVELS_for_PERMISIONS[1]
                                   )


@dp.message_handler(is_admin=True, commands=["ban", "kick", "b"])
async def cmd_ban(message: types.Message):
    if not message.reply_to_message:
        await message.reply(TEXT.REPLY_ANSWER)
        return

    await message.bot.delete_message(message.chat.id, message.message_id)
    await message.bot.kick_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id)

    await message.reply_to_message.reply("Пользоавтель забанен")


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


@dp.message_handler(is_admin=True, commands=["admin_help", "ah", "ahelp", "adminhelp"])
async def admin_help(message: types.Message):
    await message.answer(TEXT.ADMIN_HELP)


@dp.message_handler(commands=["help", "h"])
async def help(message: types.Message):
    await message.answer(TEXT.HELP)


@dp.message_handler(is_admin=True, commands=["mute", "m"])
async def mute(message: types.Message):
    global df
    print(message.text)
    if not message.reply_to_message:
        await message.reply(TEXT.REPLY_ANSWER)
        return
    if len(message.text.split()) == 2:
        try:
            minute = int(message.text.split()[1])
        except ValueError:
            await message.reply("Укажите количество минут!")
            return
    else:
        await message.reply("Укажите количество минут!")
        return
    point = int(df.loc[(df["User_id"] == str(message.from_user.id)) &
                       (df["Chat_id"] == str(message.chat.id)), "action_points"])
    if minute > 0 and point > 0:
        await bot.restrict_chat_member(chat_id=message.chat.id,
                                       user_id=message.reply_to_message.from_user.id,
                                       permissions=types.ChatPermissions(can_send_messages=False,
                                                                         can_send_media_messages=False,
                                                                         can_send_polls=False,
                                                                         can_send_other_messages=False,
                                                                         can_add_web_page_previews=False,
                                                                         can_change_info=False,
                                                                         can_invite_users=False,
                                                                         can_pin_messages=False
                                                                         ),
                                       until_date=int(time.time()) + minute * 60)
        df.loc[(df["User_id"] == str(message.from_user.id)) &
               (df["Chat_id"] == str(message.chat.id)), "action_points"] = point - 1
        if point == 1:
            df.loc[(df["User_id"] == str(message.from_user.id)) &
                   (df["Chat_id"] == str(message.chat.id)), "action_time"] = time.time()
    else:
        await message.reply("Укажите количество минут!")
        return
    await message.reply_to_message.reply("Пользоавтель забмьючен")


@dp.message_handler(commands=["unmute", "um"])
async def unmute(message: types.Message):
    global df
    print(message.text)
    if not message.reply_to_message:
        await message.reply(TEXT.REPLY_ANSWER)
        return
    lvl = int(df.loc[(df["User_id"] == str(message.from_user.id)) &
                     (df["Chat_id"] == str(message.chat.id)), "lvl"])
    await bot.restrict_chat_member(chat_id=message.chat.id,
                                   user_id=message.reply_to_message.from_user.id,
                                   permissions=Config.LEVELS_for_PERMISIONS[lvl + 1]
                                   )
    await message.reply_to_message.reply("Пользоавтель размьючен")


@dp.message_handler(commands=["update_action_points"])
async def update_action_points(message: types.Message):
    time_ = df.loc[(df["User_id"] == str(message.from_user.id)) &
                   (df["Chat_id"] == str(message.chat.id)), "action_time"].to_dict()[0]
    if int(time.time()) > time_ + 24 * 3600:
        df.loc[(df["User_id"] == str(message.reply_to_message.from_user.id)) &
               (df["Chat_id"] == str(message.chat.id)), "action_time"] = time.time()
        lvl = int(df.loc[(df["User_id"] == str(message.from_user.id)) & (df["Chat_id"] == str(message.chat.id)), "lvl"])
        df.loc[(df["User_id"] == str(message.reply_to_message.from_user.id)) &
               (df["Chat_id"] == str(message.chat.id)), "action_time"] = Config.LEVELS_action_points[lvl]
        await message.reply(TEXT.reply_update_action_points(Config.LEVELS_action_points[lvl]))
    else:
        await message.reply(TEXT.reply_no_update_action_points(time_ + 24 * 3600 - int(time.time())))


@dp.message_handler(commands=["point"])
async def check_point(message: types.Message):
    # points = df.loc[(df["User_id"] == str(message.from_user.id)) &
    #                 (df["Chat_id"] == str(message.chat.id)), "action_points"].to_dict()[0]
    points = int(df.loc[(df["User_id"] == str(message.from_user.id)) & (df["Chat_id"] == str(message.chat.id)), "action_points"])
    print(points)
    await message.reply(f"У вас осталось {points} очков действий")


@dp.message_handler(is_admin = True, commands=["prefix", "p"])
async def set_prefix(message: types.Message):
    prefix = message.text.split()[-1]
    ans = check_prefix(prefix)
    if ans == "no_len":
        await message.reply("❗️не допустимая длина префикса\nдлина префикса должна быть в диапозоне от 0 до 16")
        return
    elif ans == "not_litters":
        await message.reply("❗️не допустимый формат префикса\nпрефикс должен состоять только из латинских букв")
        return
    else:
        await bot.set_chat_administrator_custom_title(message.chat.id, message.from_user.id, prefix)
        await message.reply(f"ваш префикс {prefix}")
        return


@dp.message_handler(commands=["statistics"])
async def statistics(message: types.Message):
    inline_kb_full = InlineKeyboardMarkup(row_width=2)
    inline_btn_1 = InlineKeyboardButton('самые активные люди чата', callback_data='statistics_people_in_chat')
    inline_btn_2 = InlineKeyboardButton('немного о чате', callback_data='info_about_chat')
    inline_btn_3 = InlineKeyboardButton('самые активные люди', callback_data='statistics_people_in_world')
    inline_kb_full.add(inline_btn_1)
    inline_kb_full.add(inline_btn_2)
    inline_kb_full.add(inline_btn_3)
    await message.reply("выберите какую именно статистику вы хотите видеть?", reply_markup=inline_kb_full)


@dp.callback_query_handler(text="statistics_people_in_chat")
async def statistics_people_in_chat(call: types.CallbackQuery):
    ans_df = df.loc[df["Chat_id"] == str(call.message.chat.id)].sort_values(by=["message_count_in_fact"],
                                                                            ascending=False)[:5]

    await call.message.answer(TEXT.most_activity_people(ans_df))


@dp.callback_query_handler(text="info_about_chat")
async def info_about_chat(call: types.CallbackQuery):
    count = df.loc[(df["Chat_id"] == str(call.message.chat.id)), "message_count_in_fact"].sum()
    active_users = len(df.loc[(df["Chat_id"] == str(call.message.chat.id)), "message_count"])
    mean_lvl = df.loc[(df["Chat_id"] == str(call.message.chat.id)), "lvl"].mean()
    mean_karma = df.loc[(df["Chat_id"] == str(call.message.chat.id)), "karma"].mean()
    print(count, active_users, mean_lvl, mean_karma)
    await call.message.answer(TEXT.info(count, active_users, round(mean_lvl, 2), round(mean_karma, 2)))


@dp.callback_query_handler(text="statistics_people_in_world")
async def statistics_people_in_world(call: types.CallbackQuery):
    ans_df = df_global.sort_values(by=["message_count"], ascending=False)[:5]

    await call.message.answer(TEXT.most_activity_people(ans_df, in_chat=False))


@dp.message_handler(commands=["cat", "new_cat"])
async def new_cat_for_chat(message: types.Message):
    photo = await new_cat(flag=False)
    await message.answer_photo(photo)


@dp.message_handler()
async def echo(message: types.Message):
    if message.text[0] == "/":
        await message.reply("Мне жаль, я не знаю такую команду.\nИспользуй /help что бы посмотреть что я умею")
    await update_karma(message)
    await message_counter(message)
    # print(message.chat.shifted_id)


if __name__ == '__main__':
    aiogram.executor.start_polling(dp)
