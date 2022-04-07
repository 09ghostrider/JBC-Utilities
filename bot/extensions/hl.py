import hikari
import lightbulb
import random
import miru
import pymongo
from pymongo import MongoClient
import datetime

plugin = lightbulb.Plugin("hl")
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./secrets/prefix") as f:
    prefix = f.read().strip()

with open("./secrets/db") as f:
    mongoclient = f.read().strip()

@lightbulb.Check
def perms_check(ctx: lightbulb.Context) -> None:
    cluster = MongoClient(mongoclient)
    configs = cluster["highlight"]["server_configs"]

    config = configs.find_one({"guild": ctx.interaction.guild_id})
    if config == None:
        return False
    
    roles = ctx.interaction.member.get_roles()
    for r in config["req"]:
        role = ctx.app.cache.get_role(r)
        if role in roles:
            return True
    return False

@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.add_checks(lightbulb.owner_only| lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | perms_check)
@lightbulb.command("highlight", "Highlighting means you will receive a message when your keyword is said in chat.", aliases=["hl"])
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def _hl(ctx: lightbulb.Context) -> None:
    embed=hikari.Embed(title="=== Command Help ===", description="""highlight - Highlighting means you will receive a message when your keyword is said in chat. It will only notify you if you haven't posted anything in chat for the past 5 minutes.

    Usage: -highlight [subcommand]
    """, color=random.randint(0x0, 0xffffff))
    embed.add_field(name="== Subcommands ==", value="""- add - add a word to your highlights list
    - remove - remove a word from your highlight list
    - list - show your current highlight list
    - block - block a channel or member from triggering your highlights
    - unblock - unblock a blocked channel or member
    - clear - clear all your highlights""")
    await ctx.respond(embed=embed)

@_hl.child
@lightbulb.option("word", "the word to start tracking")
@lightbulb.command("add", "add a word to your highlights list", inherit_checks=True, aliases=["+", "a"])
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _add(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    word = ctx.options.word
    word = word.lower()
    user_id = ctx.author.id

    if "@everyone" in word or "@here" in word:
        await ctx.respond("You cant highlight `@everyone` and `@here`", flags=ephemeral)
        return
    if len(word) < 2:
        await ctx.respond("Word needs to be at least 2 characters long", flags=ephemeral)
        return
    if len(word) > 20:
        await ctx.respond("Words can only be upto 20 characters", flags=ephemeral)
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
            await ctx.respond("You can only have 10 highlights", flags=ephemeral)
            return
        hl_list = user_data["hl"]
        
        if word in hl_list:
            await ctx.respond("That word is already in your highlight list", flags=ephemeral)
            return
        user_data["hl"].append(word)
    if in_db == False:
        highlight.insert_one(user_data)
    elif in_db == True:
        highlight.update_one({"_id":user_id}, {"$set":{"hl":user_data["hl"]}})
    await ctx.respond(f"Successfully add **{word}** to your highlights list")

@_hl.child
@lightbulb.option("word", "the word to stop tracking")
@lightbulb.command("remove", "remove a word from your highlight list", inherit_checks=True, aliases=["-", "r"])
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _remove(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    word = ctx.options.word
    word = word.lower()
    user_id = ctx.author.id
    
    cluster = MongoClient(mongoclient)
    highlight = cluster["highlight"]["highlight"]

    user_data = highlight.find_one({
        "_id": {"$eq": user_id}
    })
    if user_data == None:
        await ctx.respond(f"You are not tracking any words", flags=ephemeral)
        return
    
    hl_list = user_data["hl"]
    if word not in hl_list:
        await ctx.respond("You are not tracking that word", flags=ephemeral)
        return
    
    hl_list.pop(hl_list.index(word))
    highlight.update_one({"_id":user_id}, {"$set":{"hl":hl_list}})
    await ctx.respond(f"Successfully remove **{word}** from your highlights list")

@_hl.child
@lightbulb.command("list", "show your current highlight list", inherit_checks=True, aliases=["show", "l"])
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _list(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    user_id = ctx.author.id

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
        await ctx.respond("You are not tracking anything", flags=ephemeral)
        return

    hl_str = ""
    for x in user_data["hl"]:
        hl_str = hl_str + x + "\n"
    embed = hikari.Embed(title="You're currently tracking the following words", description=f"{hl_str}" ,color=random.randint(0x0, 0xffffff))
    
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
    
    await ctx.respond(embed=embed)

@_hl.child
@lightbulb.option("blocks", "the member or channel to block", type=str)
@lightbulb.command("block", "block a channel or member from triggering your highlights", inherit_checks=True, aliases=["b"])
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _block(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
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
        else:
            await ctx.respond("Unknown channel or member", flags=ephemeral)
            return
    
    if channel == None and member == None:
        await ctx.respond("Unknown channel or member", flags=ephemeral)
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
            await ctx.respond(f"Successfuly blocked {channel.mention}")
            highlight.update_one({"_id":user_id}, {"$set":{"block_channel":user_data["block_channel"]}})
        else:
            await ctx.respond("That channel is already blocked", flags=ephemeral)
            return
    elif member != None:
        if member.id == ctx.author.id:
            await ctx.respond("You dont need to block yourself, you cant trigger your own highlights", flags=ephemeral)
            return
        if member.is_bot == True:
            await ctx.respond("You dont need to block bots, they cant trigger your highlights", flags=ephemeral)
            return
        if member.id not in user_data["block_member"]:
            user_data["block_member"].append(member.id)
            await ctx.respond(f"Successfuly blocked {member.mention}", user_mentions=False)
            highlight.update_one({"_id":user_id}, {"$set":{"block_member":user_data["block_member"]}})
        else:
            await ctx.respond("That member is already blocked", flags=ephemeral)
            return

@_hl.child
@lightbulb.option("blocks", "the member or channel to unblock", type=str)
@lightbulb.command("unblock", "unblock a blocked channel or member", inherit_checks=True, aliases=["unb"])
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _unblock(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
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
        else:
            await ctx.respond("That is not in your block list", flags=ephemeral)
            return
    
    if channel == None and member == None:
        await ctx.respond("That is not in your block list", flags=ephemeral)
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
            await ctx.respond(f"Successfuly unblocked {channel.mention}")
            highlight.update_one({"_id":user_id}, {"$set":{"block_channel":user_data["block_channel"]}})
        else:
            await ctx.respond("That channel is not blocked")
            return
    elif member != None:
        if member.id == ctx.author.id:
            await ctx.respond("That is not in your block list")
            return
        if member.id in user_data["block_member"]:
            user_data["block_member"].pop(user_data["block_member"].index(member.id))
            await ctx.respond(f"Successfuly unblocked {member.mention}", user_mentions=False)
            highlight.update_one({"_id":user_id}, {"$set":{"block_member":user_data["block_member"]}})
        else:
            await ctx.respond("That member is not blocked")
            return

@_hl.child
@lightbulb.command("clear", "clear all your highlights", inherit_checks=True, aliases=["c"])
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _clear(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    cluster = MongoClient(mongoclient)
    highlight = cluster["highlight"]["highlight"]
    user_id = ctx.author.id

    user_data = highlight.find_one({
        "_id": {"$eq": user_id}
    })

    if user_data == None:
        await ctx.respond("You are not tracking anything", flags=ephemeral)
        return
    
    else:
        try:
            highlight.update_one({"_id":user_id}, {"$set": {"hl": []}})
        except Exception as e:
            await ctx.respond("There was a error", flags=ephemeral)
            raise e
        await ctx.respond("Cleared all your highlights")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)