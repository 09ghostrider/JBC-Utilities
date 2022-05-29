import hikari
import lightbulb
import random
import miru
import pymongo
from pymongo import MongoClient
import datetime
import os
from dotenv import load_dotenv
import json

load_dotenv()
mongoclient = os.getenv("DATABASE")
with open("./configs/config.json") as f:
    bot_config = json.load(f)

@lightbulb.Check
def botban_check(ctx: lightbulb.Context) -> None:
    return True
    # try:
    #     user_id = int(ctx.event.message.author.id)
    # except:
    #     user_id = int(ctx.interaction.user.id)

    # cluster = MongoClient(mongoclient)
    # banned_users = cluster["owner"]["botban"]
    # banned = banned_users.find_one({"user_id": user_id})

    # if not banned:
    #     return True
    # return False

@lightbulb.Check
def jbc_server_check(ctx: lightbulb.Context) -> None:
    return ctx.guild_id == 832105614577631232

@lightbulb.Check
def testing_server_check(ctx: lightbulb.Context) -> None:
    return ctx.guild_id == 881031368199524372