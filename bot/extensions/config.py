import hikari
import lightbulb
import random
import miru
import pymongo
from pymongo import MongoClient
import datetime

plugin = lightbulb.Plugin("serverconfig")
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./secrets/prefix") as f:
    prefix = f.read().strip()

with open("./secrets/db") as f:
    mongoclient = f.read().strip()

@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command("serverconfig", "manage settings and configuration for this guild", aliases=["sc", "serverconf"])
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def _serverconf(ctx: lightbulb.Context) -> None:
    pass

@_serverconf.child
@lightbulb.option("command", "the command to list permissions for", required=True, choices=["afk", "react", "donations", "hl"])
@lightbulb.command("list", "list the roles that can use the command", aliases=["l", "s", "show"], inherit_checks=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _list(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    command = ctx.options.command
    guild_id = ctx.interaction.guild_id
    
    if command == "afk":
        cluster = MongoClient(mongoclient)
        db = cluster["afk"]["server_configs"]
        find = db.find_one({"guild": {"$eq": guild_id}})
    elif command == "react":
        cluster = MongoClient(mongoclient)
        db = cluster["ar"]["server_configs"]
        find = db.find_one({"guild": {"$eq": guild_id}})
    elif command == "donations":
        cluster = MongoClient(mongoclient)
        db = cluster["donations"]["server_configs"]
        find = db.find_one({"guild": {"$eq": guild_id}})
    elif command == "hl":
        cluster = MongoClient(mongoclient)
        db = cluster["highlights"]["server_configs"]
        find = db.find_one({"guild": {"$eq": guild_id}})
    else:
        await ctx.respond("Unknown command", reply=True, flags=ephemeral)
        return
    
    if find == None:
        val1 = "No roles setup"
    else:
        if find["req"] == []:
            val1 = "No roles setup"
        else:
            val1 = ""
            for r in find["req"]:
                val1 = val1 + f"` - ` <@&{r}> \n"
    embed= hikari.Embed(title=f"Settings for {command}", color=random.randint(0x0, 0xffffff))
    embed.set_thumbnail(ctx.get_guild().icon_url)
    embed.add_field(name="Required Roles", value=val1)
    embed.add_field(name="Required Permissions", value="` - ` Administrator")
    await ctx.respond(embed=embed, reply=True)

@_serverconf.child
@lightbulb.option("role", "the role to add", required=True, type=hikari.Role)
@lightbulb.option("command", "the command to list permissions for", required=True, choices=["afk", "react", "donations", "hl"])
@lightbulb.command("add", "add a role that can use the command", aliases=["a", "+"], inherit_checks=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _list(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    command = ctx.options.command
    guild_id = ctx.interaction.guild_id
    role = ctx.options.role
    
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

    elif command == "react":
        cluster = MongoClient(mongoclient)
        db = cluster["ar"]["server_configs"]
        find = db.find_one({"guild": {"$eq": guild_id}})
        if find == None:
            find = {
                "guild": guild_id,
                "req": []
            }
            in_db = False
        else:
            in_db = True

    elif command == "donations":
        cluster = MongoClient(mongoclient)
        db = cluster["donations"]["server_configs"]
        find = db.find_one({"guild": {"$eq": guild_id}})
        if find == None:
            find = {
                "guild": guild_id,
                "req": []
            }
            in_db = False
        else:
            in_db = True
        
    elif command == "hl":
        cluster = MongoClient(mongoclient)
        db = cluster["highlights"]["server_configs"]
        find = db.find_one({"guild": {"$eq": guild_id}})
        if find == None:
            find = {
                "guild": guild_id,
                "req": []
            }
            in_db = False
        else:
            in_db = True

    else:
        await ctx.respond("Unknown command", reply=True, flags=ephemeral)
        return

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
@lightbulb.option("command", "the command to list permissions for", required=True, choices=["afk", "react", "donations", "hl"])
@lightbulb.command("remove", "remove a role that can use the command", aliases=["a", "+"], inherit_checks=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _list(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    command = ctx.options.command
    guild_id = ctx.interaction.guild_id
    role = ctx.options.role
    
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

    elif command == "react":
        cluster = MongoClient(mongoclient)
        db = cluster["ar"]["server_configs"]
        find = db.find_one({"guild": {"$eq": guild_id}})
        if find == None:
            find = {
                "guild": guild_id,
                "req": []
            }
            in_db = False
        else:
            in_db = True

    elif command == "donations":
        cluster = MongoClient(mongoclient)
        db = cluster["donations"]["server_configs"]
        find = db.find_one({"guild": {"$eq": guild_id}})
        if find == None:
            find = {
                "guild": guild_id,
                "req": []
            }
            in_db = False
        else:
            in_db = True
        
    elif command == "hl":
        cluster = MongoClient(mongoclient)
        db = cluster["highlights"]["server_configs"]
        find = db.find_one({"guild": {"$eq": guild_id}})
        if find == None:
            find = {
                "guild": guild_id,
                "req": []
            }
            in_db = False
        else:
            in_db = True

    else:
        await ctx.respond("Unknown command", reply=True, flags=ephemeral)
        return

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