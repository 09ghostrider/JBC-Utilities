import hikari
import lightbulb
import random
import asyncio
import miru
import json
from bot.utils.checks import botban_check

plugin = lightbulb.Plugin("utility")
plugin.add_checks(botban_check)
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./configs/config.json") as f:
    bot_config = json.load(f)

@plugin.command()
@lightbulb.option("member", "the member to show", type=hikari.Member, required=False, default=None)
@lightbulb.command("avatar", "shows the members display avatar", aliases=["av"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _av(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    if member == None:
        member = ctx.event.message.member
    
    embed = hikari.Embed(color=bot_config['color']['default'], title=f"{member}'s avatar")
    embed.set_image(member.display_avatar_url)
    await ctx.respond(embed=embed, reply=True)

@plugin.command()
@lightbulb.option("user", "the user to show", type=hikari.User, required=False, default=None)
@lightbulb.command("banner", "shows the users banner")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _banner(ctx: lightbulb.Context) -> None:
    user = ctx.options.user
    if not user:
        user = ctx.event.message.author
    
    user = await ctx.app.rest.fetch_user(user.id)
    embed = hikari.Embed(color=bot_config['color']['default'], title=f"{user}'s banner")
    if user.banner_url != None:
        embed.set_image(user.banner_url)
    else:
        embed.description = "No banner set"
    await ctx.respond(embed=embed, reply=True)

@plugin.command()
@lightbulb.command("appeal", "link to the appeal server", aliases=['banappeal', 'appealserver'])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _appeal(ctx: lightbulb.Context) -> None:
    await ctx.respond("https://discord.gg/d4BwBUgSZK")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)