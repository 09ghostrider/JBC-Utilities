import hikari
import lightbulb
import random
import asyncio
import miru
import requests
import json
from bot.utils.checks import botban_check

plugin = lightbulb.Plugin("fun")
plugin.add_checks(botban_check)
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./configs/config.json") as f:
    bot_config = json.load(f)

eight_ball_responses = [
    "It is certain",
    "It is decidedly so",
    "Without a doubt",
    "Yes, definitely",
    "You may rely on it",
    "As I see it, yes",
    "Most likely",
    "Outlook good",
    "Yes",
    "Signs point to yes",
    "Reply hazy try again",
    "Ask again later",
    "Better not tell you now",
    "Cannot predict now",
    "Concentrate and ask again",
    "Don't count on it",
    "My reply is no",
    "My sources say no",
    "Outlook not so good",
    "Very doubtful"
]

@plugin.command()
@lightbulb.option("text", "text", type=str, required=False, default=None, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.command("howgay", "shows how gay you are", aliases=["gayrate"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _howgay(ctx: lightbulb.Context) -> None:
    text = ctx.options.text
    if not text:
        text = ctx.event.message.author.username
    gayrate = random.randint(0, 100)
    embed = hikari.Embed(color=bot_config["color"]["default"], title="Gay rate", description=f"{text} is {gayrate}% gay :gay_pride_flag:")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.option("text", "text", type=str, required=False, default=None, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.command("noobrate", "shows how noob you are", aliases=["noob"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _noobrate(ctx: lightbulb.Context) -> None:
    text = ctx.options.text
    if not text:
        text = ctx.event.message.author.username
    noobrate = random.randint(0, 100)
    embed = hikari.Embed(color=bot_config["color"]["default"], title="Noob rate", description=f"{text} is {noobrate}% noob")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.option("text", "text", type=str, required=False, default=None, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.command("progamer", "shows how much of a gamer you are", aliases=["gamer"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _progamer(ctx: lightbulb.Context) -> None:
    text = ctx.options.text
    if not text:
        text = ctx.event.message.author.username
    progamer = random.randint(0, 100)
    embed = hikari.Embed(color=bot_config["color"]["default"], title="Pro gamer", description=f"{text} is {progamer}% pro gamer")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.option("text", "text", type=str, required=False, default=None, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.command("prorate", "shows how pro you are", aliases=["pro"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _prorate(ctx: lightbulb.Context) -> None:
    text = ctx.options.text
    if not text:
        text = ctx.event.message.author.username
    prorate = random.randint(0, 100)
    embed = hikari.Embed(color=bot_config["color"]["default"], title="Pro rate", description=f"{text} is {prorate}% pro")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.option("text", "text", type=str, required=False, default=None, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.command("simprate", "shows how simp you are", aliases=["simp"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _simprate(ctx: lightbulb.Context) -> None:
    text = ctx.options.text
    if not text:
        text = ctx.event.message.author.username
    simprate = random.randint(0, 100)
    embed = hikari.Embed(color=bot_config["color"]["default"], title="Simp rate", description=f"{text} is {simprate}% simp")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.option("text", "text", type=str, required=False, default=None, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.command("penis", "big or small penis", aliases=["pp"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _penis(ctx: lightbulb.Context) -> None:
    text = ctx.options.text
    if not text:
        text = ctx.event.message.author.username
    pp = random.randint(0, 15)
    size = "="*pp
    embed = hikari.Embed(color=bot_config["color"]["default"], title="peepee size", description=f"{text}'s penis\n8{size}D")
    await ctx.respond(embed=embed)

@plugin.command()
@lightbulb.option("user", "the user to roast", required=False, default=None, type=hikari.User)
@lightbulb.command("roast", "used to roast a user", aliases=["insult"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _roast(ctx: lightbulb.Context) -> None:
    r = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=json").json()
    user = ctx.options.user
    if user:
        await ctx.respond(f"{user.mention}: {r['insult']}", reply=True, user_mentions=True)
    else:
        await ctx.respond(f"{r['insult']}", reply=True)

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

# @plugin.command()
# @lightbulb.command("thought", "Thoughts")
# @lightbulb.implements(lightbulb.PrefixCommand)
# async def _thought(ctx: lightbulb.Context) -> None:
#     r = (requests.get("https://api.popcat.xyz/fact").json())["fact"]
#     await ctx.respond(f"{r}", reply=True)

@plugin.command()
@lightbulb.command("quote", "Famous quotes")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _quote(ctx: lightbulb.Context) -> None:
    r = requests.get("https://api.popcat.xyz/showerthoughts").json()
    await ctx.respond(f""""{r['result']}" - {r['author']}""", reply=True)

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

@plugin.command()
@lightbulb.command("8ball", "this command gives 100% accurate results")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _8ball(ctx: lightbulb.Context) -> None:
    ball = random.choice(eight_ball_responses)
    await ctx.respond(f":8ball: **|** {ball}", reply=True)

@plugin.command()
@lightbulb.command("flip", "flip a coin")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _flip(ctx: lightbulb.Context) -> None:
    coin = random.choice(["head", "tail"])
    await ctx.respond(f":coin: **|** You flipped a {coin}", reply=True)

@plugin.command()
@lightbulb.option("choices", "the choices to choose from", required=True, type=str, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.command("choose", "Chooses a random element from the supplied choices, use a comma (,) for multi word selects", aliases=['pick', 'select', 'choice'])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _choose(ctx: lightbulb.Context) -> None:
    choices = ctx.options.choices
    if "," in choices:
        cList = choices.split(",")
    else:
        cList = choices.split(" ")
    choice = random.choice(cList)
    await ctx.respond(f"{choice}")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)