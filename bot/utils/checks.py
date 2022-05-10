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
    cluster = MongoClient(mongoclient)
    banned_users = cluster["owner"]["botban"]
    banned = banned_users.find_one({"user_id": int(ctx.event.message.author.id)})

    if not banned:
        return True
    else:
        return False