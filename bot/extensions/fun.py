import hikari
import lightbulb
import random
import asyncio
import miru
import requests

plugin = lightbulb.Plugin("fun")
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./secrets/prefix") as f:
    prefix = f.read().strip()

@plugin.command()
@lightbulb.option("text", "text", type=str, required=False, default=None, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.command("howgay", "shows how gay you are", aliases=["gayrate"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _howgay(ctx: lightbulb.Context) -> None:
    text = ctx.options.text
    if text == None:
        text = ctx.event.message.author.username
    gayrate = random.randint(0, 100)
    embed = hikari.Embed(color=random.randint(0x0, 0xffffff), title="Gay rate", description=f"{text} is {gayrate}% gay :gay_pride_flag:")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.option("text", "text", type=str, required=False, default=None, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.command("simprate", "shows how simp you are", aliases=["simp"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _simprate(ctx: lightbulb.Context) -> None:
    text = ctx.options.text
    if text == None:
        text = ctx.event.message.author.username
    simprate = random.randint(0, 100)
    embed = hikari.Embed(color=random.randint(0x0, 0xffffff), title="Simp rate", description=f"{text} is {simprate}% simp")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.option("text", "text", type=str, required=False, default=None, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.command("penis", "big or small penis", aliases=["pp"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _penis(ctx: lightbulb.Context) -> None:
    text = ctx.options.text
    if text == None:
        text = ctx.event.message.author.username
    pp = random.randint(0, 15)
    size = "="*pp
    embed = hikari.Embed(color=random.randint(0x0, 0xffffff), title="peepee size", description=f"{text}'s penis\n8{size}D")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.option("user", "the user to roast", required=False, default=None, type=hikari.User)
@lightbulb.command("roast", "used to roast a user", aliases=["insult"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _roast(ctx: lightbulb.Context) -> None:
    r = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=json").json()
    roast = r['insult']
    user = ctx.options.user
    if user is not None:
        await ctx.respond(f"{user}: {roast}", reply=True)
    else:
        await ctx.respond(f"{roast}", reply=True)

@plugin.command()
@lightbulb.command("joke", "want a joke?")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _joke(ctx: lightbulb.Context) -> None:
    r = (requests.get("https://api.popcat.xyz/joke").json())["joke"]
    await ctx.respond(f"{r}", reply=True)

@plugin.command()
@lightbulb.command("fact", "Facts time")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _fact(ctx: lightbulb.Context) -> None:
    r = (requests.get("https://api.popcat.xyz/fact").json())["fact"]
    await ctx.respond(f"{r}", reply=True)

@plugin.command()
@lightbulb.command("thought", "Thoughts")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _thought(ctx: lightbulb.Context) -> None:
    r = (requests.get("https://api.popcat.xyz/fact").json())["fact"]
    await ctx.respond(f"{r}", reply=True)

@plugin.command()
@lightbulb.command("quote", "Famous quotes")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _quote(ctx: lightbulb.Context) -> None:
    r = requests.get("https://api.popcat.xyz/showerthoughts").json()
    t = r["result"]
    a = r["author"]
    await ctx.respond(f""""{t}" - {a}""", reply=True)

@plugin.command()
@lightbulb.command("meme", "get a meme at your will")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _meme(ctx: lightbulb.Context) -> None:
    r = requests.get("https://meme-api.herokuapp.com/gimme").json()
    embed=hikari.Embed(description = f"**[{r['title']}]({r['postLink']})**")
    embed.set_image(r['url'])
    embed.set_footer(text=f"👍 {r['ups']} | {r['subreddit']}")
    await ctx.respond(embed=embed, reply=True)

# @plugin.command()
# # @lightbulb.add_cooldown(30, 1, lightbulb.UserBucket)
# @lightbulb.add_checks(lightbulb.guild_only)
# @lightbulb.option("end", "the end range of the random number", required=True, type=int)
# @lightbulb.option("start", "the start range of the random number", required=True, type=int)
# @lightbulb.command("gtn", "feeling lucky? Try guess the number", aliases=['guessthenumber'])
# @lightbulb.implements(lightbulb.PrefixCommand)
# async def _gtn(ctx: lightbulb.Context) -> None:
#     try:
#         await ctx.event.message.delete()
#     except:
#         pass

#     start = ctx.options.start
#     end = ctx.options.end

#     embed1 = hikari.Embed(
#         title = "GUESS THE NUMBER",
#         description = f"**Range:** {start} - {end}\n**Started by:** {ctx.author.mention}",
#         color = random.randint(0x0, 0xFFFFFF)
#     )
#     embed1.set_footer(text=f"Guild: {ctx.get_guild()}")
#     message1 = await ctx.respond(embed1)

#     jump_url = str((await message1.message()).make_link(ctx.guild_id))
#     number = random.randint(start, end)
#     embed2 = hikari.Embed(
#         title = f"GUESS THE NUMBER",
#         description = f"**Range:** {start} - {end}\n**Number:** ||{number}||",
#         color = random.randint(0x0, 0xFFFFFF)
#     )
#     view = miru.View()
#     view.add_item(miru.Button(label="Jump", url=jump_url))

#     embed2.set_footer(text=f"Guild: {ctx.get_guild()}")
#     message2 = await ctx.author.send(embed2, components=view.build())

#     total_guesses = 0

#     while True:
#         try:
#             message = await ctx.app.wait_for(event_type="GuildMessageCreateEvent", timeout=5, predicate=None) # 300
#         except asyncio.TimeoutError:
#             return await ctx.app.rest.create_message((await ctx.event.message.fetch_channel()), "Timeout!", reply=(await message1.message()), embed=embed2)
#         else:
#             if ctx.event.message.guild_id == message.guild_id and ctx.event.message.channel_id == message.channel_id and ctx.event.message.author.id != message.author.id:
#                 try:
#                     if int(message.content.strip()) == number:
#                         answer = message
#                         break
#                 except:
#                     pass

#     embed3 = hikari.Embed(
#         title = f"The number was guessed!",
#         description = f"**Range:** {start} - {end}\n**Number:** {number}\n**Guessed by:** {answer.author}",
#         color = random.randint(0x0, 0xFFFFFF)
#     )
#     await ctx.app.rest.create_message((await ctx.event.message.fetch_channel()), reply=answer, embed=embed3, mentions_reply=True)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)