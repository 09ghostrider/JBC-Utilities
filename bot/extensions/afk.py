import hikari
import lightbulb
import random
import miru
import pymongo
from pymongo import MongoClient
import datetime
from dotenv import load_dotenv
import os

plugin = lightbulb.Plugin("afk")

load_dotenv()
mongoclient = os.getenv("DATABASE")
with open("./secrets/prefix") as f:
    prefix = f.read().strip()

@lightbulb.Check
def perms_check(ctx: lightbulb.Context) -> None:
    cluster = MongoClient(mongoclient)
    configs = cluster["afk"]["server_configs"]

    config = configs.find_one({"guild": ctx.interaction.guild_id})
    if config == None:
        return False
    
    for r in config["req"]:
        role = ctx.app.cache.get_role(r)
        roles = ctx.interaction.member.get_roles()
        if role in roles:
            return True
    return False

@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("afk", "Set an AFK status to display when you are mentioned")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def _afk(ctx: lightbulb.Context) -> None:
    embed=hikari.Embed(title="=== Command Help ===", description="""afk - Set an AFK status to display when you are mentioned

Usage: -afk [subcommand]""", color=random.randint(0x0, 0xffffff))
    embed.add_field(name="== Subcommands ==", value="""- clear - Remove the AFK status of a member.
- ignore - Use in a channel to not return from AFK when talking in that channel.
- ignored - List all the AFK ignored channels.
- set - Set an AFK status shown when you're mentioned, and display in nickname.""")
    await ctx.respond(embed=embed)

@_afk.child
@lightbulb.add_checks(lightbulb.owner_only| lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | perms_check)
@lightbulb.option("status", "The status to set", modifier=lightbulb.commands.base.OptionModifier(3), type=str, default="AFK", required=False)
@lightbulb.command("set", "Set an AFK status shown when you're mentioned, and display in nickname.", inherit_checks=True, aliases=["s"])
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _set(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    status = ctx.options.status
    user_id = ctx.interaction.user.id
    guild_id = ctx.interaction.guild_id
    timestamp = round(datetime.datetime.now().timestamp())

    cluster = MongoClient(mongoclient)
    afk = cluster["afk"]["afk"]
    afk.delete_one({"id": user_id, "guild": guild_id})

    user_data = {
    "id": user_id,
    "guild": guild_id,
    "status": status,
    "timestamp": timestamp
    }

    # cluster = MongoClient(mongoclient)
    # afk = cluster["afk"]["afk"]
    afk.insert_one(user_data)
    await ctx.respond(f"{ctx.interaction.user.mention}: I set your AFK: {status}", role_mentions=False, user_mentions=True)

    try:
        nick = ctx.interaction.member.nickname
        if nick == None:
            nick = ctx.interaction.user.username
        await ctx.interaction.member.edit(nick=f"[AFK] {nick}", reason="Member went AFK")
    except Exception as e:
        print(e)


@_afk.child
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.MANAGE_CHANNELS))
@lightbulb.option("channel", "The channel to ignore", modifier=lightbulb.commands.base.OptionModifier(3), type=hikari.GuildChannel, required=False, default=None)
@lightbulb.command("ignore", "Use in a channel to not return from AFK when talking in that channel.", inherit_checks=True, aliases=["i"])
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _ignore(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    c = ctx.options.channel
    if c == None:
        channel = ctx.interaction.channel_id
    else:
        channel = c.id
    guild_id = ctx.interaction.guild_id

    cluster = MongoClient(mongoclient)
    configs = cluster["afk"]["server_configs"]

    config = configs.find_one({
        "guild": guild_id
    })

    if config == None:
        in_db = False
        config = {
            "guild": guild_id,
            "ignored": [],
            "req": []
        }
    else:
        in_db = True

    if channel in config["ignored"]:
        config["ignored"].pop(config["ignored"].index(channel))
        await ctx.respond(f"Removed <#{channel}> from AFK ignored list")
    else:
        config["ignored"].append(channel)
        await ctx.respond(f"Added <#{channel}> to AFK ignored list")
    
    if in_db == True:
        configs.update_one({"guild": guild_id}, {"$set":{"ignored": config["ignored"]}})
    else:
        configs.insert_one(config)

@_afk.child
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.MANAGE_CHANNELS))
@lightbulb.command("ignored", "List all the AFK ignored channels", inherit_checks=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _ignored(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    guild_id = ctx.interaction.guild_id
    cluster = MongoClient(mongoclient)
    configs = cluster["afk"]["server_configs"]

    config = configs.find_one({
        "guild": guild_id
    })

    embed = hikari.Embed(color=random.randint(0x0, 0xffffff), title="AFK ignored channels")

    if config == None or config["ignored"] == []:
        embed.description = "No ignored channels"
    else:
        desc = ""
        count = 1
        for c in config["ignored"]:
            desc = desc + "\n" + f"`{count}:` <#{c}>"
            count += 1
        embed.description = desc
    
    await ctx.respond(embed=embed, reply=True)

@_afk.child
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.MANAGE_CHANNELS))
@lightbulb.option("member", "The member to clear AFK status", type=hikari.Member)
@lightbulb.command("clear", "Remove the AFK status of a member.", inherit_checks=True, aliases=["c"])
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _clear(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    member = ctx.options.member
    user_id = member.id
    guild_id = ctx.interaction.guild_id

    cluster = MongoClient(mongoclient)
    afk = cluster["afk"]["afk"]

    user_data = afk.find_one({
        "id": {"$eq": user_id},
        "guild": {"$eq": guild_id}
    })

    if user_data == None:
        await ctx.respond(f"{member} is not AFK", reply=True)
        return
    
    afk.delete_one({"id": user_id, "guild": guild_id})
    await ctx.respond(f"Cleared AFK status of {member}", reply=True)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)