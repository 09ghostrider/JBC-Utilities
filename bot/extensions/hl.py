import hikari
import lightbulb
import random
import miru
import pymongo
from pymongo import MongoClient
import datetime

plugin = lightbulb.Plugin("hl")

with open(".\\secrets\\prefix") as f:
    prefix = f.read().strip()

with open(".\\secrets\\db") as f:
    mongoclient = f.read().strip()

@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("highlight", "Highlighting means you will receive a message when your keyword is said in chat.", aliases=["hl"])
@lightbulb.implements(lightbulb.PrefixCommandGroup)
async def _hl(ctx: lightbulb.Context) -> None:
    embed=hikari.Embed(title="=== Command Help ===", description="""highlight - Highlighting means you will receive a message when your keyword is said in chat.

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
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _add(ctx: lightbulb.Context) -> None:
    word = ctx.options.word
    word = word.lower()
    user_id = ctx.author.id

    # await ctx.respond(ctx.event.message.mentions)
    if bool(ctx.event.message.mentions.users) or bool(ctx.event.message.mentions.role_ids) or bool(ctx.event.message.mentions.channels) or ctx.event.message.mentions.everyone:
        await ctx.respond("You can't highlight mentions")
        return
    if "@everyone" in word or "@here" in word:
        await ctx.respond("You cant highlight `@everyone` and `@here`")
        return
    if len(word) < 2:
        await ctx.respond("Word needs to be at least 2 characters long")
        return
    if len(word) > 20:
        await ctx.respond("Words can only be upto 20 characters")
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
            await ctx.respond("You can only have 10 highlights")
            return
        hl_list = user_data["hl"]
        
        if word in hl_list:
            await ctx.respond("That word is already in your highlight list")
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
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _remove(ctx: lightbulb.Context) -> None:
    word = ctx.options.word
    word = word.lower()
    user_id = ctx.author.id
    
    cluster = MongoClient(mongoclient)
    highlight = cluster["highlight"]["highlight"]

    user_data = highlight.find_one({
        "_id": {"$eq": user_id}
    })
    if user_data == None:
        await ctx.respond(f"You are not tracking any words")
        return
    
    hl_list = user_data["hl"]
    if word not in hl_list:
        await ctx.respond("You are not tracking that word")
        return
    
    hl_list.pop(hl_list.index(word))
    highlight.update_one({"_id":user_id}, {"$set":{"hl":hl_list}})
    await ctx.respond(f"Successfully remove **{word}** from your highlights list")

@_hl.child
@lightbulb.command("list", "show your current highlight list", inherit_checks=True, aliases=["show", "l"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _list(ctx: lightbulb.Context) -> None:
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
        await ctx.respond("You are not tracking anything")
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
        else:
            await ctx.respond("Unknown channel or member")
            return
    
    if channel == None and member == None:
        await ctx.respond("Unknown channel or member")
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
            await ctx.respond("That channel is already blocked")
            return
    elif member != None:
        if member.id == ctx.author.id:
            await ctx.respond("You dont need to block yourself, you cant trigger your own highlights")
            return
        if member.is_bot == True:
            await ctx.respond("You dont need to block bots, they cant trigger your highlights")
            return
        if member.id not in user_data["block_member"]:
            user_data["block_member"].append(member.id)
            await ctx.respond(f"Successfuly blocked {member.mention}", user_mentions=False)
            highlight.update_one({"_id":user_id}, {"$set":{"block_member":user_data["block_member"]}})
        else:
            await ctx.respond("That member is already blocked")
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
        else:
            await ctx.respond("That is not in your block list")
            return
    
    if channel == None and member == None:
        await ctx.respond("That is not in your block list")
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
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _clear(ctx: lightbulb.Context) -> None:
    cluster = MongoClient(mongoclient)
    highlight = cluster["highlight"]["highlight"]
    user_id = ctx.author.id

    user_data = highlight.find_one({
        "_id": {"$eq": user_id}
    })

    if user_data == None:
        await ctx.respond("You are not tracking anything")
        return
    
    else:
        try:
            highlight.update_one({"_id":user_id}, {"$set": {"hl": []}})
        except Exception as e:
            await ctx.respond("There was a error")
            raise e
        await ctx.respond("Cleared all your highlights")

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
    history = await channel.fetch_history(before=message.message.created_at).limit(4)
    description = ""

    for h in reversed(history):
        description = description + "\n" + f"**[{h.created_at}] {h.author.username}:** {h.content[:200]}"
    description = description + "\n" + f"**[{message.message.created_at}] {message.message.author.username}:** {message.message.content[:200]}"

    matches = highlight.find(
            # {"hl": {"$in": word}},
            # {"block_member": {"nin": message.author.id}},
            # {"block_channel": {"nin": message.channel_id}},
            {"_id": {"$ne": user_id}}
        )

    for word in words:
        if matches is not None:
            for match in matches:
                if word in match["hl"]:
                    if user_id not in match["block_member"] and message.message.channel_id not in match["block_channel"]:
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
                                content = f"""In **{(await message.message.app.rest.fetch_guild(message.message.guild_id)).name}** {channel.mention}, you were mentioned with highlight word "{word}"
                                """
                                user = await message.message.app.rest.fetch_user(int(match["_id"]))
                                userdm = await user.fetch_dm_channel()
                                await userdm.send(content, embed=embed, components=view.build())
                                dmed_users.append(int(match["_id"]))

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)