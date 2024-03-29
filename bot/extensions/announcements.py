import hikari
import lightbulb
import random
import miru
import json
import asyncio
import datetime
from bot.utils.checks import botban_check, jbc_server_check
from bot.utils.funcs import edit_perms

plugin = lightbulb.Plugin("announcements")
plugin.add_checks(lightbulb.guild_only)
plugin.add_checks(botban_check)
plugin.add_checks(jbc_server_check)
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./configs/config.json") as f:
    bot_config = json.load(f)

@plugin.command()
@lightbulb.add_checks(lightbulb.has_roles(832111569764352060) | lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option("message", "message to include while pinging", required=False, type=str, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.command("gping", "ping the giveaway ping role")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _gping(ctx: lightbulb.Context) -> None:
    if ctx.event.message.channel_id != 851315401459892245:
        return await ctx.respond("This command can only be used in <#851315401459892245>", reply=True)

    try:
        await ctx.event.message.delete()
    except:
        pass
    
    text = "" if not ctx.options.message else f": {ctx.options.message}"
    await ctx.respond(f"<@&850991787593302016>{text}", role_mentions=True)

@plugin.command()
@lightbulb.add_checks(lightbulb.has_roles(832111569764352060) | lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option("message", "message to include while pinging", required=False, type=str, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.command("eping", "ping the event ping role")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _gping(ctx: lightbulb.Context) -> None:
    if ctx.event.message.channel_id != 933855270826807308:
        return await ctx.respond("This command can only be used in <#933855270826807308>", reply=True)

    try:
        await ctx.event.message.delete()
    except:
        pass
    
    text = "" if not ctx.options.message else f": {ctx.options.message}"
    await ctx.respond(f"<@&832109829946081301>{text}", role_mentions=True)

@plugin.command()
@lightbulb.add_cooldown(300, 1, lightbulb.buckets.GuildBucket)
@lightbulb.add_checks(lightbulb.has_roles(901767319716524085, 832108259221307392, mode=any) | lightbulb.owner_only)
@lightbulb.option("message", "donors message", required=True, type=str, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.option("requirements", "the requirements for this giveaway", required=False, type=hikari.Role, modifier=lightbulb.commands.base.OptionModifier(2))
@lightbulb.option("donor", "the donor of this heist", required=True, type=hikari.Member)
@lightbulb.option("amount", "the heist amount", required=True, type=str)
@lightbulb.command("heist", "ping the heist ping and start a heist")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _heist(ctx: lightbulb.Context) -> None:
    if ctx.event.message.channel_id != 945812242857865276:
        return await ctx.respond("This command can only be used in <#945812242857865276>", reply=True)
    
    amount = ctx.options.amount
    donor = ctx.options.donor
    reqs = ctx.options.requirements
    message = ctx.options.message

    dankaccess = 888028007783100426
    heistping = 951694220345880596
    duration = 60

    try:
        amount = int(amount)
    except:
        try:
            if "e" in amount:
                first_digit, how_many_zeros = amount.split("e")
                amount = int(f"{first_digit}{'0' * int(how_many_zeros)}")
            else:
                return await ctx.respond("Invalid amount", reply=True)
        except:
            return await ctx.respond("Invalid amount", reply=True)

    if amount <= 0:
        return await ctx.respond("Invalid amount", reply=True)
    
    if donor.is_bot == True or donor.is_system == True:
        return await ctx.respond("Bots cant be donors", reply=True)

    try:
        await ctx.event.message.delete()
    except:
        pass

    reqs_str = ""
    if reqs != []:
        for r in reqs:
            reqs_str += f"{str(r.mention)}, "
        reqs_str = reqs_str[:-2]
    else:
        reqs_str = "None"

    guild = ctx.get_guild()

    embed = hikari.Embed(
        color = bot_config['color']['default'],
        title = "HEIST STARTING",
        description = f"""{bot_config['emoji']['blue_arrow2']} **Amount:** {amount:,}
{bot_config['emoji']['blue_arrow2']} **Donor:** {donor.mention}
{bot_config['emoji']['blue_arrow2']} **Requirements:** {reqs_str}
{bot_config['emoji']['blue_arrow2']} **Message:** {message}"""
    )

    embed_msg = await ctx.respond(embed=embed)
    ping_msg = await ctx.respond(f"<@&{heistping}> **Heist starting in {duration} seconds**", role_mentions=True)
    ping_msg2 = await ping_msg.message()

    await (ping_msg2).add_reaction("⏰")

    for r in range(int(duration/2)):
        await asyncio.sleep(2)
        await ping_msg2.edit(f"<@&{heistping}> Heist starting in **{duration-(r*2)-2}** seconds!", role_mentions=True)
    await ping_msg2.edit(f"<@&{heistping}> Heist starting!", role_mentions=True)

    if reqs != []:
        await edit_perms(ctx, "lock", ctx.event.message.channel_id, dankaccess, hikari.Permissions.VIEW_CHANNEL)
        for r in reqs:
            await edit_perms(ctx, "unlock", ctx.event.message.channel_id, r.id, hikari.Permissions.VIEW_CHANNEL)

    reactions = await ctx.app.rest.fetch_reactions_for_emoji(channel=ctx.event.message.channel_id, message=ping_msg2, emoji="⏰")
    
    pings = ""
    for y in reactions:
        pings += str(y.mention)
    try:
        await ctx.respond(pings, delete_after=1, user_mentions=True)
    except:
        pass

    await ctx.respond(f"{ctx.event.message.author.mention} please begin the heist", user_mentions=True)

    while True:
        try:
            event = await ctx.app.wait_for(
                hikari.GuildMessageCreateEvent, 
                timeout = 300, 
                predicate = lambda event: (
                    event.guild_id == ctx.event.message.guild_id 
                    and event.message.channel_id == ctx.event.message.channel_id
                    and event.author_id == 270904126974590976
                )
            )
            msg = await ctx.app.rest.fetch_message(ctx.channel_id, event.message.id)
            if msg.embeds != []:
                if msg.embeds[0].title == f"**{ctx.event.message.author.username}** is starting a bank robbery":
                    heist = msg
                    break

        except asyncio.TimeoutError:
            await ctx.respond("No heist delected, resettings channel.")
            if reqs != []:
                await edit_perms(ctx, "unlock", ctx.event.message.channel_id, dankaccess, hikari.Permissions.VIEW_CHANNEL)
                for r in reqs:
                    await edit_perms(ctx, "reset", ctx.event.message.channel_id, r.id, hikari.Permissions.VIEW_CHANNEL)
            return await ctx.respond("Channel reset comepete, ready for next heist.")
    
    heist_detect = await ctx.respond(f"Heist time remaining: <t:{round((heist.created_at+datetime.timedelta(seconds=90)).timestamp())}:R>.", reply=heist)
    heist_detect_msg = await heist_detect.message()

    await asyncio.sleep(90)
    try:
        await heist_detect_msg.edit(f"Heist time remaining: Heist ended.")
    except:
        pass

    if reqs != []:
        await edit_perms(ctx, "unlock", ctx.event.message.channel_id, dankaccess, hikari.Permissions.VIEW_CHANNEL)
        for r in reqs:
            await ctx.bot.rest.delete_permission_overwrite(channel=ctx.event.message.channel_id, target=r)
    await ctx.respond("Channel reset comepete, ready for next heist.")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)