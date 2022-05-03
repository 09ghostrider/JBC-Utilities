import hikari
import lightbulb
import random
import miru
import pymongo
from pymongo import MongoClient
import datetime
from miru.ext import nav

plugin = lightbulb.Plugin("donations")
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./secrets/prefix") as f:
    prefix = f.read().strip()

# with open("./secrets/db") as f:
#     mongoclient = f.read().strip()

class pingroles(miru.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[1]), style=hikari.ButtonStyle.PRIMARY, custom_id="832109776136568863", row=1)
    async def button_1(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(832109776136568863)
        embed = hikari.Embed(color = "2f3136")
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[2]), style=hikari.ButtonStyle.PRIMARY, custom_id="834014226699649035", row=1)
    async def button_2(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(834014226699649035)
        embed = hikari.Embed(color = "2f3136")
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)

    @miru.button(emoji=hikari.Emoji.parse(numemojis[3]), style=hikari.ButtonStyle.PRIMARY, custom_id="832109829946081301", row=1)
    async def button_3(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(832109829946081301)
        embed = hikari.Embed(color = "2f3136")
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[4]), style=hikari.ButtonStyle.PRIMARY, custom_id="849617885218996234", row=1)
    async def button_4(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(849617885218996234)
        embed = hikari.Embed(color = "2f3136")
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[5]), style=hikari.ButtonStyle.PRIMARY, custom_id="850012948390739988", row=2)
    async def button_5(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(850012948390739988)
        embed = hikari.Embed(color = "2f3136")
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[6]), style=hikari.ButtonStyle.PRIMARY, custom_id="850991787593302016", row=2)
    async def button_6(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(850991787593302016)
        embed = hikari.Embed(color = "2f3136")
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[7]), style=hikari.ButtonStyle.PRIMARY, custom_id="913265617254105128", row=2)
    async def button_7(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(913265617254105128)
        embed = hikari.Embed(color = "2f3136")
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[8]), style=hikari.ButtonStyle.PRIMARY, custom_id="951694220345880596", row=2)
    async def button_8(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(951694220345880596)
        embed = hikari.Embed(color = "2f3136")
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)

@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("pingroles", "get ping roles", aliases=["pr"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _pingrole(ctx: lightbulb.Context) -> None:
    try:
        await ctx.event.message.delete()
    except:
        pass

    embed = hikari.Embed(
        title = "<a:preparing:943820731043696671> PING ROLES <a:preparing:943820731043696671>",
        description = f"""{numemojis[1]}: <@&832109776136568863>
{numemojis[2]}: <@&834014226699649035>
{numemojis[3]}: <@&832109829946081301>
{numemojis[4]}: <@&849617885218996234>
{numemojis[5]}: <@&850012948390739988>
{numemojis[6]}: <@&850991787593302016>
{numemojis[7]}: <@&913265617254105128>
{numemojis[8]}: <@&951694220345880596>""",
        color = "2f3136"
    )
    embed.set_thumbnail(ctx.get_guild().icon_url)
    view = pingroles()
    msg = await ctx.respond(embed=embed, components=view.build())
    view.start(await msg.message())

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)