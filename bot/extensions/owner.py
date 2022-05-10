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

plugin = lightbulb.Plugin("owner")
plugin.add_checks(lightbulb.owner_only)

load_dotenv()
mongoclient = os.getenv("DATABASE")
with open("./configs/config.json") as f:
    bot_config = json.load(f)

@plugin.command()
@lightbulb.option("reason", "the reason for their ban", type=str, required=False, default="None", modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.option("user", "the user to bot ban", type=hikari.User, required=True)
@lightbulb.command("botban", "ban a user from using this bot commands")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _botban(ctx: lightbulb.Context) -> None:
    user = ctx.options.user
    reason = ctx.options.reason

    if user.id in bot_config['bot']['owner_ids']:
        return await ctx.respond("Why would u want to ban yourself....")

    cluster = MongoClient(mongoclient)
    banned_users = cluster["owner"]["botban"]
    banned = banned_users.find_one({"user_id": int(user.id)})

    if banned:
        return await ctx.respond(f"{user} is already bot banned", reply=True)
    
    banned = {
        "user_id": int(user.id),
        "reason": reason
    }
    banned_users.insert_one(banned)

    await ctx.respond(f"{user} has been bot banned\nReason: {reason}", reply=True)

@plugin.command()
@lightbulb.option("user", "the user to bot unban", type=hikari.User, required=True)
@lightbulb.command("botunban", "unban a user from using this bot commands")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _botunban(ctx: lightbulb.Context) -> None:
    user = ctx.options.user

    cluster = MongoClient(mongoclient)
    banned_users = cluster["owner"]["botban"]
    banned = banned_users.find_one({"user_id": int(user.id)})

    if not banned:
        return await ctx.respond(f"{user} is not bot banned", reply=True)
    
    banned_users.delete_one({"user_id": int(user.id)})
    await ctx.respond(f"{user} has been bot unbanned", reply=True)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)