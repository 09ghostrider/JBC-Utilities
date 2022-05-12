import hikari
import lightbulb
import random
import miru
import pymongo
from pymongo import MongoClient
import datetime
import os
import json
from dotenv import load_dotenv
from bot.utils.checks import botban_check

plugin = lightbulb.Plugin("serverconfig")
plugin.add_checks(botban_check)
ephemeral = hikari.MessageFlag.EPHEMERAL

load_dotenv()
mongoclient = os.getenv("DATABASE")
with open("./configs/config.json") as f:
    bot_config = json.load(f)

def config_find(command:str, guild_id:int):
    if command == "afk":
        cluster = MongoClient(mongoclient)
        db = cluster["afk"]["server_configs"]
        find = db.find_one({"guild": {"$eq": guild_id}})
        if find == None:
            find = {
                "guild": guild_id,
                "ignored": [],
                "req": []
            }
            in_db = False
        else:
            in_db = True

    else:
        if command == "react":
            cluster = MongoClient(mongoclient)
            db = cluster["ar"]["server_configs"]
            find = db.find_one({"guild": {"$eq": guild_id}})
            

        elif command == "donations":
            cluster = MongoClient(mongoclient)
            db = cluster["donations"]["server_configs"]
            find = db.find_one({"guild": {"$eq": guild_id}})
            
            
        elif command == "highlight":
            cluster = MongoClient(mongoclient)
            db = cluster["highlight"]["server_configs"]
            find = db.find_one({"guild": {"$eq": guild_id}})
            
        
        elif command == "teleport":
            cluster = MongoClient(mongoclient)
            db = cluster["tp"]["server_configs"]
            find = db.find_one({"guild": {"$eq": guild_id}})
        
        elif command == "snipe":
            cluster = MongoClient(mongoclient)
            db = cluster["snipe"]["server_configs"]
            find = db.find_one({"guild": {"$eq": guild_id}})
        
        if find == None:
            find = {
                "guild": guild_id,
                "req": []
            }
            in_db = False
        else:
            in_db = True
        
    return find, db, in_db

@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command("serverconfig", "manage settings and configuration for this guild", aliases=["sc", "serverconf"])
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def _serverconf(ctx: lightbulb.Context) -> None:
    pass

@_serverconf.child
@lightbulb.option("command", "the command to list permissions for", required=True, choices=["afk", "react", "donations", "highlight", "teleport", "snipe"])
@lightbulb.command("list", "list the roles that can use the command", aliases=["l", "s", "show"], inherit_checks=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _list(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    command = ctx.options.command
    guild_id = ctx.interaction.guild_id
    
    find, db, in_db = config_find(command, guild_id)
    
    if find["req"] == []:
        val1 = "No roles setup"
    else:
        val1 = ""
        for r in find["req"]:
            val1 = val1 + f"{bot_config['emoji']['blue_arrow']} <@&{r}> \n"
    embed= hikari.Embed(title=f"Settings for {command}", color=bot_config["color"]["default"])
    embed.set_thumbnail(ctx.get_guild().icon_url)
    embed.add_field(name="Required Roles", value=val1)
    embed.add_field(name="Required Permissions", value=f"{bot_config['emoji']['blue_arrow']} Administrator")
    await ctx.respond(embed=embed, reply=True)

@_serverconf.child
@lightbulb.option("role", "the role to add", required=True, type=hikari.Role)
@lightbulb.option("command", "the command to list permissions for", required=True, choices=["afk", "react", "donations", "highlight", "teleport", "snipe"])
@lightbulb.command("add", "add a role that can use the command", aliases=["a", "+"], inherit_checks=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _list(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    command = ctx.options.command
    guild_id = ctx.interaction.guild_id
    role = ctx.options.role
    
    find, db, in_db = config_find(command, guild_id)

    if role.id in find["req"]:
        await ctx.resopnd(f"{role.mention} is already in the list", reply=True, role_mentions=False, flags=ephemeral)
        return
    
    find["req"].append(role.id)
    if in_db == True:
        db.update_one({"guild": guild_id}, {"$set": {"req": find["req"]}})
    elif in_db == False:
        db.insert_one(find)
    await ctx.respond(f"Added {role.mention} to list", reply=True, role_mentions=False)

@_serverconf.child
@lightbulb.option("role", "the role to remove", required=True, type=hikari.Role)
@lightbulb.option("command", "the command to list permissions for", required=True, choices=["afk", "react", "donations", "highlight", "teleport", "snipe"])
@lightbulb.command("remove", "remove a role that can use the command", aliases=["a", "+"], inherit_checks=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _list(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    command = ctx.options.command
    guild_id = ctx.interaction.guild_id
    role = ctx.options.role
    
    find, db, in_db = config_find(command, guild_id)

    if role.id not in find["req"]:
        await ctx.respond(f"{role.mention} is not in the list", reply=True, role_mentions=False, flags=ephemeral)
        return
    
    find["req"].pop(find["req"].index(role.id))
    if in_db == True:
        db.update_one({"guild": guild_id}, {"$set": {"req": find["req"]}})
    elif in_db == False:
        db.insert_one(find)
    await ctx.respond(f"Removed {role.mention} from list", reply=True, role_mentions=False)
    return

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)