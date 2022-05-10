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
from bot.utils.checks import botban_check

plugin = lightbulb.Plugin("ar")

load_dotenv()
mongoclient = os.getenv("DATABASE")
with open("./configs/config.json") as f:
    bot_config = json.load(f)

@lightbulb.Check
def perms_check(ctx: lightbulb.Context) -> None:
    cluster = MongoClient(mongoclient)
    configs = cluster["ar"]["server_configs"]

    config = configs.find_one({"guild": ctx.event.message.guild_id})
    if config == None:
        return False
    
    roles = ctx.event.message.member.get_roles()
    for r in config["req"]:
        role = ctx.app.cache.get_role(r)
        if role in roles:
            return True
    return False

@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only| lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | perms_check)
@lightbulb.command("react", "add or remove auto reaction of a member", aliases=["r"])
@lightbulb.implements(lightbulb.PrefixCommandGroup)
async def _ar(ctx: lightbulb.Context) -> None:
    embed=hikari.Embed(title="=== Command Help ===", description="""react - add or remove auto reaction of a member

Usage: -react [subcommand]
    """, color=random.randint(0x0, 0xffffff))
    embed.add_field(name="== Subcommands ==", value="""- remove - remove a ar
- add - add a ar
- list - view a members reactors""")
    await ctx.respond(embed=embed)

@_ar.child
@lightbulb.option("emoji", "the emoji to add", default=str, required=True)
@lightbulb.option("member", "the member to add the reaction for", type=hikari.Member, required=True)
@lightbulb.command("add", "add a ar", inherit_checks=True, aliases=["a", "+"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _add(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    emoji = ctx.options.emoji
    guild_id = ctx.event.message.guild_id

    if member.is_bot == True:
        await ctx.respond("You can only add ars to humans", reply=True)
        return

    try:
        ep = hikari.Emoji.parse(emoji)
        ej = plugin.bot.cache.get_emoji(ep.id)
        if ej == None or ej.guild_id != guild_id:
            await ctx.respond("Unknown Emoji\nNote: The emoji has to be from this guild", reply=True)
            return
    except:
        await ctx.respond("Invalid emoji", reply=True)
        return
    
    cluster = MongoClient(mongoclient)
    reacts = cluster["ar"]["react"]

    react = reacts.find_one({"guild": {"$eq": guild_id}, "member": {"$eq": member.id}})
    if react == None:
        react = {
            "member": member.id,
            "guild": guild_id,
            "react": []
        }
        in_db = False
    else:
        if ej.id in react["react"]:
            await ctx.respond("That emoji is already in their react list", reply=True)
            return
        in_db = True
    
    react["react"].append(ej.id)
    if in_db == True:
        reacts.update_one({"guild": {"$eq": guild_id}, "member": {"$eq": member.id}}, {"$set": {"react": react["react"]}})
    else:
        reacts.insert_one(react)

    await ctx.respond(f"Added {ej.mention} to {member.mention}'s reacts", reply=True, user_mentions=False)

@_ar.child
@lightbulb.option("emoji", "the emoji to add", default=str, required=True)
@lightbulb.option("member", "the member to add the reaction for", type=hikari.Member, required=True)
@lightbulb.command("remove", "remove a ar", inherit_checks=True, aliases=["r", "-"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _remove(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    emoji = ctx.options.emoji
    guild_id = ctx.event.message.guild_id

    if member.is_bot == True:
        await ctx.respond("You can only remove ars from humans", reply=True)
        return

    try:
        ep = hikari.Emoji.parse(emoji)
        ej = plugin.bot.cache.get_emoji(ep.id)
        if ej == None or ej.guild_id != guild_id:
            await ctx.respond("Unknown Emoji\nNote: The emoji has to be from this guild", reply=True)
            return
    except:
        await ctx.respond("Invalid emoji", reply=True)
        return
    
    cluster = MongoClient(mongoclient)
    reacts = cluster["ar"]["react"]

    react = reacts.find_one({"guild": {"$eq": guild_id}, "member": {"$eq": member.id}})
    if react == None:
        react = {
            "member": member.id,
            "guild": guild_id,
            "react": []
        }
        in_db = False
    else:
        if ej.id not in react["react"]:
            await ctx.respond("That emoji is not in their react list", reply=True)
            return
        in_db = True
    
    react["react"].pop(react["react"].index(ej.id))
    if in_db == True:
        reacts.update_one({"guild": {"$eq": guild_id}, "member": {"$eq": member.id}}, {"$set": {"react": react["react"]}})
    else:
        reacts.insert_one(react)

    await ctx.respond(f"Removed {ej.mention} from {member.mention}'s reacts", reply=True, user_mentions=False)

@_ar.child
@lightbulb.option("member", "the member to add the reaction for", type=hikari.Member, required=True)
@lightbulb.command("list", "view a members reactors", inherit_checks=True, aliases=["l", "show", "s"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _list(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    reacts = cluster["ar"]["react"]
    react = reacts.find_one({"guild": {"$eq": guild_id}, "member": {"$eq": member.id}})

    if react == None:
        desc2 = "No reacts"
        e = []
    else:
        e = react["react"]
        if e == []:
            desc2 = "No reacts"
        else:
            desc2 = ""
            for x in e:
                emoji = await ctx.app.rest.fetch_emoji(guild_id, x)
                desc2 = desc2 + f"` - ` {emoji.mention}\n"
    
    embed=hikari.Embed(title=f"{member.username}'s reacts", color=bot_config["color"]["default"], description=f"Total Reacts: {len(e)}")
    embed.set_thumbnail(member.avatar_url)
    embed.set_footer(text=f"{member} ({member.id})", icon=member.avatar_url)
    embed.add_field(name="Reacts", value=desc2)
    await ctx.respond(embed=embed, reply=True)

@plugin.listener(hikari.MessageCreateEvent)
async def _on_message(message: hikari.MessageCreateEvent) -> None:
    if message.is_human == False:
        return
    
    guild_id = message.message.guild_id
    mentions = message.message.mentions.users
    reference = message.message.referenced_message
    if mentions == {}:
        return

    cluster = MongoClient(mongoclient)
    reacts = cluster["ar"]["react"]

    counter = 0
    while True:
        try:
            member_id = list(mentions.items())[counter][0]
        except:
            return
        
        if reference != None:
            if member_id == reference.author.id:
                try:
                    member_id = list(mentions.items())[counter+1][0]
                except:
                    return

        react = reacts.find_one({"guild": {"$eq": guild_id}, "member": {"$eq": member_id}})
        if react != None:
            e = react["react"]
            if e != []:
                for x in e:
                    emoji = await message.app.rest.fetch_emoji(guild_id, x)
                    try:
                        await message.message.add_reaction(emoji)
                    except:
                        pass
            return

        else:
            counter += 1

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)