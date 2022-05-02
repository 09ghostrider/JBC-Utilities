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
    await ctx.respond(f"Latency: `{ctx.bot.heartbeat_latency*1000:.2f} ms`", reply=True)

@plugin.command()
@lightbulb.command("prefix", "Check the bot prefixes")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _prefix(ctx: lightbulb.Context) -> None:
    embed=hikari.Embed(title="Bot prefixes", description=f"<@!959029004579516457> (Mention prefix)\n`jbc `, `{prefix}` (Prefixed commands)\n/ (Slash commands)", color=random.randint(0x0, 0xffffff))
    await ctx.respond(embed=embed, reply=True)

@plugin.command()
@lightbulb.command("vote", "vote for the server")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _vote(ctx:lightbulb.Context) -> None:
    embed=hikari.Embed(color="48087C", description=f"""<a:purple_arrow:970550202823999508> Voting for **{ctx.get_guild().name}**
<a:purple_arrow:970550202823999508> You can vote every **12h** on [**top.gg**](https://top.gg/servers/832105614577631232/vote)
<a:purple_arrow:970550202823999508> Perks: <@&857221234373558273> (+1 amari multiplier)
<a:purple_arrow:970550202823999508> Thank you for voting
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
    await ctx.respond(f"**{ctx.event.message.author.username}** has entered the chat <a:JBC_enter:970541921451790346>")
    try:
        await ctx.event.message.delete()
    except:
        pass

@plugin.command()
@lightbulb.command("exit", "indicates that u left the chat")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _exit(ctx: lightbulb.Context) -> None:
    await ctx.respond(f"**{ctx.event.message.author.username}** has left the chat <a:JBC_exit:951107886606614549>")
    try:
        await ctx.event.message.delete()
    except:
        pass

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)