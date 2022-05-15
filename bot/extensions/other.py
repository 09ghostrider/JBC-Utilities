import hikari
import lightbulb
import random
import asyncio
import json
from requests import request
from bot.utils.checks import botban_check, jbc_server_check

plugin = lightbulb.Plugin("other")
plugin.add_checks(botban_check)
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./configs/config.json") as f:
    bot_config = json.load(f)

@plugin.command()
@lightbulb.command("ping", "Check the latency of the bot")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def _ping(ctx: lightbulb.Context) -> None:
    await ctx.respond(f"Latency: `{ctx.bot.heartbeat_latency*1000:.2f} ms`", reply=True)

@plugin.command()
@lightbulb.command("prefix", "Check the bot prefixes")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _prefix(ctx: lightbulb.Context) -> None:
    embed=hikari.Embed(title="Bot prefixes", description=f"""<@!{ctx.app.application.id}> (Mention prefix)\n{(str(bot_config['bot']['prefix'])[1:][:-1]).replace("'", "`")} (Prefixed commands)\n/ (Slash commands)""", color=bot_config["color"]["default"])
    await ctx.respond(embed=embed, reply=True)

@plugin.command()
@lightbulb.add_checks(jbc_server_check)
@lightbulb.command("vote", "vote for the server")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _vote(ctx: lightbulb.Context) -> None:
    blue_arrow = bot_config["emoji"]["blue_arrow"]
    embed=hikari.Embed(color=bot_config["color"]["default"], title=f"Voting for **{ctx.get_guild().name}**",description=f"""{blue_arrow} You can vote every **12h** on [**top.gg**](https://top.gg/servers/832105614577631232/vote)
{blue_arrow} Perks: <@&857221234373558273> (+1 amari multiplier)
{blue_arrow} Thank you for voting""")
    await ctx.respond(embed=embed)
    try:
        await ctx.event.message.delete()
    except:
        pass

@plugin.command()
@lightbulb.command("appeal", "link to the appeal server", aliases=['banappeal', 'appealserver'])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _appeal(ctx: lightbulb.Context) -> None:
    await ctx.respond("https://discord.gg/d4BwBUgSZK")

# @plugin.command()
# @lightbulb.command("info", "info about this bot")
# @lightbulb.implements(lightbulb.PrefixCommand)
# async def _info(ctx: lightbulb.Context) -> None:
#     embed = hikari.Embed(
#         title = "Information about this bot",
#         color = bot_config['color']['default'],
#         description = """➪ **Developer:** 09ghostrider#9999
# ➪ **Server:** https://discord.gg/1vs
# ➪ **Prefix:** `&`, `jbc `
# ➪ **Language:** Python
# ➪ **Library:** Hikari
# ➪ **GitHub:** https://github.com/09ghostrider/JBC-Utilities"""
#     )
#     await ctx.respond(embed=embed)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)