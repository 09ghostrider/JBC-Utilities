import hikari
import lightbulb
import random
import miru
import pymongo
from pymongo import MongoClient
import datetime
import os
from dotenv import load_dotenv

plugin = lightbulb.Plugin("mod")
plugin.add_checks(lightbulb.guild_only)

load_dotenv()
mongoclient = os.getenv("DATABASE")
with open("./secrets/prefix") as f:
    prefix = f.read().strip()

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option("content", "the content to dm", required=True, type=str, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.option("member", "the member to dm", required=True, type=hikari.User)
@lightbulb.command("dm", "dm a member", aliases=["directmessage"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _dm(ctx: lightbulb.Context) -> None:
    user = ctx.options.member
    content = ctx.options.content
    try:
        await (await user.fetch_dm_channel()).send(content)
        await ctx.event.message.add_reaction("✅")
    except Exception as e:
        await ctx.event.message.add_reaction("❌")

@plugin.command()
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MANAGE_CHANNELS) | lightbulb.owner_only)
@lightbulb.option("channel", "the channel to add the given member", required=True, type=hikari.GuildChannel)
@lightbulb.option("member", "the member to add to the given channel", required=True, type=hikari.Member)
@lightbulb.command("addmember", "adds a member to a given channel", aliases=["addmem", "amem"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _addmember(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    channel = ctx.options.channel

    try:
        await ctx.bot.rest.edit_permission_overwrites(channel=channel, target=member, allow=(hikari.Permissions.SEND_MESSAGES | hikari.Permissions.VIEW_CHANNEL | hikari.Permissions.READ_MESSAGE_HISTORY))
    except Exception as e:
        await ctx.respond(f"There was an error adding the member", reply=True)
        raise e

    await ctx.respond(f"Successfully added {member.mention} to <#{channel.id}>", reply=True, user_mentions=True)

@plugin.command()
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MANAGE_CHANNELS) | lightbulb.owner_only)
@lightbulb.option("channel", "the channel to removed the given member", required=True, type=hikari.GuildChannel)
@lightbulb.option("member", "the member to remove to the given channel", required=True, type=hikari.Member)
@lightbulb.command("removemember", "removes a member to a given channel", aliases=["removemem", "rmem"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _removemember(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    channel = ctx.options.channel

    try:
        await ctx.bot.rest.delete_permission_overwrite(channel=channel, target=member)
    except Exception as e:
        await ctx.respond(f"There was an error removing the member", reply=True)
        raise e

    await ctx.respond(f"Successfully removed {member.mention} from <#{channel.id}>", reply=True, user_mentions=True)

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option("text", "the text to echo", required=True, type=str, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.option("channel", "the channel to echo", required=False, default=None, type=hikari.GuildTextChannel)
@lightbulb.command("echo", "Makes the bot say something in the specified channel", aliases=["say"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _echo(ctx: lightbulb.Context) -> None:
    channel = ctx.options.channel
    text = ctx.options.text

    try:
        await ctx.event.message.delete()
    except:
        pass

    if channel == None:
        channel = ctx.get_guild().get_channel(ctx.event.message.channel_id)
    
    await ctx.app.rest.create_message(channel, text)

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option("member", "member", required=True, type=hikari.Member)
@lightbulb.command("silence", "make a member stfu", aliases=["shutup", "stfu", "shut"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _shut(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    silenced = cluster["mod"]["silenced"]
    data = silenced.find_one({"guild": {"$eq": guild_id}})
    if data == None:
        data = {
            "guild": guild_id,
            "silenced": [member.id]
        }
        silenced.insert_one(data)
        await ctx.respond(f"{member.mention} has been silenced", reply=True, user_mentions=True)

    else:
        if member.id in data["silenced"]:
            data["silenced"].pop(data["silenced"].index(member.id))
            await ctx.respond(f"{member.mention} has been unsilenced", reply=True, user_mentions=True)
        else:
            data["silenced"].append(member.id)
            await ctx.respond(f"{member.mention} has been silenced", reply=True, user_mentions=True)
        silenced.update_one({"guild": {"$eq": guild_id}}, {"$set": {"silenced": data["silenced"]}})

@plugin.command()
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | lightbulb.owner_only)
@lightbulb.option("reason", "the reason for timeout", default="None", required=False, modifier=lightbulb.commands.base.OptionModifier(3), type=str)
@lightbulb.option("duration", "the duration of timeout", required=True, type=str)
@lightbulb.option("member", "the member to timeout", required=True, type=hikari.Member)
@lightbulb.command("timeout", "Timeout a member", aliases=["to"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _timeout(ctx: lightbulb.Context) -> None:
    duration = ctx.options.duration
    member = ctx.options.member
    reason = ctx.options.reason
    
    if ctx.event.message.member == member:
        await ctx.respond("You cant timeout yourself", delete_after=3)
        return
    if (ctx.event.message.member.get_top_role()).position <= (member.get_top_role()).position:
        await ctx.respond("You cant timeout members above you", delete_after=3)
        return

    try:
        time = int(duration)
    except:
        convertTimeList = {'s':1, 'm':60, 'h':3600, 'd':86400, 'S':1, 'M':60, 'H':3600, 'D':86400}
        try:
            time = int(duration[:-1]) * convertTimeList[duration[-1]]
        except:
            await ctx.respond("Invalid duration")
            return
    if time > 2419200:
        await ctx.respond("You can only timeout members upto **28d**", delete_after=3)
        return
        
    new_reason = f"Action requested by {ctx.event.message.author.username}#{ctx.event.message.author.discriminator}\n Reason: {reason}"
    try:
        await member.edit(communication_disabled_until=(datetime.datetime.utcfromtimestamp(int(round((datetime.datetime.now().timestamp())+time)))), reason=new_reason)
        await ctx.respond(f"{member.mention} ({member.username}#{member.discriminator}) has been put to timeout for **{duration}**\n**Reason:** {reason}")
    except Exception as e:
        await ctx.respond(e, delete_after=5)
        raise e

@plugin.command()
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | lightbulb.owner_only)
@lightbulb.option("reason", "the reason for removal of timeout", default="None", required=False, modifier=lightbulb.commands.base.OptionModifier(3), type=str)
@lightbulb.option("member", "the member to remove timeout from", required=True, type=hikari.Member)
@lightbulb.command("removetimeout", "Remove timeout from a member", aliases=["rto", "unto", "removeto"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _removetimeout(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    reason = ctx.options.reason
        
    new_reason = f"Action requested by {ctx.event.message.author.username}#{ctx.event.message.author.discriminator}\n Reason: {reason}"
    try:
        await member.edit(communication_disabled_until=None, reason=new_reason)
        await ctx.respond(f"{member.mention} ({member.username}#{member.discriminator}) has been removed from timeout\n**Reason:** {reason}")
    except Exception as e:
        await ctx.respond(e, delete_after=5)
        raise e

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)