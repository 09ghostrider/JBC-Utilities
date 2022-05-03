import hikari
import lightbulb
import random
import asyncio
import json

from requests import request

plugin = lightbulb.Plugin("other")
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./configs/config.json") as f:
    bot_config = json.load(f)

@plugin.command()
@lightbulb.command("ping", "Check the latency of the bot")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _ping(ctx: lightbulb.Context) -> None:
    await ctx.respond(f"Latency: `{ctx.bot.heartbeat_latency*1000:.2f} ms`", reply=True)

@plugin.command()
@lightbulb.command("prefix", "Check the bot prefixes")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _prefix(ctx: lightbulb.Context) -> None:
    embed=hikari.Embed(title="Bot prefixes", description=f"<@!{ctx.app.application.id}> (Mention prefix)\n{bot_config['bot']['prefix']} (Prefixed commands)\n/ (Slash commands)", color=bot_config["color"]["default"])
    await ctx.respond(embed=embed, reply=True)

@plugin.command()
@lightbulb.command("vote", "vote for the server")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _vote(ctx:lightbulb.Context) -> None:
    blue_arrow = bot_config["emoji"]["blue_arrow"]
    embed=hikari.Embed(color=bot_config["color"]["default"], title=f"Voting for **{ctx.get_guild().name}**",description=f"""{blue_arrow} You can vote every **12h** on [**top.gg**](https://top.gg/servers/832105614577631232/vote)
{blue_arrow} Perks: <@&857221234373558273> (+1 amari multiplier)
{blue_arrow} Thank you for voting ❤️
""")
    await ctx.respond(embed=embed)
    try:
        await ctx.event.message.delete()
    except:
        pass

@plugin.command()
@lightbulb.command("enter", "indicates that u entered the chat")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _enter(ctx: lightbulb.Context) -> None:
    await ctx.respond(f"**{ctx.event.message.author.username}** has entered the chat {bot_config['emoji']['enter']}")
    try:
        await ctx.event.message.delete()
    except:
        pass

@plugin.command()
@lightbulb.command("exit", "indicates that u left the chat")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _exit(ctx: lightbulb.Context) -> None:
    await ctx.respond(f"**{ctx.event.message.author.username}** has left the chat {bot_config['emoji']['exit']}")
    try:
        await ctx.event.message.delete()
    except:
        pass

@plugin.command()
@lightbulb.option("member", "the member to yeet", default=None, required=False, type=hikari.Member)
@lightbulb.command("yeet", "yeet someone out from the server")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _yeet(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    if not member:
        member = ctx.event.message.member
    await ctx.respond(f"yeeted **{member.username}** out of **{ctx.get_guild().name}** {bot_config['emoji']['peepoyeet']}", reply=True)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)