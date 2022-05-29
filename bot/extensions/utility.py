import hikari
import lightbulb
import random
import asyncio
import miru
import json
import os
import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from bot.utils.checks import botban_check
from miru.ext import nav

plugin = lightbulb.Plugin("utility")
plugin.add_checks(botban_check)
ephemeral = hikari.MessageFlag.EPHEMERAL

load_dotenv()
mongoclient = os.getenv("DATABASE")
with open("./configs/config.json") as f:
    bot_config = json.load(f)

@plugin.command()
@lightbulb.option("member", "the member to show", type=hikari.Member, required=False, default=None)
@lightbulb.command("avatar", "shows the members display avatar", aliases=["av"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _av(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    if member == None:
        member = ctx.event.message.member
    
    embed = hikari.Embed(color=bot_config['color']['default'], title=f"{member}'s avatar")
    embed.set_image(member.display_avatar_url)
    await ctx.respond(embed=embed, reply=True)

@plugin.command()
@lightbulb.option("user", "the user to show", type=hikari.User, required=False, default=None)
@lightbulb.command("banner", "shows the users banner")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _banner(ctx: lightbulb.Context) -> None:
    user = ctx.options.user
    if not user:
        user = ctx.event.message.author
    
    user = await ctx.app.rest.fetch_user(user.id)
    embed = hikari.Embed(color=bot_config['color']['default'], title=f"{user}'s banner")
    if user.banner_url != None:
        embed.set_image(user.banner_url)
    else:
        embed.description = "No banner set"
    await ctx.respond(embed=embed, reply=True)

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.MANAGE_GUILD))
@lightbulb.option("text", "the embed content", required=True, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.option("channel", "the channel to send the embed in", type=hikari.GuildChannel, required=False, default=None)
@lightbulb.command("embed", "Creates an embed with the specified color in the specified channel, separate the title from the description with |")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _embed(ctx: lightbulb.Context) -> None:
    channel = ctx.options.channel
    text = ctx.options.text

    if not channel:
        cid = ctx.event.message.channel_id
    else:
        cid = channel.id
    
    try:
        title, description = text.split("|", 1)

        embed = hikari.Embed(title=title, description=description, color=bot_config['color']['default'])
        await ctx.app.rest.create_message(cid, embed=embed)
        await ctx.event.message.add_reaction("✅")
    except:
        await ctx.event.message.add_reaction("❌")

@lightbulb.Check
def afk_perms_check(ctx: lightbulb.Context) -> None:
    cluster = MongoClient(mongoclient)
    configs = cluster["afk"]["server_configs"]

    config = configs.find_one({"guild": ctx.event.message.guild_id})
    if config == None:
        return False
    
    for r in config["req"]:
        role = ctx.app.cache.get_role(r)
        roles = ctx.event.message.member.get_roles()
        if role in roles:
            return True
    return False

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | afk_perms_check)
@lightbulb.option("status", "The status to set", modifier=lightbulb.commands.base.OptionModifier(3), type=str, default="AFK", required=False)
@lightbulb.command("afk", "Set an AFK status shown when you're mentioned, and display in nickname.")
@lightbulb.implements(lightbulb.PrefixCommandGroup)
async def _afk(ctx: lightbulb.Context) -> None:
    status = ctx.options.status
    user_id = ctx.event.message.author.id
    guild_id = ctx.event.message.guild_id
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

    afk.insert_one(user_data)
    await ctx.respond(f"{ctx.event.message.author.mention}: I set your AFK: {status}", role_mentions=False, user_mentions=True)

    try:
        nick = ctx.event.message.member.nickname
        if nick == None:
            nick = ctx.event.message.author.username
        else:
            if nick.startswith("[AFK] "):
                return
        await ctx.event.message.member.edit(nick=f"[AFK] {nick}", reason="Member went AFK")
    except:
        pass

@_afk.child
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | afk_perms_check)
@lightbulb.option("status", "The status to set", modifier=lightbulb.commands.base.OptionModifier(3), type=str, default="AFK", required=False)
@lightbulb.command("set", "Set an AFK status shown when you're mentioned, and display in nickname.", inherit_checks=True, aliases=["s"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _set(ctx: lightbulb.Context) -> None:
    status = ctx.options.status
    user_id = ctx.event.message.author.id
    guild_id = ctx.event.message.guild_id
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

    afk.insert_one(user_data)
    await ctx.respond(f"{ctx.event.message.author.mention}: I set your AFK: {status}", role_mentions=False, user_mentions=True)

    try:
        nick = ctx.event.message.member.nickname
        if nick == None:
            nick = ctx.event.message.author.username
        await ctx.event.message.member.edit(nick=f"[AFK] {nick}", reason="Member went AFK")
    except:
        pass


@_afk.child
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.MANAGE_CHANNELS))
@lightbulb.option("channel", "The channel to ignore", modifier=lightbulb.commands.base.OptionModifier(3), type=hikari.GuildChannel, required=False, default=None)
@lightbulb.command("ignore", "Use in a channel to not return from AFK when talking in that channel.", inherit_checks=False)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _ignore(ctx: lightbulb.Context) -> None:
    c = ctx.options.channel
    if c == None:
        channel = ctx.event.message.channel_id
    else:
        channel = c.id
    guild_id = ctx.event.message.guild_id

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
        await ctx.respond(f"Removed <#{channel}> from AFK ignored list", reply=True)
    else:
        config["ignored"].append(channel)
        await ctx.respond(f"Added <#{channel}> to AFK ignored list", reply=True)
    
    if in_db == True:
        configs.update_one({"guild": guild_id}, {"$set":{"ignored": config["ignored"]}})
    else:
        configs.insert_one(config)

@_afk.child
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.MANAGE_CHANNELS))
@lightbulb.command("ignored", "List all the AFK ignored channels", inherit_checks=False)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _ignored(ctx: lightbulb.Context) -> None:
    guild_id = ctx.event.message.guild_id
    cluster = MongoClient(mongoclient)
    configs = cluster["afk"]["server_configs"]

    config = configs.find_one({
        "guild": guild_id
    })

    embed = hikari.Embed(color=bot_config["color"]["default"], title="AFK ignored channels")

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
@lightbulb.command("clear", "Remove the AFK status of a member.", inherit_checks=False)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _clear(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    user_id = member.id
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    afk = cluster["afk"]["afk"]

    user_data = afk.find_one({
        "id": {"$eq": user_id},
        "guild": {"$eq": guild_id}
    })

    if user_data == None:
        return await ctx.respond(f"{member} is not AFK", reply=True)
    
    afk.delete_one({"_id": user_id, "guild": guild_id})
    await ctx.respond(f"Cleared AFK status of {member}", reply=True)

@plugin.listener(hikari.MessageCreateEvent)
async def _on_message(message: hikari.MessageCreateEvent) -> None:
    if message.is_human == False:
        return

    if message.content == None or message.content == "":
        return
    
    guild_id = message.message.guild_id
    channel_id = message.message.channel_id

    cluster = MongoClient(mongoclient)
    configs = cluster["afk"]["server_configs"]

    config = configs.find_one({
        "guild": guild_id
    })

    if config != None:
        if channel_id in config["ignored"]:
            return

    afk = cluster["afk"]["afk"]
    user_data = afk.find_one({
        "id": {"$eq": message.message.author.id},
        "guild": {"$eq": message.message.guild_id}
    })
    c = await message.app.rest.fetch_channel(message.message.channel_id)
    if user_data != None:
        if (round(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())) - user_data["timestamp"] > 30:
            afk.delete_one({"id": message.message.author.id, "guild": message.message.guild_id})
            await c.send(f"Welcome back {message.message.author.mention}, I removed your AFK", user_mentions=True)

            try:
                nick = message.message.member.nickname
                if nick != None:
                    if nick.startswith("[AFK] "):
                        nick = nick[6:]
                    else:
                        return
                    await message.message.member.edit(nick=nick, reason="Member returned from being AFK")
            except:
                pass

    mentions = message.message.mentions.users
    if mentions == {}:
        return
    for m in mentions.values():
        user_data = afk.find_one({
            "id": {"$eq": m.id},
            "guild": {"$eq": message.message.guild_id}
        })
        if user_data != None:
            s = user_data["status"]
            t = user_data["timestamp"]
            await c.send(f"**{m.username}** is AFK: {s} - <t:{t}:R>", user_mentions=True)

@lightbulb.Check
def ar_perms_check(ctx: lightbulb.Context) -> None:
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
@lightbulb.add_checks(lightbulb.owner_only| lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | ar_perms_check)
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

# @plugin.listener(hikari.MessageCreateEvent)
# async def _on_message(message: hikari.MessageCreateEvent) -> None:
#     if message.is_human == False:
#         return
    
#     guild_id = message.message.guild_id
#     mentions = message.message.mentions.users
#     reference = message.message.referenced_message
#     if mentions == {}:
#         return

#     cluster = MongoClient(mongoclient)
#     reacts = cluster["ar"]["react"]

#     counter = 0
#     while True:
#         try:
#             member_id = list(mentions.items())[counter][0]
#         except:
#             return
        
#         if reference != None:
#             if member_id == reference.author.id:
#                 try:
#                     member_id = list(mentions.items())[counter+1][0]
#                 except:
#                     return

#         react = reacts.find_one({"guild": {"$eq": guild_id}, "member": {"$eq": member_id}})
#         if react != None:
#             e = react["react"]
#             if e != []:
#                 for x in e:
#                     emoji = await message.app.rest.fetch_emoji(guild_id, x)
#                     try:
#                         await message.message.add_reaction(emoji)
#                     except:
#                         pass
#             return

#         else:
#             counter += 1

@plugin.listener(hikari.MessageCreateEvent)
async def _on_message(message: hikari.MessageCreateEvent) -> None:
    if message.is_human == False:
        return
    
    guild_id = message.message.guild_id
    mentions = message.message.mentions.users
    
    if mentions == {}:
        return

    cluster = MongoClient(mongoclient)
    reacts = cluster["ar"]["react"]

    react = reacts.find_one({"guild": guild_id, "member": int((list(mentions.items())[0][1]).id)})
    if react != None:
        e = react["react"]
        if e != []:
            for x in e:
                emoji = await message.app.rest.fetch_emoji(guild_id, x)
                try:
                    await message.message.add_reaction(emoji)
                except:
                    pass

# @lightbulb.Check
# def hl_perms_check(ctx: lightbulb.Context) -> None:
#     cluster = MongoClient(mongoclient)
#     configs = cluster["highlight"]["server_configs"]

#     config = configs.find_one({"guild": ctx.event.message.guild_id})
#     if config == None:
#         return False
    
#     roles = ctx.event.message.member.get_roles()
#     for r in config["req"]:
#         role = ctx.app.cache.get_role(r)
#         if role in roles:
#             return True
#     return False

# @plugin.command()
# @lightbulb.add_checks(lightbulb.guild_only)
# @lightbulb.add_checks(lightbulb.owner_only| lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | hl_perms_check)
# @lightbulb.command("highlight", "Highlighting means you will receive a message when your keyword is said in chat.", aliases=["hl"])
# @lightbulb.implements(lightbulb.PrefixCommandGroup)
# async def _hl(ctx: lightbulb.Context) -> None:
#     embed=hikari.Embed(title="=== Command Help ===", description="""highlight - Highlighting means you will receive a message when your keyword is said in chat. It will only notify you if you haven't posted anything in chat for the past 5 minutes.

#     Usage: -highlight [subcommand]
#     """, color=bot_config["color"]["default"])
#     embed.add_field(name="== Subcommands ==", value="""- add - add a word to your highlights list
#     - remove - remove a word from your highlight list
#     - list - show your current highlight list
#     - block - block a channel or member from triggering your highlights
#     - unblock - unblock a blocked channel or member
#     - clear - clear all your highlights""")
#     await ctx.respond(embed=embed)

# @_hl.child
# @lightbulb.option("word", "the word to start tracking", type=str)
# @lightbulb.command("add", "add a word to your highlights list", inherit_checks=True, aliases=["+", "a"])
# @lightbulb.implements(lightbulb.PrefixSubCommand)
# async def _add(ctx: lightbulb.Context) -> None:
#     word = ctx.options.word
#     word = word.lower()
#     user_id = ctx.event.message.author.id

#     if "@everyone" in word or "@here" in word:
#         await ctx.respond("You cant highlight `@everyone` and `@here`", reply=True)
#         return
#     if len(word) < 2:
#         await ctx.respond("Word needs to be at least 2 characters long", reply=True)
#         return
#     if len(word) > 50:
#         await ctx.respond("Words can only be upto 50 characters", reply=True)
#         return
    
#     cluster = MongoClient(mongoclient)
#     highlight = cluster["highlight"]["highlight"]

#     user_data = highlight.find_one({
#         "_id": {"$eq": user_id}
#     })
    
#     if user_data is None:
#         in_db = False
#         user_data = {
#             "_id": user_id,
#             "hl": [],
#             "block_channel": [],
#             "block_member": []
#         }

#     else:
#         in_db = True
#         hl_count = len(user_data["hl"])
#         if hl_count >= 10:
#             await ctx.respond("You can only have 10 highlights", reply=True)
#             return
#         hl_list = user_data["hl"]
        
#         if word in hl_list:
#             await ctx.respond("That word is already in your highlight list", reply=True)
#             return
#         user_data["hl"].append(word)
#     if in_db == False:
#         highlight.insert_one(user_data)
#     elif in_db == True:
#         highlight.update_one({"_id":user_id}, {"$set":{"hl":user_data["hl"]}})
#     await ctx.respond(f"""Successfully add "{word}" to your highlights list""", reply=True)

# @_hl.child
# @lightbulb.option("word", "the word to stop tracking", type=str)
# @lightbulb.command("remove", "remove a word from your highlight list", inherit_checks=True, aliases=["-", "r"])
# @lightbulb.implements(lightbulb.PrefixSubCommand)
# async def _remove(ctx: lightbulb.Context) -> None:
#     word = ctx.options.word
#     word = word.lower()
#     user_id = ctx.event.message.author.id
    
#     cluster = MongoClient(mongoclient)
#     highlight = cluster["highlight"]["highlight"]

#     user_data = highlight.find_one({
#         "_id": {"$eq": user_id}
#     })
#     if user_data == None:
#         await ctx.respond(f"You are not tracking any words", reply=True)
#         return
    
#     hl_list = user_data["hl"]
#     if word not in hl_list:
#         await ctx.respond("You are not tracking that word", reply=True)
#         return
    
#     hl_list.pop(hl_list.index(word))
#     highlight.update_one({"_id":user_id}, {"$set":{"hl":hl_list}})
#     await ctx.respond(f"""Successfully remove "{word}" from your highlights list""", reply=True)

# @_hl.child
# @lightbulb.command("list", "show your current highlight list", inherit_checks=True, aliases=["show", "l"])
# @lightbulb.implements(lightbulb.PrefixSubCommand)
# async def _list(ctx: lightbulb.Context) -> None:
#     user_id = ctx.event.message.author.id

#     cluster = MongoClient(mongoclient)
#     highlight = cluster["highlight"]["highlight"]

#     user_data = highlight.find_one({
#         "_id": {"$eq": user_id}
#     })
    
#     if user_data is None:
#         user_data = {
#             "_id": user_id,
#             "hl": [],
#             "block_channel": [],
#             "block_member": []
#         }

#     if user_data["hl"] == []:
#         await ctx.respond("You are not tracking anything", reply=True)
#         return

#     hl_str = ""
#     for x in user_data["hl"]:
#         hl_str = hl_str + x + "\n"
#     embed = hikari.Embed(title="You're currently tracking the following words", description=f"{hl_str}" ,color=bot_config["color"]["default"])
    
#     if user_data["block_channel"] != []:
#         channel_str = ""
#         for c in user_data["block_channel"]:
#             channel_str = channel_str + f"<#{c}>\n"
#         embed.add_field(name="Ignored Channels", value=channel_str, inline=True)
    
#     if user_data["block_member"] != []:
#         member_str = ""
#         for c in user_data["block_member"]:
#             member_str = member_str + f"<@!{c}>\n"
#         embed.add_field(name="Ignored Members", value=member_str, inline=True)
    
#     await ctx.respond(embed=embed, reply=True)

# @_hl.child
# @lightbulb.option("blocks", "the member or channel to block", type=str)
# @lightbulb.command("block", "block a channel or member from triggering your highlights", inherit_checks=True, aliases=["b"])
# @lightbulb.implements(lightbulb.PrefixSubCommand)
# async def _block(ctx: lightbulb.Context) -> None:
#     blocks = ctx.options.blocks
#     channel = None
#     member = None
#     try:
#         channel = ctx.get_guild().get_channel(blocks)
#     except:
#         pass
#     if channel == None:
#         try:
#             member = await ctx.bot.rest.fetch_member(ctx.guild_id, blocks)
#         except:
#             pass
    
#     if member == None and channel == None:
#         if blocks.startswith("<#") and blocks.endswith(">"):
#             try:
#                 c = int(blocks[2:][:-1])
#                 channel = ctx.get_guild().get_channel(c)
#             except:
#                 pass
#         elif blocks.startswith("<@!") and blocks.endswith(">") and channel == None:
#             try:
#                 m = int(blocks[3:][:-1])
#                 member = await ctx.bot.rest.fetch_member(ctx.guild_id, m)
#             except:
#                 pass
#         elif blocks.startswith("<@") and blocks.endswith(">") and channel == None:
#             try:
#                 m = int(blocks[2:][:-1])
#                 member = await ctx.bot.rest.fetch_member(ctx.guild_id, m)
#             except:
#                 pass
#         else:
#             await ctx.respond("Unknown channel or member", reply=True)
#             return
    
#     if channel == None and member == None:
#         await ctx.respond("Unknown channel or member", reply=True)
#         return
    
#     cluster = MongoClient(mongoclient)
#     highlight = cluster["highlight"]["highlight"]
#     user_id = ctx.author.id

#     user_data = highlight.find_one({
#         "_id": {"$eq": user_id}
#     })
    
#     if user_data is None:
#         user_data = {
#             "_id": user_id,
#             "hl": [],
#             "channel": [],
#             "member": []
#         }
    
#     if channel != None:
#         if channel.id not in user_data["block_channel"]:
#             user_data["block_channel"].append(channel.id)
#             await ctx.respond(f"Successfuly blocked {channel.mention}", reply=True)
#             highlight.update_one({"_id":user_id}, {"$set":{"block_channel":user_data["block_channel"]}})
#         else:
#             await ctx.respond("That channel is already blocked", reply=True)
#             return
#     elif member != None:
#         if member.id == ctx.author.id:
#             await ctx.respond("You dont need to block yourself, you cant trigger your own highlights", reply=True)
#             return
#         if member.is_bot == True:
#             await ctx.respond("You dont need to block bots, they cant trigger your highlights", reply=True)
#             return
#         if member.id not in user_data["block_member"]:
#             user_data["block_member"].append(member.id)
#             await ctx.respond(f"Successfuly blocked {member.mention}", user_mentions=False, reply=True)
#             highlight.update_one({"_id":user_id}, {"$set":{"block_member":user_data["block_member"]}})
#         else:
#             await ctx.respond("That member is already blocked", reply=True)
#             return

# @_hl.child
# @lightbulb.option("blocks", "the member or channel to unblock", type=str)
# @lightbulb.command("unblock", "unblock a blocked channel or member", inherit_checks=True, aliases=["unb"])
# @lightbulb.implements(lightbulb.PrefixSubCommand)
# async def _unblock(ctx: lightbulb.Context) -> None:
#     blocks = ctx.options.blocks
#     channel = None
#     member = None
#     try:
#         channel = ctx.get_guild().get_channel(blocks)
#     except:
#         pass
#     if channel == None:
#         try:
#             member = await ctx.bot.rest.fetch_member(ctx.guild_id, blocks)
#         except:
#             pass
    
#     if member == None and channel == None:
#         if blocks.startswith("<#") and blocks.endswith(">"):
#             try:
#                 c = int(blocks[2:][:-1])
#                 channel = ctx.get_guild().get_channel(c)
#             except:
#                 pass
#         elif blocks.startswith("<@!") and blocks.endswith(">") and channel == None:
#             try:
#                 m = int(blocks[3:][:-1])
#                 member = await ctx.bot.rest.fetch_member(ctx.guild_id, m)
#             except:
#                 pass
#         elif blocks.startswith("<@") and blocks.endswith(">") and channel == None:
#             try:
#                 m = int(blocks[2:][:-1])
#                 member = await ctx.bot.rest.fetch_member(ctx.guild_id, m)
#             except:
#                 pass
#         else:
#             await ctx.respond("That is not in your block list", reply=True)
#             return
    
#     if channel == None and member == None:
#         await ctx.respond("That is not in your block list", reply=True)
#         return
    
#     cluster = MongoClient(mongoclient)
#     highlight = cluster["highlight"]["highlight"]
#     user_id = ctx.author.id

#     user_data = highlight.find_one({
#         "_id": {"$eq": user_id}
#     })
    
#     if user_data is None:
#         user_data = {
#             "_id": user_id,
#             "hl": [],
#             "block_channel": [],
#             "block_member": []
#         }
    
#     if channel != None:
#         if channel.id in user_data["block_channel"]:
#             user_data["block_channel"].pop(user_data["block_channel"].index(channel.id))
#             await ctx.respond(f"Successfuly unblocked {channel.mention}", reply=True)
#             highlight.update_one({"_id":user_id}, {"$set":{"block_channel":user_data["block_channel"]}})
#         else:
#             await ctx.respond("That channel is not blocked", reply=True)
#             return
#     elif member != None:
#         if member.id == ctx.author.id:
#             await ctx.respond("That is not in your block list", reply=True)
#             return
#         if member.id in user_data["block_member"]:
#             user_data["block_member"].pop(user_data["block_member"].index(member.id))
#             await ctx.respond(f"Successfuly unblocked {member.mention}", user_mentions=False, reply=True)
#             highlight.update_one({"_id":user_id}, {"$set":{"block_member":user_data["block_member"]}})
#         else:
#             await ctx.respond("That member is not blocked", reply=True)
#             return

# @_hl.child
# @lightbulb.command("clear", "clear all your highlights", inherit_checks=True, aliases=["c"])
# @lightbulb.implements(lightbulb.PrefixSubCommand)
# async def _clear(ctx: lightbulb.Context) -> None:
#     cluster = MongoClient(mongoclient)
#     highlight = cluster["highlight"]["highlight"]
#     user_id = ctx.event.message.author.id

#     user_data = highlight.find_one({
#         "_id": {"$eq": user_id}
#     })

#     if user_data == None:
#         await ctx.respond("You are not tracking anything", reply=True)
#         return
    
#     else:
#         try:
#             highlight.update_one({"_id":user_id}, {"$set": {"hl": []}})
#         except Exception as e:
#             await ctx.respond("There was a error", reply=True)
#             raise e
#         await ctx.respond("Cleared all your highlights", reply=True)

# last_seen = {}

# @plugin.listener(hikari.MessageCreateEvent)
# async def _on_message(message: hikari.MessageCreateEvent) -> None:
#     if message.is_human == False:
#         return

#     if message.content == None or message.content == "":
#         return
    
#     user_id = message.author.id

#     global last_seen
    
#     while True:
#         try:
#             last_seen[str(message.message.guild_id)][str(message.message.channel_id)][str(user_id)] = datetime.datetime.now()
#             break
#         except KeyError:
#             try:
#                 dummy1 = last_seen[str(message.message.guild_id)]
#             except KeyError:
#                 last_seen[str(message.message.guild_id)] = {}
#             try:
#                 dummy2 =last_seen[str(message.message.guild_id)][str(message.message.channel_id)]
#             except KeyError:
#                 last_seen[str(message.message.guild_id)][str(message.message.channel_id)] = {}
    
#     cluster = MongoClient(mongoclient)
#     highlight = cluster["highlight"]["highlight"]

#     words = (message.content).split(" ")
#     dmed_users = []

#     channel = await message.message.app.rest.fetch_channel(message.message.channel_id)
#     t = (message.message.created_at) + datetime.timedelta(0,1)
#     history = await channel.fetch_history(before=t).limit(5)
#     description = ""

#     for h in reversed(history):
#         try:
#             if len(h.content) > 200:
#                 hc = h.content[:200]
#             else:
#                 hc = h.content
#         except:
#             hc = ""
#         description = description + "\n" + f"**[<t:{round(h.created_at.timestamp())}:T>] {h.author.username}:** {hc}"

#     matches = highlight.find(
#             {"_id": {"$ne": user_id}}
#         )

#     for word in words:
#         if matches is not None:
#             for match in matches:
#                 try:
#                     member = await message.message.app.rest.fetch_member(message.message.guild_id, int(match["_id"]))
#                     if member:
#                         if word.lower() in match["hl"]:
#                             if user_id not in match["block_member"] and message.message.channel_id not in match["block_channel"]:
#                                 try:
#                                     perms = lightbulb.utils.permissions_in(channel, member)
#                                     if hikari.Permissions.VIEW_CHANNEL in perms:
#                                         if int(match["_id"]) not in dmed_users:
#                                             last_seen_check = False
#                                             try:
#                                                 local_last_seen = last_seen[str(message.message.guild_id)][str(message.message.channel_id)][str(match["_id"])]
#                                                 if (datetime.datetime.now() - local_last_seen).total_seconds() > 300:
#                                                     last_seen_check = True
#                                             except KeyError:
#                                                 last_seen_check = True
#                                             if last_seen_check == True:
#                                                 embed=hikari.Embed(title=word, description=description, color=random.randint(0x0, 0xffffff))
#                                                 view = miru.View()
#                                                 view.add_item(miru.Button(label="Message", url=f"https://discord.com/channels/{message.message.guild_id}/{message.message.channel_id}/{message.message.id}"))
#                                                 content = f"""In **{(await message.message.app.rest.fetch_guild(message.message.guild_id)).name}** {channel.mention}, you were mentioned with highlight word "{word}" """
#                                                 try:
#                                                     userdm = await member.user.fetch_dm_channel()
#                                                     await userdm.send(content, embed=embed, components=view.build())
#                                                     dmed_users.append(int(match["_id"]))
#                                                 except:
#                                                     pass
#                                 except:
#                                     pass
#                 except:
#                     pass

@lightbulb.Check
def tp_perms_check(ctx: lightbulb.Context) -> None:
    cluster = MongoClient(mongoclient)
    configs = cluster["tp"]["server_configs"]

    config = configs.find_one({"guild": ctx.event.message.guild_id})
    if config == None:
        return False
    
    for r in config["req"]:
        role = ctx.app.cache.get_role(r)
        roles = ctx.event.message.member.get_roles()
        if role in roles:
            return True
    return False

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only| lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | tp_perms_check)
@lightbulb.option("name", "name of the checkpoint", type=str, required=True)
@lightbulb.command("teleport", "quickly teleport to a channel", aliases=["tp"])
@lightbulb.implements(lightbulb.PrefixCommandGroup)
async def _teleport(ctx: lightbulb.Context) -> None:
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

@_teleport.child
@lightbulb.option("channel", "the channel to teleport", required=True, type=hikari.GuildChannel)
@lightbulb.option("name", "the name of the checkpoint", required=True, type=str)
@lightbulb.command("add", "save a new checkpoint", inherit_checks=True, aliases=["a", "+"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _add(ctx: lightbulb.Context) -> None:
    name = ctx.options.name
    channel = ctx.options.channel
    guild_id = ctx.event.message.guild_id
    user_id = ctx.event.message.author.id

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
            await ctx.respond(f"Checkpoint **{name}** already exists", reply=True)
            return
        else:
            checkpoint["points"][name] = channel.id
        checkpoints.update_one({"guild": {"$eq": guild_id}, "user": {"$eq": user_id}}, {"$set": {"points": checkpoint["points"]}})
    
    await ctx.respond(f"Successfully saved checkpoint **{name}**", reply=True)

@_teleport.child
@lightbulb.option("name", "the name of the checkpoint", required=True, type=str)
@lightbulb.command("remove", "delete a saved checkpoint", inherit_checks=True, aliases=["r", "-"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _remove(ctx: lightbulb.Context) -> None:
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
        if name in checkpoint["points"].keys():
            del checkpoint["points"][name]
        else:
            await ctx.respond(f"You do not have a checkpoint saved as **{name}**", reply=True)
            return

    checkpoints.update_one({"guild": {"$eq": guild_id}, "user": {"$eq": user_id}}, {"$set": {"points": checkpoint["points"]}})
    await ctx.respond(f"Successfully deleted checkpoint **{name}**", reply=True)

@_teleport.child
@lightbulb.command("list", "list your saved checkpoints", inherit_checks=True, aliases=["s", "l", "show"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _list(ctx: lightbulb.Context) -> None:
    guild_id = ctx.event.message.guild_id
    user_id = ctx.event.message.author.id

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
    
    embed=hikari.Embed(title=f"{ctx.event.message.author.username}'s checkpoints", color=bot_config['color']['default'], description=desc2)
    await ctx.respond(embed=embed, reply=True)

snipe_data = {}

@lightbulb.Check
def snipe_perms_check(ctx: lightbulb.Context) -> None:
    cluster = MongoClient(mongoclient)
    configs = cluster["snipe"]["server_configs"]

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
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | snipe_perms_check)
@lightbulb.option("channel", "the channel to snipe messages from", required=False, default=None, type=hikari.GuildChannel)
@lightbulb.command("snipe", "snipe a deleted or edited message", aliases=['sniper'])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _snipe(ctx: lightbulb.Context) -> None:
    channel = ctx.options.channel

    if not channel:
        channel_id = ctx.event.message.channel_id
        channel = ctx.get_channel()
    else:
        channel_id = channel.id
    
    try:
        snipe_list = snipe_data[str(channel_id)]
    except:
        return await ctx.respond("There is nothing to snipe")
    
    if snipe_list == []:
        return await ctx.respond("There is nothing to snipe")
    
    pages = []
    for data in snipe_list:
        embed = hikari.Embed(
            color = bot_config['color']['default']
        )
        embed.timestamp = data['time']
        embed.set_footer(text = f"{snipe_list.index(data)+1} / {len(snipe_list)}")

        if data['type'] == "delete":
            if data['content'] != None:
                embed.description = data['content']
            if data['attachment'] != None:
                embed.set_image(data['attachment'])
            embed.title = "Message Deleted"
            embed.set_author(name=f"{data['user']}", icon=data['avatar'])
        
        elif data['type'] == "edit":
            embed.add_field(name="Old content", value=str(data['old']))
            embed.add_field(name="New content", value=str(data['new']))
            embed.title = "Message Edited"
            embed.set_author(name=f"{data['user']}", icon=data['avatar'])
        
        elif data['type'] == "purge":
            embed.title = f"{data['count']} Messages Purged"
            embed.description = data['content']

        pages.append(embed)

    navigator = nav.NavigatorView(pages=pages, buttons=[miru.ext.nav.buttons.PrevButton(style=hikari.ButtonStyle.PRIMARY, emoji=hikari.Emoji.parse(bot_config['emoji']['blue_arrowL'])), miru.ext.nav.buttons.NextButton(style=hikari.ButtonStyle.PRIMARY, emoji=hikari.Emoji.parse(bot_config['emoji']['blue_arrowR']))])
    await navigator.send(ctx.event.message.channel_id)

@plugin.listener(hikari.GuildMessageUpdateEvent)
async def _on_message_update(message: hikari.GuildMessageUpdateEvent) -> None:
    old = message.old_message
    new = message.message

    if not new:
        return
    
    try:
        if new.author.is_bot == True or new.author.is_system == True:
            return
    except:
        return

    data = {
        "type": "edit",
        "id": int(new.author.id),
        "user": str(new.author),
        "avatar": str(new.author.avatar_url),
        "new": new.content,
        "old": old.content,
        "time": new.edited_timestamp
    }

    global snipe_data

    try:
        snipe_data[str(new.channel_id)] = [data] + snipe_data[str(new.channel_id)]
    except KeyError:
        snipe_data[str(new.channel_id)] = []
        snipe_data[str(new.channel_id)] = [data] + snipe_data[str(new.channel_id)]

@plugin.listener(hikari.GuildMessageDeleteEvent)
async def _on_message_delete(message: hikari.GuildMessageDeleteEvent) -> None:
    msg = message.old_message
    if not msg:
        return
    
    if msg.author.is_bot == True or msg.author.is_system == True:
        return

    data = {
        "type": "delete",
        "id": int(msg.author.id),
        "user": str(msg.author),
        "avatar": str(msg.author.avatar_url),
        "content": msg.content,
        "time": datetime.datetime.now(tz=datetime.timezone.utc)
    }

    if msg.attachments != ():
        data['attachment'] = str((msg.attachments[0]).url)
    else:
        data['attachment'] = None

    global snipe_data

    try:
        snipe_data[str(msg.channel_id)] = [data] + snipe_data[str(msg.channel_id)]
    except KeyError:
        snipe_data[str(msg.channel_id)] = []
        snipe_data[str(msg.channel_id)] = [data] + snipe_data[str(msg.channel_id)]

@plugin.listener(hikari.GuildBulkMessageDeleteEvent)
async def _on_bulk_delete(messages: hikari.GuildBulkMessageDeleteEvent) -> None:
    msgs = messages.old_messages
    
    msgs_list = []
    for m in msgs.values():
        msgs_list.append(m)

    content = ""
    for msg in reversed(list(msgs.values())):
        content += f"\n**{msg.author.username}:** {msg.content}"
    
    data = {
        "type": "purge",
        "content": content,
        "time": datetime.datetime.now(tz=datetime.timezone.utc),
        "count": len(msgs)
    }

    global snipe_data

    try:
        snipe_data[str(messages.channel_id)] = [data] + snipe_data[str(messages.channel_id)]
    except KeyError:
        snipe_data[str(messages.channel_id)] = []
        snipe_data[str(messages.channel_id)] = [data] + snipe_data[str(messages.channel_id)]

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)