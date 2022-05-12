from operator import le
import hikari
import lightbulb
import random
import miru
import pymongo
from pymongo import MongoClient
import datetime
from miru.ext import nav
import json
from bot.utils.checks import botban_check, jbc_server_check

plugin = lightbulb.Plugin("donations")
plugin.add_checks(jbc_server_check)
plugin.add_checks(botban_check)
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./configs/config.json") as f:
    bot_config = json.load(f)

numemojis = {
    0: "<a:_0_:956584073084674049>",
    1: "<a:_1_:956583838992187483>",
    2: "<a:_2_:956583892951912488>",
    3: "<a:_3_:956583961944023141>",
    4: "<a:_4_:956583976733122570>",
    5: "<a:_5_:956583995125157948>",
    6: "<a:_6_:956584014758699079>",
    7: "<a:_7_:956584029338091520>",
    8: "<a:_8_:956584045087715418>",
    9: "<a:_9_:956584058966650950>"
}

class verify(miru.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
    
    @miru.button(emoji=hikari.Emoji.parse(bot_config['emoji']['tickmark']), label="Verify", style=hikari.ButtonStyle.SUCCESS, custom_id="verify")
    async def verify_button(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(832108400129212438)
        if role not in ctx.member.get_roles():
            await ctx.respond("You are now verified", flags=ephemeral)
            await ctx.member.add_role(role)
        else:
            await ctx.respond("You are already verified", flags=ephemeral)

class dankaccess(miru.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
    
    @miru.button(emoji=hikari.Emoji.parse(bot_config['emoji']['clap']), label="Gain Access", style=hikari.ButtonStyle.SUCCESS, custom_id="dankaccess")
    async def verify_button(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(888028007783100426)
        if role not in ctx.member.get_roles():
            await ctx.respond("You now have access to dank memer channels", flags=ephemeral)
            await ctx.member.add_role(role)
        else:
            await ctx.respond("You dont have access to dank memer channels anymore", flags=ephemeral)
            await ctx.member.remove_role(role)

class karutaaccess(miru.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
    
    @miru.button(emoji=hikari.Emoji.parse(bot_config['emoji']['karuta']), label="Gain Access", style=hikari.ButtonStyle.SUCCESS, custom_id="karutaaccess")
    async def verify_button(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(973792910774509698)
        if role not in ctx.member.get_roles():
            await ctx.respond("You now have access to karuta channels", flags=ephemeral)
            await ctx.member.add_role(role)
        else:
            await ctx.respond("You dont have access to karuta channels anymore", flags=ephemeral)
            await ctx.member.remove_role(role)

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
        color = bot_config['color']['default']
    )
    embed.set_thumbnail(ctx.get_guild().icon_url)
    view = pingroles()
    msg = await ctx.respond(embed=embed, components=view.build())
    view.start(await msg.message())

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command("verify", "shows the verify embed")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _verify(ctx: lightbulb.Context) -> None:
    if ctx.event.message.channel_id != 834009679553101854:
        return await ctx.respond(f"This command can only be used in <#834009679553101854>", reply=True)
    
    try:
        await ctx.event.message.delete()
    except:
        pass

    embed = hikari.Embed(title="Verification", description="Make sure to read <#832107000589844491> before verifying.\nClick the button below to verify.\nEnjoy your stay here!!", color=bot_config['color']['default'])
    embed.set_thumbnail(ctx.get_guild().icon_url)
    view = verify()
    msg = await ctx.respond(embed=embed, components=view.build())
    view.start(await msg.message())

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command("dankaccess", "sends the dank access embed")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _dankaccess(ctx: lightbulb.Context) -> None:
    if ctx.event.message.channel_id != 852396608440107048:
        return await ctx.respond("This command can only be used in <#852396608440107048>", reply=True)

    try:
        await ctx.event.message.delete()
    except:
        pass

    embed = hikari.Embed(title="Dank Memer access", description=f"""Click the {bot_config['emoji']['clap']} button to gain access to the channels.\nBe sure to read the rules.\nDank channels also include <#851315401459892245>, <#933855270826807308> and <#945812242857865276>""", color=bot_config['color']['default'])
    embed.set_thumbnail(ctx.get_guild().icon_url)
    view = dankaccess()
    msg = await ctx.respond(embed=embed, components=view.build())
    view.start(await msg.message())

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command("karutaaccess", "sends the dank access embed")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _dankaccess(ctx: lightbulb.Context) -> None:
    if ctx.event.message.channel_id != 974227197181173760:
        return await ctx.respond("This command can only be used in <#974227197181173760>", reply=True)

    try:
        await ctx.event.message.delete()
    except:
        pass

    embed = hikari.Embed(title="Karuta access", description=f"""Click the {bot_config['emoji']['karuta']} button to gain access to the channels.\nBe sure to read the rules.""", color=bot_config['color']['default'])
    view = karutaaccess()
    msg = await ctx.respond(embed=embed, components=view.build())
    view.start(await msg.message())

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)