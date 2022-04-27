import hikari
import lightbulb
import random
import asyncio
import miru

plugin = lightbulb.Plugin("fun")
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./secrets/prefix") as f:
    prefix = f.read().strip()

@plugin.command()
@lightbulb.option("text", "text", type=str, required=False, default=None, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.command("howgay", "shows how gay you are", aliases=["gayrate"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _howgay(ctx: lightbulb.Context) -> None:
    text = ctx.options.text
    if text == None:
        text = ctx.event.message.author.username
    gayrate = random.randint(0, 100)
    embed = hikari.Embed(color=random.randint(0x0, 0xffffff), title="Gay rate", description=f"{text} is {gayrate}% gay :gay_pride_flag:")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.option("text", "text", type=str, required=False, default=None, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.command("simprate", "shows how simp you are", aliases=["simp"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _simprate(ctx: lightbulb.Context) -> None:
    text = ctx.options.text
    if text == None:
        text = ctx.event.message.author.username
    gayrate = random.randint(0, 100)
    embed = hikari.Embed(color=random.randint(0x0, 0xffffff), title="Simp rate", description=f"{text} is {gayrate}% simp")
    await ctx.respond(embed=embed)

# @plugin.command()
# @lightbulb.option("text", "text", type=str, required=False, default=None, modifier=lightbulb.commands.base.OptionModifier(3))
# @lightbulb.command("penis", "big or small penis", aliases=["pp"])
# @lightbulb.implements(lightbulb.PrefixCommand)
# async def _penis(ctx: lightbulb.Context) -> None:
#     text = ctx.options.text
#     if text == None:
#         text = ctx.event.message.author.username
#     gayrate = random.randint(0, 100)
#     embed = hikari.Embed(color=random.randint(0x0, 0xffffff), title="peepee size", description=f"{text} is {gayrate} gay :gay_pride_flag:")
#     await ctx.respond(embed=embed)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)