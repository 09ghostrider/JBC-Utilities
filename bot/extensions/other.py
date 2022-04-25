import hikari
import lightbulb
import random
import asyncio

plugin = lightbulb.Plugin("other")
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./secrets/prefix") as f:
    prefix = f.read().strip()

@plugin.command()
@lightbulb.command("ping", "Check the latency of the bot")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def _ping(ctx: lightbulb.Context) -> None:
    try:
        await ctx.respond(f"Latency: `{ctx.bot.heartbeat_latency*1000:.2f} ms`", flags=ephemeral, reply=True)
    except:
        await ctx.respond(f"Latency: `{ctx.bot.heartbeat_latency*1000:.2f} ms`", reply=True)

@plugin.command()
@lightbulb.command("prefix", "Check the bot prefixes")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def _prefix(ctx: lightbulb.Context) -> None:
    embed=hikari.Embed(title="Bot prfixes", description=f"<@!959029004579516457> (Mention prefix)\n{prefix} (Prefixed commands)\n/ (Slash commands)", color=random.randint(0x0, 0xffffff))
    await ctx.respond(embed=embed, reply=True)
def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)