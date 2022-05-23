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
from bot.utils.funcs import edit_perms

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

async def lockdown_unlockdown(ctx:lightbulb.Context, lorul:str, channels:list, role:int, p):
    if lorul == "lock":
        reason = f"Lockdown issued by {ctx.event.message.author} ({ctx.event.message.author.id})"
        embed = hikari.Embed(title="Lockdown :lock:", description="This category has been locked. Please be patient and do not DM staff as we sort out the issues that may be occurring. Thanks.", color=bot_config['color']['default'])
    else:
        reason = f"Unlockdown issued by {ctx.event.message.author} ({ctx.event.message.author.id})"
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
        elif lorul == "unlock":
            deny &= ~p
            allow |= p
        elif lorul == "reset":
            deny &= ~p
        
        await ctx.app.rest.edit_permission_overwrites(
            channel = cid,
            target = role,
            allow = allow,
            deny = deny,
            reason = reason,
            target_type = hikari.PermissionOverwriteType.ROLE
        )

        await c.send(embed=embed)

@lightbulb.Check
def gman_event_check(ctx: lightbulb.Context) -> None:
    if ctx.event.message.channel_id == 933855270826807308 and 832111569764352060 in ctx.event.message.member.role_ids:
        return True
    return False

@plugin.command()
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MANAGE_CHANNELS) | lightbulb.owner_only | gman_event_check)
@lightbulb.option("role", "the role lock the channel for", type=hikari.Role, required=False, default=None)
@lightbulb.option("channel", "the channel to lock", type=hikari.GuildChannel, required=False, default=None)
@lightbulb.command("lock", "lock a channel for a perticular role")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _lock(ctx: lightbulb.Context) -> None:
    role = ctx.options.role
    channel = ctx.options.channel

    if not role:
        role_id = ctx.event.message.guild_id
        role = "@everyone"
    else:
        role_id = role.id
        role = role.name
    
    if not channel:
        channel_id = ctx.event.message.channel_id
    else:
        channel_id = channel.id
    
    await edit_perms(ctx, "lock", channel_id, role_id, hikari.Permissions.SEND_MESSAGES)

    await ctx.respond(f"Locked <#{channel_id}> for **{role}**", role_mentions=False, mentions_everyone=False)

@plugin.command()
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MANAGE_CHANNELS) | lightbulb.owner_only | gman_event_check)
@lightbulb.option("state", "True for enable permission, False for reset permission (Default = False)", required=False, type=bool, default=False)
@lightbulb.option("role", "the role unlock the channel for", type=hikari.Role, required=False, default=None)
@lightbulb.option("channel", "the channel to unlock", type=hikari.GuildChannel, required=False, default=None)
@lightbulb.command("unlock", "unlock a channel for a perticular role")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _unlock(ctx: lightbulb.Context) -> None:
    role = ctx.options.role
    channel = ctx.options.channel
    state = ctx.options.state

    if not role:
        role_id = ctx.event.message.guild_id
        role = "@everyone"
    else:
        role_id = role.id
        role = role.name
    
    if not channel:
        channel_id = ctx.event.message.channel_id
    else:
        channel_id = channel.id
    
    if state == True:
        s = "unlock"
    else:
        s = "reset"

    await edit_perms(ctx, s, channel_id, role_id, hikari.Permissions.SEND_MESSAGES)

    await ctx.respond(f"Unlocked <#{channel_id}> for **{role}**", role_mentions=False, mentions_everyone=False)

@plugin.command()
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MANAGE_CHANNELS) | lightbulb.owner_only | gman_event_check)
@lightbulb.option("role", "the role lock the channel for", type=hikari.Role, required=False, default=None)
@lightbulb.option("channel", "the channel to lock", type=hikari.GuildChannel, required=False, default=None)
@lightbulb.command("viewlock", "lock a channel for a perticular role", aliases=["vlock"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _viewlock(ctx: lightbulb.Context) -> None:
    role = ctx.options.role
    channel = ctx.options.channel

    if not role:
        role_id = ctx.event.message.guild_id
        role = "@everyone"
    else:
        role_id = role.id
        role = role.name
    
    if not channel:
        channel_id = ctx.event.message.channel_id
    else:
        channel_id = channel.id
    
    await edit_perms(ctx, "lock", channel_id, role_id, hikari.Permissions.VIEW_CHANNEL)

    await ctx.respond(f"View locked <#{channel_id}> for **{role}**", role_mentions=False, mentions_everyone=False)

@plugin.command()
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MANAGE_CHANNELS) | lightbulb.owner_only | gman_event_check)
@lightbulb.option("state", "True for enable permission, False for reset permission (Default = False)", required=False, type=bool, default=False)
@lightbulb.option("role", "the role unlock the channel for", type=hikari.Role, required=False, default=None)
@lightbulb.option("channel", "the channel to unlock", type=hikari.GuildChannel, required=False, default=None)
@lightbulb.command("viewunlock", "unlock a channel for a perticular role", aliases=["vunlock"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _viewunlock(ctx: lightbulb.Context) -> None:
    role = ctx.options.role
    channel = ctx.options.channel
    state = ctx.options.state

    if not role:
        role_id = ctx.event.message.guild_id
        role = "@everyone"
    else:
        role_id = role.id
    
    if not channel:
        channel_id = ctx.event.message.channel_id
        role = role.name
    else:
        channel_id = channel.id
    
    if state == True:
        s = "unlock"
    else:
        s = "reset"

    await edit_perms(ctx, s, channel_id, role_id, hikari.Permissions.VIEW_CHANNEL)

    await ctx.respond(f"View unlocked <#{channel_id}> for **{role}**", role_mentions=False, mentions_everyone=False)

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

    channels = [834011997917413386, 868810579664597042, 897504251645943818, 834264185953058877, 841259536294608907, 886108586768478238, 924243183209185280, 973788657486020648, 973791488469245952, 972472890077351996, 851315417334677514, 834266950720290848, 834266997025406996, 927064797219000330, 927065062672306176, 834266718569496596, 926122207141306438, 845305881015877662, 896595923730333736, 889661750650208307, 926534852990357555, 960037267651588166]
    role = 832105614577631232

    await lockdown_unlockdown(ctx, "lock", channels, role, hikari.Permissions.SEND_MESSAGES)
    
    await ctx.respond("Lockdown complete")


@_lockdown.child
@lightbulb.command("dank", "lockdown the dank category", aliases=['dankmemer'], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _dank(ctx: lightbulb.Context) -> None:
    await ctx.respond("Locking dank memer category")

    channels = [834266950720290848, 834266997025406996, 927064797219000330, 927065062672306176, 851315417334677514]
    role = 832105614577631232

    await lockdown_unlockdown(ctx, "lock", channels, role, hikari.Permissions.SEND_MESSAGES)
    
    await ctx.respond("Lockdown complete")


@_lockdown.child
@lightbulb.command("karuta", "lockdown the karuta category", inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _karuta(ctx: lightbulb.Context) -> None:
    await ctx.respond("Locking karuta category")

    channels = [973789884722606080, 924243183209185280, 972472890077351996, 973788657486020648, 973791488469245952]
    role = 832105614577631232

    await lockdown_unlockdown(ctx, "lock", channels, role, hikari.Permissions.SEND_MESSAGES)
    
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

    channels = [834011997917413386, 868810579664597042, 897504251645943818, 834264185953058877, 841259536294608907, 886108586768478238, 924243183209185280, 973788657486020648, 973791488469245952, 972472890077351996, 851315417334677514, 834266950720290848, 834266997025406996, 927064797219000330, 927065062672306176, 834266718569496596, 926122207141306438, 845305881015877662, 896595923730333736, 889661750650208307, 926534852990357555, 960037267651588166]
    role = 832105614577631232

    await lockdown_unlockdown(ctx, "reset", channels, role, hikari.Permissions.SEND_MESSAGES)
    
    await ctx.respond("Unlockdown complete")


@_unlockdown.child
@lightbulb.command("dank", "unlockdown the dank category", aliases=['dankmemer'], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _dank(ctx: lightbulb.Context) -> None:
    await ctx.respond("Unlocking dank memer category")

    channels = [834266950720290848, 834266997025406996, 927064797219000330, 927065062672306176, 851315417334677514]
    role = 832105614577631232

    await lockdown_unlockdown(ctx, "reset", channels, role, hikari.Permissions.SEND_MESSAGES)
    
    await ctx.respond("Unlockdown complete")


@_unlockdown.child
@lightbulb.command("karuta", "unlockdown the karuta category", inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _karuta(ctx: lightbulb.Context) -> None:
    await ctx.respond("Unlocking karuta category")

    channels = [973789884722606080, 924243183209185280, 972472890077351996, 973788657486020648, 973791488469245952]
    role = 832105614577631232

    await lockdown_unlockdown(ctx, "reset", channels, role, hikari.Permissions.SEND_MESSAGES)
    
    await ctx.respond("Unlockdown complete")

@plugin.command()
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.BAN_MEMBERS))
@lightbulb.option("reason", "the reason for their ban", type=str, modifier=lightbulb.commands.base.OptionModifier(3), required=False)
@lightbulb.option("delete_days", "the number of days to delete messages for", type=int, default=0, required=False)
@lightbulb.option("member", "the mmeber to ban", type=hikari.User)
@lightbulb.command("ban", "Bans a member whether or not the member is in the server")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _ban(ctx: lightbulb.Context) -> None:
    user = ctx.options.member
    delete_days = ctx.options.delete_days
    reason = ctx.options.reason

    try:
        member = await ctx.app.rest.fetch_member(ctx.event.message.guild_id, user)
    except hikari.NotFoundError:
        member = None

    if member:
        if (ctx.event.message.member.get_top_role()).position <= (member.get_top_role()).position:
            return await ctx.respond("You can not do that due to role hierarchy")

    delete_days = 0 if delete_days < 0 else delete_days
    delete_days = 7 if delete_days > 7 else delete_days

    await ctx.app.rest.ban_user(ctx.event.message.guild_id, user, delete_message_days=delete_days, reason = f"Action requested by {ctx.event.message.author} ({ctx.event.message.author.id}) | Reason: {reason}")
    await ctx.respond(f"Banned **{user}**")

@plugin.command()
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.BAN_MEMBERS))
@lightbulb.add_checks(lightbulb.bot_has_role_permissions(hikari.Permissions.BAN_MEMBERS))
@lightbulb.option("reason", "the reason for their unban", type=str, modifier=lightbulb.commands.base.OptionModifier(3), required=False)
@lightbulb.option("member", "the member to unban", type=hikari.User)
@lightbulb.command("unban", "Unban a banned member")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _unban(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    reason = ctx.options.reason

    try:
        await ctx.app.rest.unban_user(ctx.event.message.guild_id, member, reason = f"Action requested by {ctx.event.message.author} ({ctx.event.message.author.id}) | Reason: {reason}")
    except hikari.NotFoundError:
        return await ctx.respond(f"Not a previously banned member")
    await ctx.respond(f"Unbanned **{member}**")

@plugin.command()
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.KICK_MEMBERS))
@lightbulb.option("reason", "the reason for their kick", type=str, modifier=lightbulb.commands.base.OptionModifier(3), required=False)
@lightbulb.option("member", "the member to kick", type=hikari.Member)
@lightbulb.command("kick", "kick a member from the server")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _kick(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    reason = ctx.options.reason

    if (ctx.event.message.member.get_top_role()).position <= (member.get_top_role()).position:
            return await ctx.respond("You can not do that due to role hierarchy")
    
    await ctx.app.rest.kick_user(ctx.event.message.guild_id, member, reason = f"Action requested by {ctx.event.message.author} ({ctx.event.message.author.id}) | Reason: {reason}")
    await ctx.respond(f"Kicked **{member}**")

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command("censor", "censor a word from being used")
@lightbulb.implements(lightbulb.PrefixCommandGroup)
async def _censor(ctx: lightbulb.Context) -> None:
    pass

@_censor.child
@lightbulb.option("word", "the word to censor", type=str, required=True)
@lightbulb.command("add", "add a word to the censor list", aliases=["+"], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _add(ctx: lightbulb.Context) -> None:
    word = ctx.options.word
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})
    
    if censor_list is None:
        censor_list = {
            "guild_id": guild_id,
            "censored": [word],
            "whitelist": {
                "role": [],
                "channel": [],
                "member": []
            },
            "punishment": {
                "action": "timeout",
                "duration": 120
            }
        }
        censor_db.insert_one(censor_list)
        return await ctx.respond(f"""Added "{word}" to censor list""", reply=True)
    
    if word in censor_list["censored"]:
        return await ctx.respond("It is already censored", reply=True)
    
    censor_list["censored"].append(word)
    censor_db.update_one({"guild_id": guild_id}, {"$set": {"censored": censor_list["censored"]}})
    await ctx.respond(f"""Added "{word}" to censor list""", reply=True)

@_censor.child
@lightbulb.option("word", "the word to uncensor", type=str, required=True)
@lightbulb.command("remove", "remove a word from the censor list", aliases=["-"], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _remove(ctx: lightbulb.Context) -> None:
    word = ctx.options.word
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})
    
    if censor_list is None:
        return await ctx.respond("It is not censored", reply=True)
    
    if word not in censor_list["censored"]:
        return await ctx.respond("It is not censored", reply=True)
    
    censor_list["censored"].pop(censor_list["censored"].index(word))
    censor_db.update_one({"guild_id": guild_id}, {"$set": {"censored": censor_list["censored"]}})
    await ctx.respond(f"""Removed "{word}" from censor list""", reply=True)

@_censor.child
@lightbulb.command("list", "check the censor list", aliases=["show"], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _list(ctx: lightbulb.Context) -> None:
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})

    if censor_list is None:
        return await ctx.respond("You have no censored words", reply=True)
    
    if censor_list["censored"] == []:
        return await ctx.respond("You have no censored words", reply=True)

    desc = ""
    for w in censor_list["censored"]:
        desc += f"\n{w}"
    embed = hikari.Embed(title="Censored words", description=desc, color=bot_config["color"]["default"])
    embed.set_footer(text=f"{len(censor_list['censored'])} words censored")
    await ctx.respond(embed=embed, reply=True)

@_censor.child
@lightbulb.command("settings", "view and edit the censor settings for this guild", aliases=["setting", "set", "s"], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubGroup)
async def _settings(ctx: lightbulb.Context) -> None:
    pass

@_settings.child
@lightbulb.command("view", "view the current setting", inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _settings_view(ctx: lightbulb.Context) -> None:
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})
    
    if censor_list is None:
        censor_list = {
            "guild_id": guild_id,
            "censored": [],
            "whitelist": {
                "role": [],
                "channel": [],
                "member": []
            },
            "punishment": {
                "action": "timeout",
                "duration": 120
            }
        }

    embed=hikari.Embed(title="CENSOR SETTINGS", color=bot_config["color"]["default"])
    embed.description = f"""{bot_config['emoji']['reply2']} **Punishment:** {censor_list['punishment']['action']}
{bot_config['emoji']['reply']} **Duration:** {datetime.timedelta(seconds = int(censor_list['punishment']['duration']))} (if punishment is timeout)"""

    f1 = ""
    if len(censor_list['whitelist']['role']) == 0:
        f1 = f"{bot_config['emoji']['reply']} None"
    elif len(censor_list['whitelist']['role']) == 1:
        f1 = f"{bot_config['emoji']['reply']} <@&{censor_list['whitelist']['role'][0]}>"
    else:
        l1 = censor_list['whitelist']['role'][:-1]
        for r1 in l1:
            f1 += f"\n{bot_config['emoji']['reply2']} <@&{r1}>"
        f1 += f"\n{bot_config['emoji']['reply']} <@&{censor_list['whitelist']['role'][-1:][0]}>"
    embed.add_field(name=f"Roles ({len(censor_list['whitelist']['role'])}):", value=f1, inline=True)

    f2 = ""
    if len(censor_list['whitelist']['channel']) == 0:
        f2 = f"{bot_config['emoji']['reply']} None"
    elif len(censor_list['whitelist']['channel']) == 1:
        f2 = f"{bot_config['emoji']['reply']} <#{censor_list['whitelist']['channel'][0]}>"
    else:
        l2 = censor_list['whitelist']['channel'][:-1]
        for r2 in l2:
            f2 += f"\n{bot_config['emoji']['reply2']} <#{r2}>"
        f2 += f"\n{bot_config['emoji']['reply']} <#{censor_list['whitelist']['channel'][-1:][0]}>"
    embed.add_field(name=f"Channels ({len(censor_list['whitelist']['channel'])}):", value=f2, inline=True)

    f3 = ""
    if len(censor_list['whitelist']['member']) == 0:
        f3 = f"{bot_config['emoji']['reply']} None"
    elif len(censor_list['whitelist']['member']) == 1:
        f3 = f"{bot_config['emoji']['reply']} <@!{censor_list['whitelist']['member'][0]}>"
    else:
        l3 = censor_list['whitelist']['member'][:-1]
        for r3 in l3:
            f3 += f"\n{bot_config['emoji']['reply2']} <@!{r3}>"
        f3 += f"\n{bot_config['emoji']['reply']} <@!{censor_list['whitelist']['member'][-1:][0]}>"
    embed.add_field(name=f"Members ({len(censor_list['whitelist']['member'])}):", value=f3, inline=True)

    await ctx.respond(embed=embed, reply=True)

@_settings.child
@lightbulb.command("whitelist", "whitelist a role, channel or member from being punished", aliases=["wl"], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubGroup)
async def _settings_whitelist(ctx: lightbulb.Context) -> None:
    pass

@_settings_whitelist.child
@lightbulb.option("role", "the role to whitelist", type=hikari.Role, required=True)
@lightbulb.command("role", "whitelist a role from being punished", inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _settings_whitelist_role(ctx: lightbulb.Context) -> None:
    role = ctx.options.role
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})
    
    if censor_list is None:
        censor_list = {
            "guild_id": guild_id,
            "censored": [],
            "whitelist": {
                "role": [role.id],
                "channel": [],
                "member": []
            },
            "punishment": {
                "action": "timeout",
                "duration": 120
            }
        }
        censor_db.insert_one(censor_list)
        return await ctx.respond(f"Added {role.mention} to whitelist", reply=True, role_mentions=False)
    
    if role.id in censor_list['whitelist']['role']:
        censor_list['whitelist']['role'].pop(censor_list['whitelist']['role'].index(role.id))
        censor_db.update_one({"guild_id": guild_id}, {"$set": {"whitelist": censor_list['whitelist']}})
        return await ctx.respond(f"Removed {role.mention} from whitelist", reply=True, role_mentions=False)
    
    censor_list['whitelist']['role'].append(role.id)
    censor_db.update_one({"guild_id": guild_id}, {"$set": {"whitelist": censor_list['whitelist']}})
    await ctx.respond(f"Added {role.mention} to whitelist", reply=True, role_mentions=False)

@_settings_whitelist.child
@lightbulb.option("channel", "the channel to whitelist", type=hikari.GuildChannel, required=True)
@lightbulb.command("channel", "whitelist a channel from being punished", inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _settings_whitelist_channel(ctx: lightbulb.Context) -> None:
    channel = ctx.options.channel
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})
    
    if censor_list is None:
        censor_list = {
            "guild_id": guild_id,
            "censored": [],
            "whitelist": {
                "role": [],
                "channel": [channel.id],
                "member": []
            },
            "punishment": {
                "action": "timeout",
                "duration": 120
            }
        }
        censor_db.insert_one(censor_list)
        return await ctx.respond(f"Added {channel.mention} to whitelist", reply=True, role_mentions=False)
    
    if channel.id in censor_list['whitelist']['channel']:
        censor_list['whitelist']['channel'].pop(censor_list['whitelist']['channel'].index(channel.id))
        censor_db.update_one({"guild_id": guild_id}, {"$set": {"whitelist": censor_list['whitelist']}})
        return await ctx.respond(f"Removed {channel.mention} from whitelist", reply=True, role_mentions=False)
    
    censor_list['whitelist']['channel'].append(channel.id)
    censor_db.update_one({"guild_id": guild_id}, {"$set": {"whitelist": censor_list['whitelist']}})
    await ctx.respond(f"Added {channel.mention} to whitelist", reply=True, role_mentions=False)

@_settings_whitelist.child
@lightbulb.option("member", "the member to whitelist", type=hikari.Member, required=True)
@lightbulb.command("member", "whitelist a member from being punished", inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _settings_whitelist_member(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})
    
    if censor_list is None:
        censor_list = {
            "guild_id": guild_id,
            "censored": [],
            "whitelist": {
                "role": [],
                "channel": [],
                "member": [member.id]
            },
            "punishment": {
                "action": "timeout",
                "duration": 120
            }
        }
        censor_db.insert_one(censor_list)
        return await ctx.respond(f"Added {member.mention} to whitelist", reply=True, role_mentions=False)
    
    if member.id in censor_list['whitelist']['member']:
        censor_list['whitelist']['member'].pop(censor_list['whitelist']['member'].index(member.id))
        censor_db.update_one({"guild_id": guild_id}, {"$set": {"whitelist": censor_list['whitelist']}})
        return await ctx.respond(f"Removed {member.mention} from whitelist", reply=True, role_mentions=False)
    
    censor_list['whitelist']['member'].append(member.id)
    censor_db.update_one({"guild_id": guild_id}, {"$set": {"whitelist": censor_list['whitelist']}})
    await ctx.respond(f"Added {member.mention} to whitelist", reply=True, role_mentions=False)

@_settings.child
@lightbulb.option("action", "the action to take", required=True, type=str, choices=["ban", "kick", "timeout"])
@lightbulb.command("punishment", "the punishment when a censored word is used (default = timeout)", aliases=["punish", "action"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _settings_action(ctx: lightbulb.Context) -> None:
    action = (ctx.options.action).lower()
    guild_id = ctx.event.message.guild_id

    if action in ['ban', 'b']:
        action = "ban"
    elif action in ['kick', 'k']:
        action = "kick"
    elif action in ['timeout', 'to', 'mute', 'm']:
        action = "timeout"
    else:
        return await ctx.respond("Invalid action\nAvailable actions: timeout, kick, ban", reply=True)

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})
    
    if censor_list is None:
        censor_list = {
            "guild_id": guild_id,
            "censored": [],
            "whitelist": {
                "role": [],
                "channel": [],
                "member": []
            },
            "punishment": {
                "action": action,
                "duration": 120
            }
        }
        censor_db.insert_one(censor_list)
        return await ctx.respond(f"Set the action to {action}", reply=True)
    
    censor_list['punishment']['action'] = action
    censor_db.update_one({"guild_id": guild_id}, {"$set": {"punishment": censor_list['punishment']}})
    await ctx.respond(f"Set the action to {action}", reply=True)

@_settings.child
@lightbulb.option("duration", "the duration of timeout", required=True, type=str)
@lightbulb.command("duration", "if the punishment is set to timeout, the duration of timeout (default = 120s)", aliases=["md", "tod"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _settings_duration(ctx: lightbulb.Context) -> None:
    duration = ctx.options.duration
    guild_id = ctx.event.message.guild_id

    try:
        duration = int(duration)
    except:
        convertTimeList = {'s':1, 'm':60, 'h':3600, 'd':86400, 'S':1, 'M':60, 'H':3600, 'D':86400}
        try:
            duration = int(duration[:-1]) * convertTimeList[duration[-1]]
        except:
            return await ctx.respond("Invalid duration\nAvailable options: s, m, h, d", reply=True)
    if duration < 1:
        duration = 1

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})
    
    if censor_list is None:
        censor_list = {
            "guild_id": guild_id,
            "censored": [],
            "whitelist": {
                "role": [],
                "channel": [],
                "member": []
            },
            "punishment": {
                "action": "timeout",
                "duration": duration
            }
        }
        censor_db.insert_one(censor_list)
        return await ctx.respond(f"Set timeout duration to {datetime.timedelta(seconds = int(duration))}", reply=True)
    
    
    censor_list['punishment']['duration'] = duration
    censor_db.update_one({"guild_id": guild_id}, {"$set": {"punishment": censor_list['punishment']}})
    await ctx.respond(f"Set timeout duration to {datetime.timedelta(seconds = int(duration))}", reply=True)

@plugin.listener(hikari.MessageCreateEvent)
async def _on_message(message: hikari.MessageCreateEvent) -> None:
    if message.is_human == False:
        return
    
    if message.message.content is None:
        return

    guild_id = message.message.guild_id
    channel_id = message.message.channel_id
    member = await message.message.app.rest.fetch_member(guild_id, message.message.author.id)

    if member.id in bot_config['bot']['owner_ids']:
        return

    perms = lightbulb.utils.permissions.permissions_for(member)
    if hikari.Permissions.ADMINISTRATOR in perms:
        return

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})

    if censor_list is None:
        return
    if censor_list['censored'] == []:
        return
    
    if member.id in censor_list['whitelist']['member']:
        return
    
    if channel_id in censor_list['whitelist']['channel']:
        return
    
    roles = member.get_roles()
    for r in censor_list['whitelist']['role']:
        role = message.message.app.cache.get_role(r)
        if role in roles:
            return

    for word in censor_list['censored']:
        msg = message.message.content.lower().replace(" ", "")
        w = word.lower().replace(" ", "")
        if word in msg or word in message.message.content.lower() or w in msg or w in message.message.content.lower():
            try:
                await message.message.delete()
            except:
                pass
            
            action = censor_list['punishment']['action']
            reason = f"Automatic action carried out for using a blacklisted word ({word})"
            guild = await message.message.app.rest.fetch_guild(message.message.guild_id)
            channel = await message.message.app.rest.fetch_channel(channel_id)

            if action == "timeout":
                try:
                    await member.edit(communication_disabled_until=(datetime.datetime.utcfromtimestamp(int(round((datetime.datetime.now(tz=datetime.timezone.utc).timestamp())+int(censor_list['punishment']['duration']))))), reason=reason)
                    action_taken = bot_config['emoji']['tick']
                    try:
                        await message.message.author.send(f"You have been put to timeout for **{datetime.timedelta(seconds=int(censor_list['punishment']['duration']))}** in **{guild.name}**\nReason: {reason}")
                        member_dm = bot_config['emoji']['tick']
                    except:
                        member_dm = bot_config['emoji']['cross']
                except:
                    action_taken = bot_config['emoji']['cross']
                    member_dm = bot_config['emoji']['cross']
                
                embed=hikari.Embed(color=bot_config['color']['default'])
                embed.set_author(name=str(member), icon=str(member.avatar_url))
                embed.description = f"""{bot_config['emoji']['blue_arrow']} **Member:** {member.mention} ({member.id})
{bot_config['emoji']['blue_arrow']} **Action:** {action}
{bot_config['emoji']['blue_arrow']} **Duration:** {datetime.timedelta(seconds=int(censor_list['punishment']['duration']))}
{bot_config['emoji']['blue_arrow']} **Reason:** {reason}
{bot_config['emoji']['blue_arrow']} **Message:** {message.message.content[:200]}"""
                embed.add_field(name="More info:", value=f"""{bot_config['emoji']['blue_arrow']} Member DM: {member_dm}
{bot_config['emoji']['blue_arrow']} Action taken: {action_taken}""")

                await message.message.app.rest.create_message(channel, embed=embed)

            elif action == "ban":
                try:
                    await message.message.author.send(f"You have banned from **{guild.name}**\nReason: {reason}")
                    member_dm = bot_config['emoji']['tick']
                except:
                    member_dm = bot_config['emoji']['cross']
                try:
                    await message.message.app.rest.ban_member(guild, member, reason=reason)
                    action_taken = bot_config['emoji']['tick']
                except:
                    action_taken = bot_config['emoji']['cross']
                
                embed=hikari.Embed(color=bot_config['color']['default'])
                embed.set_author(name=str(member), icon=str(member.avatar_url))
                embed.description = f"""{bot_config['emoji']['blue_arrow']} **Member:** {member.mention} ({member.id})
{bot_config['emoji']['blue_arrow']} **Action:** {action}
{bot_config['emoji']['blue_arrow']} **Reason:** {reason}
{bot_config['emoji']['blue_arrow']} **Message:** {message.message.content[:200]}"""
                embed.add_field(name="More info:", value=f"""{bot_config['emoji']['blue_arrow']} Member DM: {member_dm}
{bot_config['emoji']['blue_arrow']} Action taken: {action_taken}""")

                await message.message.app.rest.create_message(await message.message.app.rest.fetch_channel(channel_id), embed=embed)

            elif action == "kick":
                try:
                    await message.message.author.send(f"You have kicked from **{guild.name}**\nReason: {reason}")
                    member_dm = bot_config['emoji']['tick']
                except:
                    member_dm = bot_config['emoji']['cross']
                try:
                    await message.message.app.rest.kick_member(guild, member, reason=reason)
                    action_taken = bot_config['emoji']['tick']
                except:
                    action_taken = bot_config['emoji']['cross']
                
                embed=hikari.Embed(color=bot_config['color']['default'])
                embed.set_author(name=str(member), icon=str(member.avatar_url))
                embed.description = f"""{bot_config['emoji']['blue_arrow']} **Member:** {member.mention} ({member.id})
{bot_config['emoji']['blue_arrow']} **Action:** {action}
{bot_config['emoji']['blue_arrow']} **Reason:** {reason}
{bot_config['emoji']['blue_arrow']} **Message:** {message.message.content[:200]}"""
                embed.add_field(name="More info:", value=f"""{bot_config['emoji']['blue_arrow']} Member DM: {member_dm}
{bot_config['emoji']['blue_arrow']} Action taken: {action_taken}""")

                await message.message.app.rest.create_message(await message.message.app.rest.fetch_channel(channel_id), embed=embed)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)