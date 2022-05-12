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

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.MANAGE_GUILD))
@lightbulb.option("text", "the embed content", required=True, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.option("channel", "the channel to send the embed in", type=hikari.GuildChannel, required=False, default=None)
@lightbulb.command("embed", "Creates an embed with the specified color in the specified channel, separate the title from the description with |")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _embed(ctx: lightbulb.Context) -> None:
    channel = ctx.options.channel
    text = ctx.options.text

    if not channel:
        cid = ctx.event.message.channel_id
    else:
        cid = channel.id
    
    title, description = text.split("|", 1)

    embed = hikari.Embed(title=title, description=description, color=bot_config['color']['default'])
    await ctx.app.rest.create_message(cid, embed=embed)


def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)