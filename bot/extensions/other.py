import hikari
import lightbulb
import random

plugin = lightbulb.Plugin("other")

@plugin.command()
@lightbulb.command("ping", "Check the latency of the bot")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _ping(ctx: lightbulb.Context) -> None:
    await ctx.respond(f"Latency: `{round(ctx.bot.heartbeat_latency*1000, 2)} ms`")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)