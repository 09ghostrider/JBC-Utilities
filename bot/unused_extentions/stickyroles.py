from email import message
import os
import hikari
import lightbulb
import json
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
plugin = lightbulb.Plugin("stickyroles")
ephemeral = hikari.MessageFlag.EPHEMERAL

mongoclient = os.getenv("DATABASE")
with open("./configs/config.json") as f:
    bot_config = json.load(f)

@plugin.listener(hikari.MemberDeleteEvent)
async def _on_member_remove(member: hikari.MemberDeleteEvent) -> None:
    old_member = member.old_member
    
    if not old_member:
        return
    
    user = member.user
    guild_id = member.guild_id

    role_ids = old_member.role_ids

    if role_ids == [] or role_ids == None:
        return

    roles = {
        "guild_id": int(guild_id),
        "user_id": int(user.id),
        "role_ids": role_ids
    }

    cluster = MongoClient(mongoclient)
    stickyroles = cluster["roles"]["sticky"]
    stickyroles.insert_one(roles)

@plugin.listener(hikari.MemberCreateEvent)
async def _on_member_join(member: hikari.MemberCreateEvent) -> None:
    cluster = MongoClient(mongoclient)
    stickyroles = cluster["roles"]["sticky"]

    sticky = stickyroles.find_one({"guild_id": int(member.guild_id), "user_id": int(member.user_id)})
    if not sticky:
        return

    role_ids = sticky['role_ids']
    if role_ids == []:
        return
    
    for r in role_ids:
        try:
            await member.member.add_role(r, reason="Sticky role")
        except:
            pass
    
    stickyroles.delete_one({"_id": sticky['_id']})

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)