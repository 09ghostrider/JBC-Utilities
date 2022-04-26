from distutils.command import build
import hikari
import lightbulb
import random
import asyncio
import miru

plugin = lightbulb.Plugin("donations")
ephemeral = hikari.MessageFlag.EPHEMERAL
br_dot = "<a:br_dot:968570379113214072>"

with open("./secrets/prefix") as f:
    prefix = f.read().strip()

@lightbulb.Check
def dono_channel(ctx: lightbulb.Context) -> None:
    return ctx.event.message.channel_id == 851315417334677514

class claim_button(miru.Button):
    def __init__(self, cmd) -> None:
        super().__init__(label="Claim", emoji=hikari.Emoji.parse("<a:JBC_check:907203988468928522>"), style=hikari.ButtonStyle.SECONDARY)
        self.cmd = cmd
    
    async def callback(self, ctx: miru.Context) -> None:
        await ctx.respond(f"```{self.cmd}```", flags=ephemeral)
        self.view.gman = ctx.interaction.user
        self.view.stop()

@plugin.command()
@lightbulb.add_checks(dono_channel)
@lightbulb.option("message", "any optional message", type=str, required=False, default=None, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.option("requirements", "the requirements for the giveaway", type=str, required=False, default=None)
@lightbulb.option("winners", "the number of winners", type=str, required=False, default=1)
@lightbulb.option("prize", "the prize of the giveaway", type=str, required=True)
@lightbulb.option("duration", "the duration of the giveaway", type=str, required=True)
@lightbulb.command("gdonate", "donate for a giveaway")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _gdonate(ctx: lightbulb.Context) -> None:
    try:
        await ctx.event.message.delete()
    except:
        pass

    c = random.randint(0x0, 0xffffff)
    
    embed=hikari.Embed(title="New giveaway donation <a:JBC_moneygun:968522741839986708>", color=c)
    embed.description = f"""**Duration:** {ctx.options.duration}
**Prize:** {ctx.options.prize}
**Winners:** {ctx.options.winners}
**Requirements:** {ctx.options.requirements}
**Message:** {ctx.options.message}
**Donor:** {ctx.event.message.author}"""

    embed2=hikari.Embed(color=c, title="Thank you for donating", description="Your donation has been recorded, and a giveaway manager will respond soon.\nPlease be patient.\nKindly do not ping giveaway managers.")
    embed2.set_footer(text=ctx.get_guild().name, icon=ctx.get_guild().icon_url)
    msg = await ctx.respond(embed=embed2)

    cmd = f"!!giveaway start {ctx.options.duration} {ctx.options.winners} {ctx.options.requirements} {ctx.options.prize} --donor {ctx.event.message.author.id} --msg {ctx.options.message} --ping"
    link = miru.Button(label="Donation", url=f"https://discord.com/channels/{ctx.event.message.guild_id}/{ctx.event.message.channel_id}/{(await msg.message()).id}")
    link2 = miru.Button(label="Donation", url=f"https://discord.com/channels/{ctx.event.message.guild_id}/{ctx.event.message.channel_id}/{(await msg.message()).id}")

    view = miru.View(timeout=600)
    view.add_item(claim_button(cmd))
    view.add_item(link)
    msg2 = await ctx.app.rest.create_message(ctx.get_guild().get_channel(851346473370124309), "<@&832111569764352060> **NEW DONATION**", embed=embed, role_mentions=True, components=view.build())

    view.start(msg2)
    await view.wait()

    view2 = miru.View()
    view2.add_item(miru.Button(label="Claimed", emoji=hikari.Emoji.parse("<a:JBC_check:907203988468928522>"), disabled=True, style=hikari.ButtonStyle.SECONDARY))
    view2.add_item(link2)

    embed.set_footer(text=f"Claimed by {view.gman}", icon=view.gman.avatar_url)
    await msg2.edit(content="<@&832111569764352060> **CLAIMED**", embed=embed, components=view2.build())

@plugin.command()
# @lightbulb.add_checks(dono_channel)
@lightbulb.command("ginfo", "shows information on how to donate")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _ginfo(ctx: lightbulb.Context) -> None:
    try:
        await ctx.event.message.delete()
    except:
        pass

    c = random.randint(0x0, 0xffffff)
    
    embed=hikari.Embed(title="How to donate for giveaways <a:JBC_moneygun:968522741839986708>", color=c)
    embed.description = f"""If you would like to donate to giveaways (we accept Dank, OwO, Bro, etc.) please use the command:

**&gdonate <duration> <prize> [winners] [requirements] [message]**
eg: &gdonate 1h 1tro 1 level5 I love donating to JBC!
eg: &gdonate 6h 1tro|5pem level15|5mDonor This is how to donate multiple items or multiple requirements.

{br_dot} Minimum donation for all is **500k.**
{br_dot} Note that spaces will end your argument. For donating multiple items, refrain from using a space. Instead seperate them with a **|**.
{br_dot} A giveaway manager will then respond as soon as possible, please do not ping them.
{br_dot} If you would like to leave an area blank, just type **None**.
{br_dot} You will receive donator roles for donating a certain amount ranging from 5 million to 1 billion.
{br_dot} If you want to sponsor a heist, dm a online ADMIN. minimum donation for heist is 5 million.
{br_dot} If you would like to donate for nitro giveaways, please dm <@!488132046087258112>
{br_dot} If you wish to help support the server, you can also donate by just sending the items to <@!848196070437158912>. This will still count to your total donations."""
    embed.set_footer(text="Thank you for donating!", icon=ctx.get_guild().icon_url)
    await ctx.respond(embed=embed)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)