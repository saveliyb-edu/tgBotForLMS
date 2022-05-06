import pandas as pd
import os

import aiohttp


def read_df(name, sep=";"):
    # global df
    if os.path.exists("./name"):
        df = pd.read_csv(f'{name}', sep=sep)
    else:
        df = pd.DataFrame(columns=[
            "User_id", "Chat_id", "name", "message_count", "message_count_in_fact", "lvl", "karma", "karma_time",
            "action_points", "action_time"
        ])
    return df


def check_prefix(prefix) -> str:
    if 0 < len(prefix) <= 16:
        for i in list(prefix.lower()):
            if i not in "abcdefghijklmnopqrstuvwxyz ":
                return "not_litters"
        return "is_prefix"
    else:
        return "no_len"


async def new_cat(flag: bool =True):
    async with aiohttp.ClientSession().get("https://thiscatdoesnotexist.com/") as response:
        content = await response.read()

        # response = await session.get("https://thiscatdoesnotexist.com/")

    # p = requests.get("https://thiscatdoesnotexist.com/")
        if flag:
            out = open("img.jpg", "wb")
            out.write(content)
            out.close()
            return content
        else:
            return content
