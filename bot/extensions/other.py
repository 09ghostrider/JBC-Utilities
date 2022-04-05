import hikari
import lightbulb
import random
import asyncio

plugin = lightbulb.Plugin("other")
ephemeral = hikari.MessageFlag.EPHEMERAL

@plugin.command()
@lightbulb.command("ping", "Check the latency of the bot")
@lightbulb.implements(lightbulb.SlashCommand)
async def _ping(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE, flags=ephemeral)
    await ctx.respond(f"Latency: `{round(ctx.bot.heartbeat_latency*1000, 2)} ms`", flags=ephemeral)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)