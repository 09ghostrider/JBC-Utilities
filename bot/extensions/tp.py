import hikari
import lightbulb
import random
import asyncio
import miru
import datetime
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
import os

plugin = lightbulb.Plugin("teleport")

load_dotenv()
mongoclient = os.getenv("DATABASE")
with open("./secrets/prefix") as f:
    prefix = f.read().strip()

plugin = lightbulb.Plugin("teleport")
plugin.add_checks(lightbulb.guild_only)
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./secrets/prefix") as f:
    prefix = f.read().strip()

@lightbulb.Check
def perms_check(ctx: lightbulb.Context) -> None:
    cluster = MongoClient(mongoclient)
    configs = cluster["tp"]["server_configs"]

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
@lightbulb.add_checks(lightbulb.owner_only| lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | perms_check)
@lightbulb.command("teleport", "quickly teleport to a channel")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def _teleport(ctx: lightbulb.Context) -> None:
    pass

@_teleport.child
@lightbulb.option("channel", "the channel to teleport", required=True, type=hikari.GuildChannel)
@lightbulb.option("name", "the name of the checkpoint", required=True, type=str)
@lightbulb.command("add", "save a new checkpoint", inherit_checks=True, aliases=["a", "+"])
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _add(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    name = ctx.options.name
    channel = ctx.options.channel
    guild_id = ctx.interaction.guild_id
    user_id = ctx.interaction.user.id

    cluster = MongoClient(mongoclient)
    checkpoints = cluster["tp"]["checkpoints"]
    checkpoint = checkpoints.find_one({"guild": {"$eq": guild_id}, "user": {"$eq": user_id}})

    if checkpoint == None:
        checkpoint = {
            "guild": guild_id,
            "user": user_id,
            "points": {
                name: channel.id
            }
        }
        checkpoints.insert_one(checkpoint)
    else:
        if name in checkpoint["points"].keys():
            await ctx.respond(f"Checkpoint **{name}** already exists")
            return
        else:
            checkpoint["points"][name] = channel.id
        checkpoints.update_one({"guild": {"$eq": guild_id}, "user": {"$eq": user_id}}, {"$set": {"points": checkpoint["points"]}})
    
    await ctx.respond(f"Successfully saved checkpoint **{name}**")

@_teleport.child
@lightbulb.option("name", "the name of the checkpoint", required=True, type=str)
@lightbulb.command("remove", "delete a saved checkpoint", inherit_checks=True, aliases=["r", "-"])
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _remove(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    name = ctx.options.name
    guild_id = ctx.interaction.guild_id
    user_id = ctx.interaction.user.id

    cluster = MongoClient(mongoclient)
    checkpoints = cluster["tp"]["checkpoints"]
    checkpoint = checkpoints.find_one({"guild": {"$eq": guild_id}, "user": {"$eq": user_id}})

    if checkpoint == None:
        await ctx.respond(f"You do not have a checkpoint saved as **{name}**")
        return
    else:
        if name in checkpoint["points"].keys():
            del checkpoint["points"][name]
        else:
            await ctx.respond(f"You do not have a checkpoint saved as **{name}**")
            return

    checkpoints.update_one({"guild": {"$eq": guild_id}, "user": {"$eq": user_id}}, {"$set": {"points": checkpoint["points"]}})
    await ctx.respond(f"Successfully deleted checkpoint **{name}**")

@_teleport.child
@lightbulb.command("list", "list your saved checkpoints", inherit_checks=True, aliases=["s", "l", "show"])
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _list(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    guild_id = ctx.interaction.guild_id
    user_id = ctx.interaction.user.id

    cluster = MongoClient(mongoclient)
    checkpoints = cluster["tp"]["checkpoints"]
    checkpoint = checkpoints.find_one({"guild": {"$eq": guild_id}, "user": {"$eq": user_id}})

    if checkpoint == None:
        desc2 = "No checkpoints"
        c = []
    else:
        c = checkpoint["points"]
        if c == {}:
            desc2 = "No checkpoints"
        else:
            desc2 = ""
            for x in c:
                desc2 = desc2 + f"**{x}** : <#{c[x]}>\n"
    
    embed=hikari.Embed(title=f"{ctx.interaction.user}'s checkpoints", color=random.randint(0x0, 0xffffff), description=desc2)
    await ctx.respond(embed=embed, reply=True)

@plugin.command
@lightbulb.add_checks(lightbulb.owner_only| lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | perms_check)
@lightbulb.option("name", "name of the checkpoint", type=str, required=True)
@lightbulb.command("tp", "quickly just to a channel using the saved checkpoints")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _tp(ctx: lightbulb.Context) -> None:
    name = ctx.options.name
    guild_id = ctx.event.message.guild_id
    user_id = ctx.event.message.author.id

    cluster = MongoClient(mongoclient)
    checkpoints = cluster["tp"]["checkpoints"]
    checkpoint = checkpoints.find_one({"guild": {"$eq": guild_id}, "user": {"$eq": user_id}})

    if checkpoint == None:
        await ctx.respond(f"You do not have a checkpoint saved as **{name}**", reply=True)
        return
    else:
        if name not in checkpoint["points"].keys():
            await ctx.respond(f"You do not have a checkpoint saved as **{name}**", reply=True)
            return

    try:
        await ctx.event.message.delete()
    except:
        pass

    await ctx.respond(f"<#{checkpoint['points'][name]}>", delete_after=3)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)