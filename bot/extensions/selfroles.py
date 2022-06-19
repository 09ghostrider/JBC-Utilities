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
    1: "<:_one_:988023950632185886>",
    2: "<:_two_:988023934983237632>",
    3: "<:_three_:988023923046236200>",
    4: "<:_four_:988023910467522560>",
    5: "<:_five_:988023893732237383>",
    6: "<:_six_:988023875814170654>",
    7: "<:_seven_:988023864233701376>",
    8: "<:_eight_:988023842326851604>",
    9: "<:_nine_:988023828712161290>",
    10: "<:_ten_:988023815554617354>"
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
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[1]), style=hikari.ButtonStyle.SECONDARY, custom_id="832109776136568863", row=1)
    async def button_1(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(832109776136568863)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[2]), style=hikari.ButtonStyle.SECONDARY, custom_id="834014226699649035", row=1)
    async def button_2(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(834014226699649035)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)

    @miru.button(emoji=hikari.Emoji.parse(numemojis[3]), style=hikari.ButtonStyle.SECONDARY, custom_id="832109829946081301", row=1)
    async def button_3(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(832109829946081301)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[4]), style=hikari.ButtonStyle.SECONDARY, custom_id="849617885218996234", row=1)
    async def button_4(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(849617885218996234)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[5]), style=hikari.ButtonStyle.SECONDARY, custom_id="850012948390739988", row=1)
    async def button_5(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(850012948390739988)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
class bioroles(miru.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[1]), style=hikari.ButtonStyle.SECONDARY, custom_id="936928572877209641", row=1)
    async def button_1(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(936928572877209641)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[2]), style=hikari.ButtonStyle.SECONDARY, custom_id="936928600341508126", row=1)
    async def button_2(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(936928600341508126)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)

    @miru.button(emoji=hikari.Emoji.parse(numemojis[3]), style=hikari.ButtonStyle.SECONDARY, custom_id="936928617374564382", row=1)
    async def button_3(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(936928617374564382)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)

class colorroles(miru.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[1]), style=hikari.ButtonStyle.SECONDARY, custom_id="987598471768989697", row=1)
    async def button_1(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(987598471768989697)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[2]), style=hikari.ButtonStyle.SECONDARY, custom_id="987598639088152596", row=1)
    async def button_2(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(987598639088152596)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)

    @miru.button(emoji=hikari.Emoji.parse(numemojis[3]), style=hikari.ButtonStyle.SECONDARY, custom_id="987598764107792444", row=1)
    async def button_3(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(987598764107792444)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[4]), style=hikari.ButtonStyle.SECONDARY, custom_id="987599242401034310", row=1)
    async def button_4(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(987599242401034310)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[5]), style=hikari.ButtonStyle.SECONDARY, custom_id="987599561130381323", row=1)
    async def button_5(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(987599561130381323)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[6]), style=hikari.ButtonStyle.SECONDARY, custom_id="987599090818875442", row=2)
    async def button_6(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(987599090818875442)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[7]), style=hikari.ButtonStyle.SECONDARY, custom_id="987598830256152576", row=2)
    async def button_7(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(987598830256152576)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[8]), style=hikari.ButtonStyle.SECONDARY, custom_id="987599062519939102", row=2)
    async def button_8(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(987599062519939102)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[9]), style=hikari.ButtonStyle.SECONDARY, custom_id="987599607263535114", row=2)
    async def button_9(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(987599607263535114)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)
    
    @miru.button(emoji=hikari.Emoji.parse(numemojis[10]), style=hikari.ButtonStyle.SECONDARY, custom_id="987598400520343622", row=2)
    async def button_10(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        role = self.app.cache.get_role(987598400520343622)
        embed = hikari.Embed(color = role.color)
        if role not in ctx.member.get_roles():
            await ctx.member.add_role(role)
            embed.description = f"Added {role.mention} to you"
        else:
            await ctx.member.remove_role(role)
            embed.description = f"Removed {role.mention} from you"
        await ctx.respond(embed=embed, flags=ephemeral)

@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("pingroles", "get ping roles", aliases=["pr", "pingrole", "proles"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _pingroles(ctx: lightbulb.Context) -> None:
    try:
        await ctx.event.message.delete()
    except:
        pass

    embed = hikari.Embed(
        title = "PING ROLES",
        description = f"""{numemojis[1]}: <@&832109776136568863>
{numemojis[2]}: <@&834014226699649035>
{numemojis[3]}: <@&832109829946081301>
{numemojis[4]}: <@&849617885218996234>
{numemojis[5]}: <@&850012948390739988>""",
        color = bot_config['color']['default']
    )
    embed.set_image("https://media.discordapp.net/attachments/804978370050916362/971477192208973884/Tumblr_l_1076311018323767.gif")
    view = pingroles()
    msg = await ctx.respond(embed=embed, components=view.build())
    view.start(await msg.message())

@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("bioroles", "get bio roles", aliases=["br", "biorole", "broles"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _bioroles(ctx: lightbulb.Context) -> None:
    try:
        await ctx.event.message.delete()
    except:
        pass

    embed = hikari.Embed(
        title = "BIO ROLES",
        description = f"""{numemojis[1]}: <@&936928572877209641>
{numemojis[2]}: <@&936928600341508126>
{numemojis[3]}: <@&936928617374564382>""",
        color = bot_config['color']['default']
    )
    embed.set_image("https://media.discordapp.net/attachments/804978370050916362/971477192208973884/Tumblr_l_1076311018323767.gif")
    view = bioroles()
    msg = await ctx.respond(embed=embed, components=view.build())
    view.start(await msg.message())

@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("colorroles", "get color roles", aliases=["cr", "colorrole", "croles", "colourroles"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _colorroles(ctx: lightbulb.Context) -> None:
    try:
        await ctx.event.message.delete()
    except:
        pass

    embed = hikari.Embed(
        title = "COLOR ROLES",
        description = f"""{numemojis[1]}: <@&987598471768989697>
{numemojis[2]}: <@&987598639088152596>
{numemojis[3]}: <@&987598764107792444>
{numemojis[4]}: <@&987599242401034310>
{numemojis[5]}: <@&987599561130381323>
{numemojis[6]}: <@&987599090818875442>
{numemojis[7]}: <@&987598830256152576>
{numemojis[8]}: <@&987599062519939102>
{numemojis[9]}: <@&987599607263535114>
{numemojis[10]}: <@&987598400520343622>""",
        color = bot_config['color']['default']
    )
    embed.set_image("https://media.discordapp.net/attachments/804978370050916362/971477192208973884/Tumblr_l_1076311018323767.gif")
    view = colorroles()
    msg = await ctx.respond(embed=embed, components=view.build())
    view.start(await msg.message())

@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("selfroles", "get self roles", aliases=["sr", "selfrole", "sroles"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _selfroles(ctx: lightbulb.Context) -> None:
    try:
        await ctx.event.message.delete()
    except:
        pass

    embed = hikari.Embed(color = bot_config['color']['default'])
    embed.set_image("https://media.discordapp.net/attachments/957710808119398430/988019246548254780/unknown.png")
    await ctx.respond(embed=embed)

    embed = hikari.Embed(
        title = "COLOR ROLES",
        description = f"""{numemojis[1]}: <@&987598471768989697>
{numemojis[2]}: <@&987598639088152596>
{numemojis[3]}: <@&987598764107792444>
{numemojis[4]}: <@&987599242401034310>
{numemojis[5]}: <@&987599561130381323>
{numemojis[6]}: <@&987599090818875442>
{numemojis[7]}: <@&987598830256152576>
{numemojis[8]}: <@&987599062519939102>
{numemojis[9]}: <@&987599607263535114>
{numemojis[10]}: <@&987598400520343622>""",
        color = bot_config['color']['default']
    )
    embed.set_image("https://media.discordapp.net/attachments/804978370050916362/971477192208973884/Tumblr_l_1076311018323767.gif")
    view = colorroles()
    msg = await ctx.respond(embed=embed, components=view.build())
    view.start(await msg.message())

    embed = hikari.Embed(
        title = "BIO ROLES",
        description = f"""{numemojis[1]}: <@&936928572877209641>
{numemojis[2]}: <@&936928600341508126>
{numemojis[3]}: <@&936928617374564382>""",
        color = bot_config['color']['default']
    )
    embed.set_image("https://media.discordapp.net/attachments/804978370050916362/971477192208973884/Tumblr_l_1076311018323767.gif")
    view = bioroles()
    msg = await ctx.respond(embed=embed, components=view.build())
    view.start(await msg.message())

    embed = hikari.Embed(
        title = "PING ROLES",
        description = f"""{numemojis[1]}: <@&832109776136568863>
{numemojis[2]}: <@&834014226699649035>
{numemojis[3]}: <@&832109829946081301>
{numemojis[4]}: <@&849617885218996234>
{numemojis[5]}: <@&850012948390739988>""",
        color = bot_config['color']['default']
    )
    embed.set_image("https://media.discordapp.net/attachments/804978370050916362/971477192208973884/Tumblr_l_1076311018323767.gif")
    view = pingroles()
    msg = await ctx.respond(embed=embed, components=view.build())
    view.start(await msg.message())

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command("verify", "shows the verify embed")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _verify(ctx: lightbulb.Context) -> None:
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
@lightbulb.command("karutaaccess", "sends the karuta access embed")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _karutaccess(ctx: lightbulb.Context) -> None:
    try:
        await ctx.event.message.delete()
    except:
        pass

    embed = hikari.Embed(title="Karuta access", description=f"""Click the {bot_config['emoji']['karuta']} button to gain access to the channels.\nBe sure to read the rules.""", color=bot_config['color']['default'])
    embed.set_thumbnail(ctx.get_guild().icon_url)
    view = karutaaccess()
    msg = await ctx.respond(embed=embed, components=view.build())
    view.start(await msg.message())

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)