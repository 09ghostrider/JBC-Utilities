import hikari
import lightbulb
import random
import miru
import pymongo
from pymongo import MongoClient
import datetime

plugin = lightbulb.Plugin("serverconfig")

with open("./secrets/prefix") as f:
    prefix = f.read().strip()

with open("./secrets/db") as f:
    mongoclient = f.read().strip()

@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option("role", "the role to modify perms", required=False, default=None, type=hikari.Role)
@lightbulb.option("command", "the command to view/modify settings", required=True)
@lightbulb.option("option", "add/remove/view", required=True, type=str)
@lightbulb.command("serverconfig", "manage settings and configuration for this guild", aliases=["sc", "serverconf"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _serverconf(ctx: lightbulb.Context) -> None:
    opt = ctx.options.option.lower()
    cmd = ctx.options.command.lower()
    role = ctx.options.role
    guild_id = ctx.event.message.guild_id

    if opt == "add" or opt == "a" or opt == "+":
        option = "add"
    elif opt == "remove" or opt == "r" or opt == "-":
        option = "remove"
    elif opt == "list" or opt == "l" or opt == "settings" or opt == "s" or opt == "show":
        option = "list"
    else:
        await ctx.respond(hikari.Embed(title="Invalid option", description="Available options:\n`add`, `remove`, `list`\nUsage:\n`-serverconf <option> <command> [role]`", color="ff0000"), reply=True)
        return

    if cmd == "afk":
        command = "afk"
    elif cmd == "react" or cmd == "ar":
        command = "ar"
    elif cmd == "donos" or cmd == "donations":
        command = "donations"
    elif cmd == "hl" or cmd == "highlight":
        command = "hl"
    else:
        await ctx.respond(hikari.Embed(title="Invalid command", description="Available commands:\n`afk`, `react`, `donos`, `hl`\nUsage:\n`-serverconf <option> <command> [role]`", color="ff0000"), reply=True)
        return
    
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

        if option == "list":
            if find["req"] == []:
                val1 = "No roles setup"
            else:
                val1 = ""
                for r in find["req"]:
                    val1 = val1 + f"` - ` <@&{r}> \n"
            embed= hikari.Embed(title="Settings for 'AFK'", color=random.randint(0x0, 0xffffff))
            embed.set_thumbnail(ctx.get_guild().icon_url)
            embed.add_field(name="Required Roles", value=val1)
            embed.add_field(name="Required Permissions", value="` - ` Administrator")
            await ctx.respond(embed=embed, reply=True)
            return
        
        elif option == "add":
            if role.id in find["req"]:
                await ctx.resopnd(f"{role.mention} is already in the list", reply=True, role_mentions=False)
                return
            
            find["req"].append(role.id)
            if in_db == True:
                db.update_one({"guild": guild_id}, {"$set": {"req": find["req"]}})
            elif in_db == False:
                db.insert_one(find)
            await ctx.respond(f"Added {role.mention} to list", reply=True, role_mentions=False)
            return
        
        elif option == "remove":
            if role.id not in find["req"]:
                await ctx.resopnd(f"{role.mention} is not in the list", reply=True, role_mentions=False)
                return
            
            find["req"].pop(find["req"].index(role.id))
            if in_db == True:
                db.update_one({"guild": guild_id}, {"$set": {"req": find["req"]}})
            elif in_db == False:
                db.insert_one(find)
            await ctx.respond(f"Removed {role.mention} from list", reply=True, role_mentions=False)
            return
    
    elif command == "ar":
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

        if option == "list":
            if find["req"] == []:
                val1 = "No roles setup"
            else:
                val1 = ""
                for r in find["req"]:
                    val1 = val1 + f"` - ` <@&{r}> \n"
            embed= hikari.Embed(title="Settings for 'react'", color=random.randint(0x0, 0xffffff))
            embed.set_thumbnail(ctx.get_guild().icon_url)
            embed.add_field(name="Required Roles", value=val1)
            embed.add_field(name="Required Permissions", value="` - ` Administrator")
            await ctx.respond(embed=embed, reply=True)
            return
        
        elif option == "add":
            if role.id in find["req"]:
                await ctx.resopnd(f"{role.mention} is already in the list", reply=True, role_mentions=False)
                return
            
            find["req"].append(role.id)
            if in_db == True:
                db.update_one({"guild": guild_id}, {"$set": {"req": find["req"]}})
            elif in_db == False:
                db.insert_one(find)
            await ctx.respond(f"Added {role.mention} to list", reply=True, role_mentions=False)
            return
        
        elif option == "remove":
            if role.id not in find["req"]:
                await ctx.resopnd(f"{role.mention} is not in the list", reply=True, role_mentions=False)
                return
            
            find["req"].pop(find["req"].index(role.id))
            if in_db == True:
                db.update_one({"guild": guild_id}, {"$set": {"req": find["req"]}})
            elif in_db == False:
                db.insert_one(find)
            await ctx.respond(f"Removed {role.mention} from list", reply=True, role_mentions=False)
            return
    
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

        if option == "list":
            if find["req"] == []:
                val1 = "No roles setup"
            else:
                val1 = ""
                for r in find["req"]:
                    val1 = val1 + f"` - ` <@&{r}> \n"
            embed= hikari.Embed(title="Settings for 'donations'", color=random.randint(0x0, 0xffffff))
            embed.set_thumbnail(ctx.get_guild().icon_url)
            embed.add_field(name="Required Roles", value=val1)
            embed.add_field(name="Required Permissions", value="` - ` Administrator")
            await ctx.respond(embed=embed, reply=True)
            return
        
        elif option == "add":
            if role.id in find["req"]:
                await ctx.resopnd(f"{role.mention} is already in the list", reply=True, role_mentions=False)
                return
            
            find["req"].append(role.id)
            if in_db == True:
                db.update_one({"guild": guild_id}, {"$set": {"req": find["req"]}})
            elif in_db == False:
                db.insert_one(find)
            await ctx.respond(f"Added {role.mention} to list", reply=True, role_mentions=False)
            return
        
        elif option == "remove":
            if role.id not in find["req"]:
                await ctx.resopnd(f"{role.mention} is not in the list", reply=True, role_mentions=False)
                return
            
            find["req"].pop(find["req"].index(role.id))
            if in_db == True:
                db.update_one({"guild": guild_id}, {"$set": {"req": find["req"]}})
            elif in_db == False:
                db.insert_one(find)
            await ctx.respond(f"Removed {role.mention} from list", reply=True, role_mentions=False)
            return

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

        if option == "list":
            if find["req"] == []:
                val1 = "No roles setup"
            else:
                val1 = ""
                for r in find["req"]:
                    val1 = val1 + f"` - ` <@&{r}> \n"
            embed= hikari.Embed(title="Settings for 'hl'", color=random.randint(0x0, 0xffffff))
            embed.set_thumbnail(ctx.get_guild().icon_url)
            embed.add_field(name="Required Roles", value=val1)
            embed.add_field(name="Required Permissions", value="` - ` Administrator")
            await ctx.respond(embed=embed, reply=True)
            return
        
        elif option == "add":
            if role.id in find["req"]:
                await ctx.resopnd(f"{role.mention} is already in the list", reply=True, role_mentions=False)
                return
            
            find["req"].append(role.id)
            if in_db == True:
                db.update_one({"guild": guild_id}, {"$set": {"req": find["req"]}})
            elif in_db == False:
                db.insert_one(find)
            await ctx.respond(f"Added {role.mention} to list", reply=True, role_mentions=False)
            return
        
        elif option == "remove":
            if role.id not in find["req"]:
                await ctx.resopnd(f"{role.mention} is not in the list", reply=True, role_mentions=False)
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