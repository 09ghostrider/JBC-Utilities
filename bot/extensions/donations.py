import hikari
import lightbulb
import random
import miru
import json
from bot.utils.checks import botban_check, jbc_server_check

plugin = lightbulb.Plugin("donos")
plugin.add_checks(lightbulb.guild_only)
plugin.add_checks(botban_check)
plugin.add_checks(jbc_server_check)
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./configs/config.json") as f:
    bot_config = json.load(f)

class claim_button(miru.Button):
    def __init__(self, cmd) -> None:
        super().__init__(label="Claim", emoji=hikari.Emoji.parse(bot_config['emoji']['check']), style=hikari.ButtonStyle.SECONDARY)
        self.cmd = cmd
    
    async def callback(self, ctx: miru.Context) -> None:
        await ctx.respond(f"```{self.cmd}```", flags=ephemeral)
        self.view.gman = ctx.interaction.user
        self.view.stop()
    
    async def view_check(self, ctx: miru.Context):
        gman = ctx.app.cache.get_role(832108169441574914)
        if gman in ctx.member.get_roles() or hikari.Permissions.ADMINISTRATOR in ctx.member.permissions:
            return True
        else:
            await ctx.respond("This is not for you.", fags=ephemeral)
            return False

@plugin.command()
@lightbulb.option("options", "the options for this giveaway", type=str, required=True, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.command("gdonate", "donate for a giveaway")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _gdonate(ctx: lightbulb.Context) -> None:
    if ctx.event.message.channel_id != 988292664032120832:
        return await ctx.respond("This command can only be used in <#988292664032120832>", reply=True)
    
    options = ctx.options.options
    options = options.split("/", 4)
    if len(options) < 5:
        return await ctx.respond("Please include all the options\nUse 'None' instead of leaving the option empty", reply=True)

    try:
        await ctx.event.message.delete()
    except:
        pass

    embed=hikari.Embed(title="GIVEAWAY DONATION", color=bot_config["color"]["default"])
    embed.description = f"""{bot_config['emoji']['reply2']} **Duration:** {options[0]}
{bot_config['emoji']['reply2']} **Prize:** {options[1]}
{bot_config['emoji']['reply2']} **Winners:** {options[2]}
{bot_config['emoji']['reply2']} **Requirements:** {options[3]}
{bot_config['emoji']['reply2']} **Message:** {options[4]}
{bot_config['emoji']['reply']} **Donor:** {ctx.event.message.author}"""

    cmd = f"+gstart {options[0]} {options[2]} {options[3]} {options[1]} --donor {ctx.event.message.author.id} --msg {options[4]} --ping"

    view = miru.View(timeout=None)
    view.add_item(claim_button(cmd))
    msg = await ctx.app.rest.create_message(ctx.get_guild().get_channel(ctx.event.message.channel_id), "<@&832108169441574914>", embed=embed, role_mentions=True, components=view.build())

    view.start(msg)
    await view.wait()

    view2 = miru.View()
    view2.add_item(miru.Button(label="Claimed", emoji=hikari.Emoji.parse(bot_config['emoji']['check']), disabled=True, style=hikari.ButtonStyle.SECONDARY))

    embed.set_footer(text=f"Claimed by {view.gman}", icon=view.gman.avatar_url)
    await msg.edit(content="<@&832108169441574914>", embed=embed, components=view2.build())

@plugin.command()
@lightbulb.command("ginfo", "shows information on how to donate")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _ginfo(ctx: lightbulb.Context) -> None:
    br_dot = bot_config["emoji"]["brown_dot"]
    embed=hikari.Embed(title=f"How to donate for giveaways {bot_config['emoji']['moneygun']}", color=bot_config["color"]["default"])
    embed.description = f"""If you would like to donate to giveaways please use the command:

**&gdonate duration/prize/winners/requirements/message**
eg: &gdonate 1h/1 tro/1w/level 5/I love donating to JBC!
eg: &gdonate 6h/1 tro 5 pem/level 15 5m donor/This is how to donate multiple items or multiple requirements.

{br_dot} Minimum donation amount is **500k**.
{br_dot} Note that / will end your argument. For donating multiple items, refrain from using a /.
{br_dot} All fields are required. Use a None instead of leaving it empty.
{br_dot} A giveaway manager will then respond as soon as possible, please do not ping them.
{br_dot} If you would like to leave an area blank, just type **None**.
{br_dot} If you would like to donate for nitro giveaways, please dm <@!488132046087258112>."""
    embed.set_footer(text="Thank you for donating!", icon=ctx.get_guild().icon_url)
    await ctx.respond(embed=embed)

    try:
        await ctx.event.message.delete()
    except:
        pass

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)