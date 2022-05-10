import hikari
import lightbulb
import random
import asyncio
import os
import miru
from dotenv import load_dotenv
from pymongo import MongoClient
import datetime
from lightbulb.ext import tasks
import json
from bot.utils.checks import botban_check

plugin = lightbulb.Plugin("giveaway")
plugin.add_checks(botban_check)
plugin.add_checks(lightbulb.guild_only)
ephemeral = hikari.MessageFlag.EPHEMERAL


with open("./configs/config.json") as f:
    bot_config = json.load(f)
giveaway_content = {
    "start": "<a:JBC_blackbutterfly:948610960543862834> **GIVEAWAY** <a:JBC_sparkles:961275013657419896>",
    "end": "<a:JBC_blackbutterfly:948610960543862834> **GIVEAWAY ENDED** <a:JBC_sparkles:961275013657419896>"
}
giveaway_emoji = hikari.Emoji.parse("<a:JBC_giveaway:961280186588999681>")
greentick = "<a:GreenTick:947818850840375297>"
redcross = "<a:RedCross:944235488808665109>"

load_dotenv()
mongoclient = os.getenv("DATABASE")
with open("./secrets/prefix") as f:
    prefix = f.read().strip()

class giveaway_view(miru.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @miru.button(emoji=giveaway_emoji, custom_id="enter", style=hikari.ButtonStyle.PRIMARY)
    async def _enter(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        guild_id = ctx.guild_id
        channel_id = ctx.channel_id
        user = ctx.interaction.user
        message_id = ctx.interaction.message.id

        cluster = MongoClient(mongoclient)
        database = cluster["giveaways"]["giveaways"]
        data = database.find_one({"guild_id": guild_id, "channel_id": channel_id, "message_id": message_id})
        if data == None:
            return await ctx.respond(f"{redcross} | Unknown giveaway", flags=ephemeral)
        if data["ended"] == True:
            return await ctx.respond(f"{redcross} | This giveaway has ended", flags=ephemeral)
        
        if user.id in data["joined_users"]:
            return await ctx.respond(f"{redcross} | You have already entered this giveaway", flags=ephemeral)
        
        roles = ctx.interaction.member.get_roles()

        for r in data["blacklist"]:
            role = self.app.cache.get_role(r)
            if role in roles:
                return await ctx.respond(f"{redcross} | You have the {role.mention} role which is blacklisted from this giveaway", flags=ephemeral)
        
        bypass_check = False
        for r in data["bypass"]:
            role = self.app.cache.get_role(r)
            if role in roles:
                bypass_check = True
                break
        
        if bypass_check == False:
            for r in data["requirements"]:
                role = self.app.cache.get_role(r)
                if role not in roles:
                    return await ctx.respond(f"{redcross} | You are missing the {role.mention} role which is required for this giveaway", flags=ephemeral)
        
        data["joined_users"].append(user.id)
        database.update_one({"guild_id": guild_id, "channel_id": channel_id, "message_id": message_id}, {"$set":{"joined_users": data["joined_users"]}})

        await ctx.respond(f"{greentick} | Your entry into this giveaway has been confirmed", flags=ephemeral)

@lightbulb.Check
def perms_check(ctx: lightbulb.Context) -> None:
    cluster = MongoClient(mongoclient)
    configs = cluster["giveaways"]["server_configs"]

    config = configs.find_one({"guild": ctx.interaction.guild_id})
    if config == None:
        return False
    
    r = config["req"]
    if r != None:
        try:
            role = ctx.app.cache.get_role(r)
            roles = ctx.interaction.member.get_roles()
            if role in roles:
                return True
        except:
            return False
    return False

@plugin.command()
@lightbulb.add_cooldown(10, 1, lightbulb.cooldowns.GuildBucket)
@lightbulb.option("ping", "ping the giveaway role", required=False, default=False, type=bool)
@lightbulb.option("message", "the message for this giveaway", required=False, default="", type=str)
@lightbulb.option("blacklist", "roles blacklisted from joining this giveaway", required=False, default="", type=str)
@lightbulb.option("bypass", "roles that can bypass the requirements on this giveaway", required=False, default="", type=str)
@lightbulb.option("requirements", "the requirements for this giveaway", required=False, default="", type=str)
@lightbulb.option("donor", "the donor for thie giveaway", required=False, default=None, type=hikari.Member)
@lightbulb.option("winners", "number of winners (Default = 1)", required=False, default=1, type=int)
@lightbulb.option("prize", "the prize of the giveaway", required=True, type=str)
@lightbulb.option("duration", "the length of the giveaway (s|m|h|d)", required=True, type=str)
@lightbulb.command("gstart", "start a giveaway")
@lightbulb.implements(lightbulb.SlashCommand)
async def _gstart(ctx:lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE, flags=ephemeral)
    
    # inputs
    duration = ctx.options.duration
    prize = ctx.options.prize
    winners = ctx.options.winners
    donor = ctx.options.donor
    reqs = ctx.options.requirements
    byps = ctx.options.bypass
    bls = ctx.options.blacklist
    message = ctx.options.message
    ping = ctx.options.ping
    
    # other variables
    guild_id = ctx.interaction.guild_id
    channel_id = ctx.interaction.channel_id
    host = ctx.interaction.user
    random_color = random.randint(0x0, 0xffffff)

    # checks
    # duration check
    try:
        duration = int(duration)
    except:
        convertTimeList = {'s':1, 'm':60, 'h':3600, 'd':86400, 'S':1, 'M':60, 'H':3600, 'D':86400}
        try:
            duration = int(duration[:-1]) * convertTimeList[duration[-1]]
        except:
            return await ctx.respond("Invalid duration\nAvailable options: s, m, h, d")
    if duration > 1209600:
        return await ctx.respond("Maximum giveaway duration is 14 days")
    if duration < 10:
        return await ctx.respond("Minimum giveaway duration is 10 seconds")
    
    # winners check
    if winners > 20:
        return await ctx.respond("You can only have upto 20 winners")
    if winners < 1:
        return await ctx.respond("You must have atleast 1 winner")

    # requirements check
    requirements = []
    if reqs != "":
        reqs = reqs.split(" ")
        for r in reqs:
            try:
                int(r)
            except:
                return await ctx.respond(f"Invalid role id for requirements {r}")
            role = ctx.app.cache.get_role(r)
            if role == None:
                return await ctx.respond(f"Invalid role id for requirements {r}")
            requirements.append(role.id)
    
    # bypass check
    bypass = []
    if byps != "":
        by = byps.split(" ")
        for b in by:
            try:
                int(b)
            except:
                return await ctx.respond(f"Invalid role id for bypass {b}")
            role = ctx.app.cache.get_role(b)
            if role == None:
                return await ctx.respond(f"Invalid role id for bypass {b}")
            bypass.append(role.id)
    
    # blacklist check
    blacklist = []
    if bls != "":
        bl = bls.split(" ")
        for b2 in bl:
            try:
                int(b2)
            except:
                return await ctx.respond(f"Invalid role id for blacklist {b2}")
            role = ctx.app.cache.get_role(b2)
            if role == None:
                return await ctx.respond(f"Invalid role id for blacklist {b2}")
            blacklist.append(role.id)
    
    # time and other variables
    current_time = datetime.datetime.now(tz=datetime.timezone.utc)
    current_timestamp = current_time.timestamp()
    end_timestamp = round(int(current_timestamp + duration))
    end_time = datetime.datetime.fromtimestamp(end_timestamp, tz=datetime.timezone.utc)
    channel = ctx.get_guild().get_channel(channel_id)
    
    # donor check
    if donor != None:
        gembed_desc = f""">>> Click the {giveaway_emoji} button to enter!
Ends <t:{end_timestamp}:R>
Hosted by: {host.mention}
Donated by: {donor.mention}
"""
    else:
        gembed_desc = f""">>> Click the {giveaway_emoji} button to enter!
Ends <t:{end_timestamp}:R>
Hosted by: {host.mention}
"""

    # giveaway embed
    gawembed = hikari.Embed(title=prize, color=random_color, description=gembed_desc)
    gawembed.set_footer(text=f"Winners: {winners} | Ends")
    gawembed.timestamp = end_time

    # Requirements fields
    if requirements != []:
        req_desc1 = ""
        for r1 in requirements:
            req_desc1 = req_desc1 + f"\n> <@&{r1}>"
        gawembed.add_field(name="Requirements:", value=req_desc1, inline=False)

    if bypass != []:
        req_desc2 = ""
        for r2 in bypass:
            req_desc2 = req_desc2 + f"\n> <@&{r2}>"
        gawembed.add_field(name="Bypass:", value=req_desc2, inline=False)
    
    if blacklist != []:
        req_desc3 = ""
        for r3 in blacklist:
            req_desc3 = req_desc3 + f"\n> <@&{r3}>"
        gawembed.add_field(name="Blacklist:", value=req_desc3, inline=False)
    
    view = giveaway_view()
    giveaway = await ctx.app.rest.create_message(channel, content=giveaway_content["start"], embed=gawembed, components=view.build())
    
    # updating database
    cluster = MongoClient(mongoclient)
    database = cluster["giveaways"]["giveaways"]
    data = {
        "message_id": giveaway.id,
        "channel_id": channel_id,
        "guild_id": guild_id,
        "end_timestamp": end_timestamp,
        "winners": winners,
        "host_id": host.id,
        "requirements": requirements,
        "bypass": bypass,
        "blacklist": blacklist,
        "prize": prize,
        "joined_users": [],
        "ended": False
    }
    database.insert_one(data)
    
    # starting view
    view.start(giveaway)

    giveaway_link = f"https://discord.com/channels/{guild_id}/{channel_id}/{giveaway.id}"

    if message != "":
        msgembed = hikari.Embed(description=f"**[Message:]({giveaway_link})** {message}", color=random_color)
        await ctx.app.rest.create_message(channel, embed=msgembed)

    # ping check
    if ping == True:
        cluster = MongoClient(mongoclient)
        configs = cluster["giveaways"]["server_configs"]
        config = configs.find_one({"guild": guild_id})
        if config != None:
            pr = config["ping"]
            if pr != None:
                await ctx.app.rest.create_message(channel, f"<@&{pr}>", role_mentions=True)

    # final response
    await ctx.respond(f"{greentick} | Successfully started giveaway")

# giveaway end task
@tasks.task(s=1, auto_start=True, pass_app=True)
async def giveaway_auto_end(bot):
    current_time = datetime.datetime.now(tz=datetime.timezone.utc)
    current_timestamp = round(int(current_time.timestamp()))
    cluster = MongoClient(mongoclient)
    database = cluster["giveaways"]["giveaways"]
    data = database.find_one_and_update({
        "ended": False,
        "end_timestamp": {"$lte": current_timestamp}
    },
    {"$set": {
        "ended": True,
        "end_timestamp": current_timestamp
    }})
    if data == None:
        return
    
    # database.update_one({"_id":data["_id"]}, {"$set": {"ended": "True", "end_timestamp": current_timestamp}})

    msg = await bot.rest.fetch_message(data["channel_id"], data["message_id"])
    if msg == None:
        database.delete_one({"_id": data["_id"]})
        return
    
    winners = data['winners']

    gaw_view = miru.get_view(msg)
    for b in gaw_view.children:
        b.disabled=True
    
    end_embed = hikari.Embed(title=msg.embeds[0].title, color="000000")
    end_embed.timestamp = current_time
    for f in msg.embeds[0].fields:
        end_embed.add_field(name=f.name, value=f.value)
    end_embed.set_footer(text=f"Winners {winners} | Ended")
    desc1 = (msg.embeds[0].description)[4:]
    desc1 = desc1.split("\n")
    desc1 = desc1[2:]

    giveaway_link = f"https://discord.com/channels/{data['guild_id']}/{data['channel_id']}/{data['message_id']}"
    joined_users = data["joined_users"]
    win_list = []
    win_str = ""
    gaw_channel = await bot.rest.fetch_channel(data["channel_id"])
    host = bot.cache.get_user(data["host_id"])
    gaw_guild = bot.cache.get_guild(data["guild_id"])

    winner_dm_embed = hikari.Embed(title="You won a giveaway!", color=random.randint(0x0, 0xffffff), description=f"You won the giveaway for **{data['prize']}** in **{gaw_guild.name}**\nHost: {host.mention}")
    winner_dm_embed.set_footer(text=f"{gaw_guild.name} • # {gaw_channel.name}")
    winner_dm_embed.timestamp = current_time

    view = miru.View()
    view.add_item(miru.Button(url=giveaway_link, label="Giveaway"))

    w = 0
    while w < winners:
        if joined_users == []:
            break
        else:
            winner = random.choice(joined_users)
            if winner not in win_list:
                user = bot.cache.get_user(winner)
                if user != None:
                    try:
                        dm = await bot.rest.create_dm_channel(user.id)
                        await bot.rest.create_message(dm, embed=winner_dm_embed, components=view.build())
                    except:
                        pass
                    win_list.append(user.id)
                    win_str = win_str + f"{user.mention} "
                    w += 1
            joined_users.pop(joined_users.index(winner))
        
    host_dm_embed = hikari.Embed(title="Your giveaway ended!", color=random.randint(0x0, 0xffffff))
    host_dm_embed.timestamp = current_time
    host_dm_embed.set_footer(text=f"{gaw_guild.name} • # {gaw_channel.name}")
    host_dm_embed.description = f"Your giveaway for **{data['prize']}** in **{gaw_guild.name}** has ended.\n\nYou have **{len(win_list)}** winners."

    win_str2 = ""
    if len(win_list) == 0:
        win_str2 = "None"
    else:
        for w1 in win_list:
            win_str2 = win_str2 + f"`{(win_list.index(w1))+1}:` <@!{w1}>\n"
    host_dm_embed.add_field(name=f"Winners ({len(win_list)}):", value=win_str2)
    try:
        dm = await bot.rest.create_dm_channel(host.id)
        await bot.rest.create_message(dm, embed=host_dm_embed, components=view.build())
    except:
        pass

    if win_str == "":
        win_str = "No one"

    try:
        desc3 = f"Winners: {win_str}\nEnded at: <t:{current_timestamp}:f>\n{desc1[0]}\n{desc1[1]}"
    except:
        desc3 = f"Winners: {win_str}\nEnded at: <t:{current_timestamp}:f>\n{desc1[0]}"
    end_embed.description = desc3

    await bot.rest.create_message(gaw_channel, content=f"{win_str}\nYou won the giveaway for **{data['prize']}**", user_mentions=True, components=view.build())
    await bot.rest.edit_message(channel=gaw_channel.id, message=msg.id, content=giveaway_content["end"], components=gaw_view.build(), embed=end_embed)

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command("gconfig", "configure giveaway settings")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def _gconfig(ctx: lightbulb.Context) -> None:
    pass

@_gconfig.child
@lightbulb.option("role", "role to ping", required=True, type=hikari.Role)
@lightbulb.command("pingrole", "the role to ping when ping is set to True while hosting giveaway")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _pingrole(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    guild_id = ctx.interaction.guild_id
    role = ctx.options.role

    cluster = MongoClient(mongoclient)
    configs = cluster["giveaways"]["server_configs"]
    config = configs.find_one({"guild": guild_id})
    if config == None:
        config = {
            "guild": guild_id,
            "req": None,
            "ping": role.id
        }
        configs.insert_one(config)
    else:
        config["ping"] = role.id
        configs.update_one({"guild": guild_id}, {"$set":{"ping": config["ping"]}})
    await ctx.respond(f"Set giveaway ping role as {role.mention}", reply=True, role_mentions=False)

@_gconfig.child
@lightbulb.option("role", "the manager role", required=True, type=hikari.Role)
@lightbulb.command("managerrole", "the role than can start, end, cancel and reroll giveaways")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _managerrole(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    guild_id = ctx.interaction.guild_id
    role = ctx.options.role

    cluster = MongoClient(mongoclient)
    configs = cluster["giveaways"]["server_configs"]
    config = configs.find_one({"guild": guild_id})
    if config == None:
        config = {
            "guild": guild_id,
            "req": role.id,
            "ping": None
        }
        configs.insert_one(config)
    else:
        config["req"] = role.id
        configs.update_one({"guild": guild_id}, {"$set": {"req": config["req"]}})
    await ctx.respond(f"Set manager role as {role.mention}", reply=True, role_mentions=False)

@_gconfig.child
@lightbulb.command("view", "view the current settings for this guild")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _view(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    guild_id = ctx.interaction.guild_id

    cluster = MongoClient(mongoclient)
    configs = cluster["giveaways"]["server_configs"]
    config = configs.find_one({"guild": guild_id})
    if config == None:
        config = {
            "guild": guild_id,
            "req": None,
            "ping": None
        }
    
    embed=hikari.Embed(title="Giveaway settings", color=random.randint(0x0, 0xffffff))
    embed.set_footer(text=ctx.interaction.get_guild().name, icon=ctx.interaction.get_guild().icon_url)
    if config["req"] == None:
        embed.add_field(name="Manager role:", value="> None")
    else:
        embed.add_field(name="Manager role:", value=f"> <@&{config['req']}>")
    if config["ping"] == None:
        embed.add_field(name="Ping role:", value="> None")
    else:
        embed.add_field(name="Ping role:", value=f"> <@&{config['ping']}>")
    
    await ctx.respond(embed=embed, reply=True)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)