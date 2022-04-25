import hikari
import lightbulb
import random
import miru
import pymongo
from pymongo import MongoClient
import datetime

plugin = lightbulb.Plugin("mod")

with open("./secrets/prefix") as f:
    prefix = f.read().strip()

@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
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
        await ctx.respond(f"successfully dmed {user.mention}", reply=True)
    except Exception as e:
        await ctx.respond(f"{e}", reply=True)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)