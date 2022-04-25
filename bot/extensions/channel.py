import hikari
import lightbulb
import random
import asyncio
import miru
import datetime

plugin = lightbulb.Plugin("channels")
plugin.add_checks(lightbulb.guild_only)
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./secrets/prefix") as f:
    prefix = f.read().strip()

@plugin.command()
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MANAGE_CHANNELS) | lightbulb.owner_only)
@lightbulb.option("channel", "the channel to add the given member", required=True, type=hikari.GuildChannel)
@lightbulb.option("member", "the member to add to the given channel", required=True, type=hikari.Member)
@lightbulb.command("addmember", "adds a member to a given channel", aliases=["addmem", "amem"])
@lightbulb.implements(lightbulb.SlashCommand)
async def _addmember(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    member = ctx.options.member
    channel = ctx.options.channel

    try:
        await ctx.bot.rest.edit_permission_overwrites(channel=channel, target=member, allow=(hikari.Permissions.SEND_MESSAGES | hikari.Permissions.VIEW_CHANNEL | hikari.Permissions.READ_MESSAGE_HISTORY))
    except Exception as e:
        await ctx.respond(f"There was an error adding the member")
        raise e

    await ctx.respond(f"Successfully added {member.mention} to <#{channel.id}>", reply=True, user_mentions=True)

@plugin.command()
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MANAGE_CHANNELS) | lightbulb.owner_only)
@lightbulb.option("channel", "the channel to removed the given member", required=True, type=hikari.GuildChannel)
@lightbulb.option("member", "the member to remove to the given channel", required=True, type=hikari.Member)
@lightbulb.command("removemember", "removes a member to a given channel", aliases=["removemem", "rmem"])
@lightbulb.implements(lightbulb.SlashCommand)
async def _removemember(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    member = ctx.options.member
    channel = ctx.options.channel

    try:
        await ctx.bot.rest.delete_permission_overwrite(channel=channel, target=member)
    except Exception as e:
        await ctx.respond(f"There was an error removing the member")
        raise e

    await ctx.respond(f"Successfully removed {member.mention} from <#{channel.id}>", reply=True, user_mentions=True)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)