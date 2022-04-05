import hikari
import lightbulb
import random
import miru
import pymongo
from pymongo import MongoClient
import datetime

plugin = lightbulb.Plugin("afk")

with open("./secrets/prefix") as f:
    prefix = f.read().strip()

with open("./secrets/db") as f:
    mongoclient = f.read().strip()

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

@_afk.child
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.MANAGE_CHANNELS))
@lightbulb.option("channel", "The status to set", modifier=lightbulb.commands.base.OptionModifier(3), type=hikari.GuildChannel, required=False, default=None)
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

# @plugin.listener(hikari.MessageCreateEvent)
# async def _on_message(message: hikari.MessageCreateEvent) -> None:
#     if message.is_human == False:
#         return

#     if message.content == None or message.content == "":
#         return
    
#     guild_id = message.message.guild_id
#     channel_id = message.message.channel_id

#     cluster = MongoClient(mongoclient)
#     configs = cluster["afk"]["server_configs"]

#     config = configs.find_one({
#         "guild": guild_id
#     })

#     if config != None:
#         if channel_id in config["ignored"]:
#             return

#     afk = cluster["afk"]["afk"]
#     c = await message.app.rest.fetch_channel(message.message.channel_id)
    
#     user_data = afk.find_one({
#         "id": {"$eq": message.message.author.id},
#         "guild": {"$eq": message.message.guild_id}
#     })
#     if user_data != None:
#         if (round(datetime.datetime.now().timestamp())) - user_data["timestamp"] > 10:
#             afk.delete_one({"id": message.message.author.id, "guild": message.message.guild_id})
#             await c.send(f"Welcome back {message.message.author.mention}, I removed your AFK", user_mentions=True)

#     mentions = message.message.mentions.users
#     if mentions == {}:
#         return
#     for m in mentions.values():
#         user_data = afk.find_one({
#             "id": {"$eq": m.id},
#             "guild": {"$eq": message.message.guild_id}
#         })
#         if user_data != None:
#             s = user_data["status"]
#             t = user_data["timestamp"]
#             await c.send(f"**{m.username}** is AFK: {s} - <t:{t}:R>", user_mentions=True)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)