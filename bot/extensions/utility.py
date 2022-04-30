import hikari
import lightbulb
import random
import asyncio
import miru

plugin = lightbulb.Plugin("utility")
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./secrets/prefix") as f:
    prefix = f.read().strip()

@plugin.command()
@lightbulb.option("member", "the member to show", type=hikari.Member, required=False, default=None)
@lightbulb.command("avatar", "shows the members display avatar", aliases=["av"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _av(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    if member == None:
        member = ctx.event.message.member
    
    embed = hikari.Embed(color=random.randint(0x0, 0xffffff), title=f"{member}'s avatar")
    embed.set_image(member.display_avatar_url)
    await ctx.respond(embed=embed, reply=True)

# @plugin.command()
# @lightbulb.option("member", "the member to show", type=hikari.Member, required=False, default=None)
# @lightbulb.command("banner", "shows the members display banner")
# @lightbulb.implements(lightbulb.PrefixCommand)
# async def _banner(ctx: lightbulb.Context) -> None:
#     member = ctx.options.member
#     if not member:
#         member = ctx.event.message.member
    
#     embed = hikari.Embed(color=random.randint(0x0, 0xffffff), title=f"{member}'s banner")
#     if member.banner_url != None:
#         embed.set_image(member.banner_url)
#     else:
#         embed.description = "No banner set"
#     await ctx.respond(embed=embed, reply=True)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)