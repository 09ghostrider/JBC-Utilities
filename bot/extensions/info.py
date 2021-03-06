import hikari
import lightbulb
import random
import miru
import json
from bot.utils.checks import botban_check, jbc_server_check

plugin = lightbulb.Plugin("info")
plugin.add_checks(lightbulb.guild_only)
plugin.add_checks(botban_check)
plugin.add_checks(jbc_server_check)
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./configs/config.json") as f:
    bot_config = json.load(f)

@plugin.command()
@lightbulb.command("perks", "link to server perks")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _perks(ctx: lightbulb.Context) -> None:
    embed = hikari.Embed(
        title = "Server Perks",
        color = bot_config['color']['default'],
        description = """<#926112960315793458> contains all of the perks in the server.
Click the buttons below to jump to the respective perks.
Thank you for donating or investing in this server."""
    )

    view = miru.View()
    view.add_item(miru.Button(label="Investor Perks", url="https://discord.com/channels/832105614577631232/926112960315793458/974157215772602388"))
    view.add_item(miru.Button(label="Donor Perks", url="https://discord.com/channels/832105614577631232/926112960315793458/974157235603259402"))
    view.add_item(miru.Button(label="Booster Perks", url="https://discord.com/channels/832105614577631232/926112960315793458/974157254444073021"))
    view.add_item(miru.Button(label="Level Perks", url="https://discord.com/channels/832105614577631232/926112960315793458/974157268549521448"))

    await ctx.respond(embed=embed, components=view.build())
    
    try:
        await ctx.event.message.delete()
    except:
        pass

@plugin.command()
@lightbulb.command("iperks", "invensor perks")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _iperks(ctx: lightbulb.Context) -> None:
    embed = hikari.Embed(
        title = "Investor Perks",
        color = bot_config['color']['default'],
        description = """This is a list of the perks that you receive from investing in the server. To claim your perks, go to <#844158702906900500> and open a ticket.

<@&832111816339357701> **($10):**
<@&834994614376333312> role.
`&snipe` and `&afk` perms
Auto react

<@&832111852292800534> **($50):**
Bypass noumenon giveaways
Personal role
`&hl perms`

<@&832111893220556851> **($100):**
Private channel with 20 people
Text auto response
20 people in your personal role

<@&896591535355854869> **($200):**
Private channel with 50 people
+1 amari multi on your personal role
Bypass all giveaways

You can invest by DMing <@488132046087258112>.
Note: All perks last until you leave."""
    )

    await ctx.respond(embed=embed)
    
    try:
        await ctx.event.message.delete()
    except:
        pass


@plugin.command()
@lightbulb.command("dperks", "donor perks")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _dperks(ctx: lightbulb.Context) -> None:
    embed = hikari.Embed(
        title = "Donor Perks",
        color = bot_config['color']['default'],
        description = """This is a list of the perks that you receive from donating DMC or items. To claim your perks, go to <#844158702906900500> and open a ticket.

<@&851467779500802169> - Access to <#927064797219000330>.

<@&851467810713632808> - Access to <#927065062672306176> with a +2 amari multiplier.

<@&851631453414359071> - Access to the `&snipe` and `&afk` command.

<@&851631177085222952> - Private channel with 3 people.

<@&851631180336070739> - Auto react

<@&851631182776893482> - Text response

<@&954550639776657449> - Personal role with up to 10 people

<@&954550731921313792> - `&hl` perms

Note: All perks last until you leave"""
    )

    await ctx.respond(embed=embed)
    
    try:
        await ctx.event.message.delete()
    except:
        pass

@plugin.command()
@lightbulb.command("bperks", "booster perks")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _bperks(ctx: lightbulb.Context) -> None:
    embed = hikari.Embed(
        title = "Booster Perks",
        color = bot_config['color']['default'],
        description = """This is a list of the perks that you receive from boosting the server. To claim your perks, go to <#844158702906900500> and open a ticket.

<@&844180744917876768> **(1x boost):**
<@&834994614376333312> role.
`&snipe` and `&afk` perms
Auto react

<@&832111929056690187>  **(2x boost):**
Private channel with 5 people
`&hl` perms
Bypass noumenon giveaways


<@&832111960044077066> **(3x boost):**
Private channel with 10 people
Personal role with 10 people

Note: All perks last until you unboost """
    )

    await ctx.respond(embed=embed)
    
    try:
        await ctx.event.message.delete()
    except:
        pass

@plugin.command()
@lightbulb.command("lperks", "level perks")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _lperks(ctx: lightbulb.Context) -> None:
    embed = hikari.Embed(
        title = "Level Perks",
        color = bot_config['color']['default'],
        description = """This is a list of the perks that you receive from levelling up. They are automatically assigned.

<@&832109132038668338> - External Emoji and External Sticker permissions.

<@&832109184686227516> - Image and Embed permissions.

<@&832109251085729828> - `&afk` perms

<@&832109285239685173> `&snipe` perms

Note: All perks last until you leave."""
    )

    await ctx.respond(embed=embed)
    
    try:
        await ctx.event.message.delete()
    except:
        pass

@plugin.command()
@lightbulb.command("drules", "rules and information for dank memer")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _dkrules(ctx: lightbulb.Context) -> None:
    embed = hikari.Embed(
        title = "Rules and Information",
        color = bot_config['color']['default'],
        description = """This is a list of the rules and information needed in order to get access to this category. Please comply with them. You must also follow the rules of the server in <#832107000589844491>"""
    )

    embed.add_field(name="No scamming", value="""Scamming will not be tolerated in this server. However, if you are scammed, you will not be refunded. Although we will punish the scammer accordingly, your possessions will not be refunded unless the scammer voluntarily returns them.""")
    embed.add_field(name="No toxicity", value="""No toxicity will be allowed anywhere in the channels.""")
    embed.add_field(name="No spamming", value="""Do not spam the commands. Our antispam will kick in and you will be warned/muted.""")
    embed.add_field(name="Fight Fairly", value="""When using the fight channels, you must always have what you are fighting for on you. You must give what you lost immediately if you lose, or you will be punished accordingly.""")
    embed.add_field(name="Use Middleman", value="""Ping a moderator or above and get them to be a middleman for you when doing big trades.""")
    embed.add_field(name="Follow TOS", value="""Follow bot and discord TOS. You will be reported if you break any TOS.""")

    await ctx.respond(embed=embed)
    
    try:
        await ctx.event.message.delete()
    except:
        pass

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)