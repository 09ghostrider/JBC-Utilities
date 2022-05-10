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

plugin = lightbulb.Plugin("hl")
plugin.add_checks(botban_check)
ephemeral = hikari.MessageFlag.EPHEMERAL

load_dotenv()
mongoclient = os.getenv("DATABASE")
with open("./configs/config.json") as f:
    bot_config = json.load(f)

@lightbulb.Check
def perms_check(ctx: lightbulb.Context) -> None:
    cluster = MongoClient(mongoclient)
    configs = cluster["highlight"]["server_configs"]

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
@lightbulb.command("highlight", "Highlighting means you will receive a message when your keyword is said in chat.", aliases=["hl"])
@lightbulb.implements(lightbulb.PrefixCommandGroup)
async def _hl(ctx: lightbulb.Context) -> None:
    embed=hikari.Embed(title="=== Command Help ===", description="""highlight - Highlighting means you will receive a message when your keyword is said in chat. It will only notify you if you haven't posted anything in chat for the past 5 minutes.

    Usage: -highlight [subcommand]
    """, color=bot_config["color"]["default"])
    embed.add_field(name="== Subcommands ==", value="""- add - add a word to your highlights list
    - remove - remove a word from your highlight list
    - list - show your current highlight list
    - block - block a channel or member from triggering your highlights
    - unblock - unblock a blocked channel or member
    - clear - clear all your highlights""")
    await ctx.respond(embed=embed)

@_hl.child
@lightbulb.option("word", "the word to start tracking", type=str)
@lightbulb.command("add", "add a word to your highlights list", inherit_checks=True, aliases=["+", "a"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _add(ctx: lightbulb.Context) -> None:
    word = ctx.options.word
    word = word.lower()
    user_id = ctx.event.message.author.id

    if "@everyone" in word or "@here" in word:
        await ctx.respond("You cant highlight `@everyone` and `@here`", reply=True)
        return
    if len(word) < 2:
        await ctx.respond("Word needs to be at least 2 characters long", reply=True)
        return
    if len(word) > 50:
        await ctx.respond("Words can only be upto 50 characters", reply=True)
        return
    
    cluster = MongoClient(mongoclient)
    highlight = cluster["highlight"]["highlight"]

    user_data = highlight.find_one({
        "_id": {"$eq": user_id}
    })
    
    if user_data is None:
        in_db = False
        user_data = {
            "_id": user_id,
            "hl": [],
            "block_channel": [],
            "block_member": []
        }

    else:
        in_db = True
        hl_count = len(user_data["hl"])
        if hl_count >= 10:
            await ctx.respond("You can only have 10 highlights", reply=True)
            return
        hl_list = user_data["hl"]
        
        if word in hl_list:
            await ctx.respond("That word is already in your highlight list", reply=True)
            return
        user_data["hl"].append(word)
    if in_db == False:
        highlight.insert_one(user_data)
    elif in_db == True:
        highlight.update_one({"_id":user_id}, {"$set":{"hl":user_data["hl"]}})
    await ctx.respond(f"""Successfully add "{word}" to your highlights list""", reply=True)

@_hl.child
@lightbulb.option("word", "the word to stop tracking", type=str)
@lightbulb.command("remove", "remove a word from your highlight list", inherit_checks=True, aliases=["-", "r"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _remove(ctx: lightbulb.Context) -> None:
    word = ctx.options.word
    word = word.lower()
    user_id = ctx.event.message.author.id
    
    cluster = MongoClient(mongoclient)
    highlight = cluster["highlight"]["highlight"]

    user_data = highlight.find_one({
        "_id": {"$eq": user_id}
    })
    if user_data == None:
        await ctx.respond(f"You are not tracking any words", reply=True)
        return
    
    hl_list = user_data["hl"]
    if word not in hl_list:
        await ctx.respond("You are not tracking that word", reply=True)
        return
    
    hl_list.pop(hl_list.index(word))
    highlight.update_one({"_id":user_id}, {"$set":{"hl":hl_list}})
    await ctx.respond(f"""Successfully remove "{word}" from your highlights list""", reply=True)

@_hl.child
@lightbulb.command("list", "show your current highlight list", inherit_checks=True, aliases=["show", "l"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _list(ctx: lightbulb.Context) -> None:
    user_id = ctx.event.message.author.id

    cluster = MongoClient(mongoclient)
    highlight = cluster["highlight"]["highlight"]

    user_data = highlight.find_one({
        "_id": {"$eq": user_id}
    })
    
    if user_data is None:
        user_data = {
            "_id": user_id,
            "hl": [],
            "block_channel": [],
            "block_member": []
        }

    if user_data["hl"] == []:
        await ctx.respond("You are not tracking anything", reply=True)
        return

    hl_str = ""
    for x in user_data["hl"]:
        hl_str = hl_str + x + "\n"
    embed = hikari.Embed(title="You're currently tracking the following words", description=f"{hl_str}" ,color=bot_config["color"]["default"])
    
    if user_data["block_channel"] != []:
        channel_str = ""
        for c in user_data["block_channel"]:
            channel_str = channel_str + f"<#{c}>\n"
        embed.add_field(name="Ignored Channels", value=channel_str, inline=True)
    
    if user_data["block_member"] != []:
        member_str = ""
        for c in user_data["block_member"]:
            member_str = member_str + f"<@!{c}>\n"
        embed.add_field(name="Ignored Members", value=member_str, inline=True)
    
    await ctx.respond(embed=embed, reply=True)

@_hl.child
@lightbulb.option("blocks", "the member or channel to block", type=str)
@lightbulb.command("block", "block a channel or member from triggering your highlights", inherit_checks=True, aliases=["b"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _block(ctx: lightbulb.Context) -> None:
    blocks = ctx.options.blocks
    channel = None
    member = None
    try:
        channel = ctx.get_guild().get_channel(blocks)
    except:
        pass
    if channel == None:
        try:
            member = await ctx.bot.rest.fetch_member(ctx.guild_id, blocks)
        except:
            pass
    
    if member == None and channel == None:
        if blocks.startswith("<#") and blocks.endswith(">"):
            try:
                c = int(blocks[2:][:-1])
                channel = ctx.get_guild().get_channel(c)
            except:
                pass
        elif blocks.startswith("<@!") and blocks.endswith(">") and channel == None:
            try:
                m = int(blocks[3:][:-1])
                member = await ctx.bot.rest.fetch_member(ctx.guild_id, m)
            except:
                pass
        elif blocks.startswith("<@") and blocks.endswith(">") and channel == None:
            try:
                m = int(blocks[2:][:-1])
                member = await ctx.bot.rest.fetch_member(ctx.guild_id, m)
            except:
                pass
        else:
            await ctx.respond("Unknown channel or member", reply=True)
            return
    
    if channel == None and member == None:
        await ctx.respond("Unknown channel or member", reply=True)
        return
    
    cluster = MongoClient(mongoclient)
    highlight = cluster["highlight"]["highlight"]
    user_id = ctx.author.id

    user_data = highlight.find_one({
        "_id": {"$eq": user_id}
    })
    
    if user_data is None:
        user_data = {
            "_id": user_id,
            "hl": [],
            "channel": [],
            "member": []
        }
    
    if channel != None:
        if channel.id not in user_data["block_channel"]:
            user_data["block_channel"].append(channel.id)
            await ctx.respond(f"Successfuly blocked {channel.mention}", reply=True)
            highlight.update_one({"_id":user_id}, {"$set":{"block_channel":user_data["block_channel"]}})
        else:
            await ctx.respond("That channel is already blocked", reply=True)
            return
    elif member != None:
        if member.id == ctx.author.id:
            await ctx.respond("You dont need to block yourself, you cant trigger your own highlights", reply=True)
            return
        if member.is_bot == True:
            await ctx.respond("You dont need to block bots, they cant trigger your highlights", reply=True)
            return
        if member.id not in user_data["block_member"]:
            user_data["block_member"].append(member.id)
            await ctx.respond(f"Successfuly blocked {member.mention}", user_mentions=False, reply=True)
            highlight.update_one({"_id":user_id}, {"$set":{"block_member":user_data["block_member"]}})
        else:
            await ctx.respond("That member is already blocked", reply=True)
            return

@_hl.child
@lightbulb.option("blocks", "the member or channel to unblock", type=str)
@lightbulb.command("unblock", "unblock a blocked channel or member", inherit_checks=True, aliases=["unb"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _unblock(ctx: lightbulb.Context) -> None:
    blocks = ctx.options.blocks
    channel = None
    member = None
    try:
        channel = ctx.get_guild().get_channel(blocks)
    except:
        pass
    if channel == None:
        try:
            member = await ctx.bot.rest.fetch_member(ctx.guild_id, blocks)
        except:
            pass
    
    if member == None and channel == None:
        if blocks.startswith("<#") and blocks.endswith(">"):
            try:
                c = int(blocks[2:][:-1])
                channel = ctx.get_guild().get_channel(c)
            except:
                pass
        elif blocks.startswith("<@!") and blocks.endswith(">") and channel == None:
            try:
                m = int(blocks[3:][:-1])
                member = await ctx.bot.rest.fetch_member(ctx.guild_id, m)
            except:
                pass
        elif blocks.startswith("<@") and blocks.endswith(">") and channel == None:
            try:
                m = int(blocks[2:][:-1])
                member = await ctx.bot.rest.fetch_member(ctx.guild_id, m)
            except:
                pass
        else:
            await ctx.respond("That is not in your block list", reply=True)
            return
    
    if channel == None and member == None:
        await ctx.respond("That is not in your block list", reply=True)
        return
    
    cluster = MongoClient(mongoclient)
    highlight = cluster["highlight"]["highlight"]
    user_id = ctx.author.id

    user_data = highlight.find_one({
        "_id": {"$eq": user_id}
    })
    
    if user_data is None:
        user_data = {
            "_id": user_id,
            "hl": [],
            "block_channel": [],
            "block_member": []
        }
    
    if channel != None:
        if channel.id in user_data["block_channel"]:
            user_data["block_channel"].pop(user_data["block_channel"].index(channel.id))
            await ctx.respond(f"Successfuly unblocked {channel.mention}", reply=True)
            highlight.update_one({"_id":user_id}, {"$set":{"block_channel":user_data["block_channel"]}})
        else:
            await ctx.respond("That channel is not blocked", reply=True)
            return
    elif member != None:
        if member.id == ctx.author.id:
            await ctx.respond("That is not in your block list", reply=True)
            return
        if member.id in user_data["block_member"]:
            user_data["block_member"].pop(user_data["block_member"].index(member.id))
            await ctx.respond(f"Successfuly unblocked {member.mention}", user_mentions=False, reply=True)
            highlight.update_one({"_id":user_id}, {"$set":{"block_member":user_data["block_member"]}})
        else:
            await ctx.respond("That member is not blocked", reply=True)
            return

@_hl.child
@lightbulb.command("clear", "clear all your highlights", inherit_checks=True, aliases=["c"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _clear(ctx: lightbulb.Context) -> None:
    cluster = MongoClient(mongoclient)
    highlight = cluster["highlight"]["highlight"]
    user_id = ctx.event.message.author.id

    user_data = highlight.find_one({
        "_id": {"$eq": user_id}
    })

    if user_data == None:
        await ctx.respond("You are not tracking anything", reply=True)
        return
    
    else:
        try:
            highlight.update_one({"_id":user_id}, {"$set": {"hl": []}})
        except Exception as e:
            await ctx.respond("There was a error", reply=True)
            raise e
        await ctx.respond("Cleared all your highlights", reply=True)

last_seen = {}

@plugin.listener(hikari.MessageCreateEvent)
async def _on_message(message: hikari.MessageCreateEvent) -> None:
    if message.is_human == False:
        return

    if message.content == None or message.content == "":
        return
    
    user_id = message.author.id

    global last_seen
    
    while True:
        try:
            last_seen[str(message.message.guild_id)][str(message.message.channel_id)][str(user_id)] = datetime.datetime.now()
            break
        except KeyError:
            try:
                dummy1 = last_seen[str(message.message.guild_id)]
            except KeyError:
                last_seen[str(message.message.guild_id)] = {}
            try:
                dummy2 =last_seen[str(message.message.guild_id)][str(message.message.channel_id)]
            except KeyError:
                last_seen[str(message.message.guild_id)][str(message.message.channel_id)] = {}
    
    cluster = MongoClient(mongoclient)
    highlight = cluster["highlight"]["highlight"]

    words = (message.content).split(" ")
    dmed_users = []

    channel = await message.message.app.rest.fetch_channel(message.message.channel_id)
    t = (message.message.created_at) + datetime.timedelta(0,1)
    history = await channel.fetch_history(before=t).limit(5)
    description = ""

    for h in reversed(history):
        try:
            if len(h.content) > 200:
                hc = h.content[:200]
            else:
                hc = h.content
        except:
            hc = ""
        description = description + "\n" + f"**[<t:{round(h.created_at.timestamp())}:T>] {h.author.username}:** {hc}"

    matches = highlight.find(
            {"_id": {"$ne": user_id}}
        )

    for word in words:
        if matches is not None:
            for match in matches:
                member = await message.message.app.rest.fetch_member(message.message.guild_id, int(match["_id"]))
                if member:
                    if word.lower() in match["hl"]:
                        if user_id not in match["block_member"] and message.message.channel_id not in match["block_channel"]:
                            try:
                                perms = lightbulb.utils.permissions_in(channel, member)
                                if hikari.Permissions.VIEW_CHANNEL in perms:
                                    if int(match["_id"]) not in dmed_users:
                                        last_seen_check = False
                                        try:
                                            local_last_seen = last_seen[str(message.message.guild_id)][str(message.message.channel_id)][str(match["_id"])]
                                            if (datetime.datetime.now() - local_last_seen).total_seconds() > 300:
                                                last_seen_check = True
                                        except KeyError:
                                            last_seen_check = True
                                        if last_seen_check == True:
                                            embed=hikari.Embed(title=word, description=description, color=random.randint(0x0, 0xffffff))
                                            view = miru.View()
                                            view.add_item(miru.Button(label="Message", url=f"https://discord.com/channels/{message.message.guild_id}/{message.message.channel_id}/{message.message.id}"))
                                            content = f"""In **{(await message.message.app.rest.fetch_guild(message.message.guild_id)).name}** {channel.mention}, you were mentioned with highlight word "{word}" """
                                            try:
                                                userdm = await member.user.fetch_dm_channel()
                                                await userdm.send(content, embed=embed, components=view.build())
                                                dmed_users.append(int(match["_id"]))
                                            except:
                                                pass
                            except:
                                pass
                    
def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)