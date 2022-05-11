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
from bot.utils.checks import botban_check, jbc_server_check

plugin = lightbulb.Plugin("mod")
plugin.add_checks(lightbulb.guild_only)
plugin.add_checks(botban_check)

load_dotenv()
mongoclient = os.getenv("DATABASE")
with open("./configs/config.json") as f:
    bot_config = json.load(f)

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option("content", "the content to dm", required=True, type=str, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.option("member", "the member to dm", required=True, type=hikari.User)
@lightbulb.command("dm", "dm a member", aliases=["directmessage", "message"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _dm(ctx: lightbulb.Context) -> None:
    user = ctx.options.member
    content = ctx.options.content
    try:
        await (await user.fetch_dm_channel()).send(content)
        await ctx.event.message.add_reaction("✅")
    except:
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
@lightbulb.option("channel", "the channel to echo", required=True, type=hikari.GuildChannel)
@lightbulb.command("echo", "Makes the bot say something in the specified channel")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _echo(ctx: lightbulb.Context) -> None:
    channel = ctx.options.channel
    text = ctx.options.text
    try:
        await ctx.app.rest.create_message(channel, text, user_mentions=True)
        await ctx.event.message.add_reaction("✅")
    except:
        await ctx.event.message.add_reaction("❌")

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option("text", "the text to echo", required=True, type=str, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.command("say", "speak as if u were the bot", aliases=["s"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _say(ctx: lightbulb.Context) -> None:
    try:
        await ctx.event.message.delete()
    except:
        pass
    
    text = ctx.options.text
    reply = ctx.event.message.referenced_message
    channel = await ctx.event.message.fetch_channel()
    if not reply:
        await ctx.app.rest.create_message(channel, text, user_mentions=True)
    else:
        await ctx.app.rest.create_message(channel, text, user_mentions=True, reply=reply, mentions_reply=True)

silenced = []

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option("member", "member", required=True, type=hikari.Member)
@lightbulb.command("silence", "make a member stfu", aliases=["shutup", "stfu", "shut"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _silence(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    
    if member.id == ctx.app.application.id:
        return await ctx.respond(".....")

    if member.id == ctx.event.message.author.id:
        return await ctx.respond("You cant silence/unsilence yourself", reply=True)

    # if member.id in bot_config["bot"]["owner_ids"]:
    #     return await ctx.respond("No", reply=True)

    owner_role = ctx.app.cache.get_role(832107331265232909)
    if owner_role in member.get_roles():
        return await ctx.respond("You can't silence owners", reply=True)

    if member.id not in silenced:
        silenced.append(member.id)
        await ctx.respond(f"{member.mention} has been silenced", reply=True, user_mentions=False)
    else:
        silenced.pop(silenced.index(member.id))
        await ctx.respond(f"{member.mention} has been unsilenced", reply=True, user_mentions=False)

@plugin.listener(hikari.MessageCreateEvent)
async def _on_message(message: hikari.MessageCreateEvent) -> None:
    try:
        id = message.message.author.id
        if id in silenced:
            await message.message.delete()
    except:
        pass

@plugin.command()
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MODERATE_MEMBERS) | lightbulb.owner_only)
@lightbulb.option("reason", "the reason for timeout", default="None", required=False, modifier=lightbulb.commands.base.OptionModifier(3), type=str)
@lightbulb.option("duration", "the duration of timeout", required=True, type=str)
@lightbulb.option("member", "the member to timeout", required=True, type=hikari.Member)
@lightbulb.command("timeout", "Timeout a member", aliases=["to"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _timeout(ctx: lightbulb.Context) -> None:
    duration = ctx.options.duration
    member = ctx.options.member
    reason = ctx.options.reason
    
    if ctx.event.message.author.id != 680014609226399878:
        if (ctx.event.message.member.get_top_role()).position <= (member.get_top_role()).position:
            return await ctx.respond("You can only timeout members below you", reply=True)

    try:
        time = int(duration)
    except:
        convertTimeList = {'s':1, 'm':60, 'h':3600, 'd':86400, 'S':1, 'M':60, 'H':3600, 'D':86400}
        try:
            time = int(duration[:-1]) * convertTimeList[duration[-1]]
        except:
            return await ctx.respond("Invalid duration")
    if time < 0:
        time = 0
    if time > 2419200:
        time = 2419200
    
    new_reason = f"Action requested by {ctx.event.message.author} | Reason: {reason}"
    await member.edit(communication_disabled_until=(datetime.datetime.utcfromtimestamp(int(round((datetime.datetime.now().timestamp())+time)))), reason=new_reason)
    await ctx.respond(f"{member.mention} has been put to timeout for {datetime.timedelta(seconds = time)}\nReason: {reason}", reply=True)

@plugin.command()
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MODERATE_MEMBERS) | lightbulb.owner_only)
@lightbulb.option("reason", "the reason for removal of timeout", default="None", required=False, modifier=lightbulb.commands.base.OptionModifier(3), type=str)
@lightbulb.option("member", "the member to remove timeout from", required=True, type=hikari.Member)
@lightbulb.command("removetimeout", "Remove timeout from a member", aliases=["rto", "unto", "removeto"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _removetimeout(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    reason = ctx.options.reason
        
    new_reason = f"Action requested by {ctx.event.message.author} | Reason: {reason}"
    await member.edit(communication_disabled_until=None, reason=new_reason)
    await ctx.respond(f"{member.mention} has been removed from timeout\nReason: {reason}", reply=True)

@plugin.command()
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MANAGE_MESSAGES) |  lightbulb.owner_only)
@lightbulb.option("duration", "the duration of sm", required=False, default=0, type=str)
@lightbulb.command("slowmode", "edit the slowmode of a channel", aliases=["sm"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _sm(ctx: lightbulb.Context) -> None:
    duration = ctx.options.duration
    try:
        duration = int(duration)
    except:
        convertTimeList = {'s':1, 'm':60, 'h':3600, 'd':86400, 'S':1, 'M':60, 'H':3600, 'D':86400}
        try:
            duration = int(duration[:-1]) * convertTimeList[duration[-1]]
        except:
            return await ctx.respond("Invalid duration\nAvailable options: s, m, h, d")
    if duration > 21600:
        duration = 21600
    if duration < 0:
        duration = 0
    
    await ctx.get_guild().get_channel(ctx.event.message.channel_id).edit(rate_limit_per_user=duration)
    await ctx.respond(f"Set the slowmode to {datetime.timedelta(seconds = int(duration))}", reply=True)

async def lockdown_unlockdown(ctx:lightbulb.Context, lorul:str, channels:list, role:int):
    p = hikari.Permissions.SEND_MESSAGES

    if lorul == "lock":
        reason = f"Lockdown issued by {ctx.event.message.author} (ID: {ctx.event.message.author.id})"
        embed = hikari.Embed(title="Lockdown :lock:", description="This category has been locked. Please be patient and do not DM staff as we sort out the issues that may be occurring. Thanks.", color=bot_config['color']['default'])
    else:
        reason = f"Unlockdown issued by {ctx.event.message.author} (ID: {ctx.event.message.author.id})"
        embed = hikari.Embed(title="Unlockdown :unlock:", description="This category has been unlocked. The issues have been solved, so feel free to use the channels. Thanks.", color=bot_config['color']['default'])
    embed.set_footer(text=str(ctx.get_guild().name), icon=str(ctx.get_guild().icon_url))

    for cid in channels:
        c = await ctx.app.rest.fetch_channel(cid)
        perms = c.permission_overwrites
        try:
            perm = perms[role]
            allow = perm.allow
            deny = perm.deny
        except KeyError:
            allow = hikari.Permissions.NONE
            deny = hikari.Permissions.NONE

        if lorul == "lock":
            allow &= ~p
            deny |= p
        else:
            deny &= ~p
            allow |= p
        
        await ctx.app.rest.edit_permission_overwrites(
            channel = cid,
            target = role,
            allow = allow,
            deny = deny,
            reason = reason,
            target_type = hikari.PermissionOverwriteType.ROLE
        )

        await c.send(embed=embed)

@plugin.command()
@lightbulb.add_checks(jbc_server_check)
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MANAGE_GUILD) | lightbulb.owner_only)
@lightbulb.command("lockdown", "lockdown the server or a part of the server")
@lightbulb.implements(lightbulb.PrefixCommandGroup)
async def _lockdown(ctx: lightbulb.Context) -> None:
    await ctx.respond("Include the category to lockdown or `server` or full server lockdown\nCategories: dank, karuta")

@_lockdown.child
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command("server", "lockdown the entire server", aliases=['all', 'full'], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _server(ctx: lightbulb.Context) -> None:
    await ctx.respond("Locking entire server")

    channels = [851333787094745099, 834011997917413386, 868810579664597042, 897504251645943818, 834264185953058877, 841259536294608907, 886108586768478238, 924243183209185280, 973788657486020648, 973791488469245952, 972472890077351996, 851315417334677514, 834266950720290848, 834266997025406996, 927064797219000330, 927065062672306176, 834266718569496596, 926122207141306438, 845305881015877662, 896595923730333736, 889661750650208307, 926534852990357555, 960037267651588166]
    role = 832105614577631232

    await lockdown_unlockdown(ctx, "lock", channels, role)
    
    await ctx.respond("Lockdown complete")


@_lockdown.child
@lightbulb.command("dank", "lockdown the dank category", aliases=['dankmemer'], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _dank(ctx: lightbulb.Context) -> None:
    await ctx.respond("Locking dank memer category")

    channels = [834266950720290848, 834266997025406996, 927064797219000330, 927065062672306176, 851315417334677514]
    role = 888028007783100426

    await lockdown_unlockdown(ctx, "lock", channels, role)
    
    await ctx.respond("Lockdown complete")


@_lockdown.child
@lightbulb.command("karuta", "lockdown the karuta category", inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _karuta(ctx: lightbulb.Context) -> None:
    await ctx.respond("Locking karuta category")

    channels = [973789884722606080, 924243183209185280, 972472890077351996, 973788657486020648, 973791488469245952]
    role = 973792910774509698

    await lockdown_unlockdown(ctx, "lock", channels, role)
    
    await ctx.respond("Lockdown complete")

@plugin.command()
@lightbulb.add_checks(jbc_server_check)
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MANAGE_GUILD) | lightbulb.owner_only)
@lightbulb.command("unlockdown", "unlockdown the server or a part of the server")
@lightbulb.implements(lightbulb.PrefixCommandGroup)
async def _unlockdown(ctx: lightbulb.Context) -> None:
    await ctx.respond("Include the category to unlockdown or `server` or full server unlockdown\nCategories: dank, karuta")

@_unlockdown.child
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command("server", "unlockdown the entire server", aliases=['all', 'full'], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _server(ctx: lightbulb.Context) -> None:
    await ctx.respond("Unlocking entire server")

    channels = [851333787094745099, 834011997917413386, 868810579664597042, 897504251645943818, 834264185953058877, 841259536294608907, 886108586768478238, 924243183209185280, 973788657486020648, 973791488469245952, 972472890077351996, 851315417334677514, 834266950720290848, 834266997025406996, 927064797219000330, 927065062672306176, 834266718569496596, 926122207141306438, 845305881015877662, 896595923730333736, 889661750650208307, 926534852990357555, 960037267651588166]
    role = 832105614577631232

    await lockdown_unlockdown(ctx, "unlock", channels, role)
    
    await ctx.respond("Unlockdown complete")


@_lockdown.child
@lightbulb.command("dank", "unlockdown the dank category", aliases=['dankmemer'], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _dank(ctx: lightbulb.Context) -> None:
    await ctx.respond("Unlocking dank memer category")

    channels = [834266950720290848, 834266997025406996, 927064797219000330, 927065062672306176, 851315417334677514]
    role = 888028007783100426

    await lockdown_unlockdown(ctx, "unlock", channels, role)
    
    await ctx.respond("Unlockdown complete")


@_lockdown.child
@lightbulb.command("karuta", "unlockdown the karuta category", inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _karuta(ctx: lightbulb.Context) -> None:
    await ctx.respond("Unlocking karuta category")

    channels = [973789884722606080, 924243183209185280, 972472890077351996, 973788657486020648, 973791488469245952]
    role = 973792910774509698

    await lockdown_unlockdown(ctx, "unlock", channels, role)
    
    await ctx.respond("Unlockdown complete")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)