import datetime
import hikari
import lightbulb
import json
from bot.utils.checks import botban_check

plugin = lightbulb.Plugin("snipe")
plugin.add_checks(botban_check)
ephemeral = hikari.MessageFlag.EPHEMERAL

with open("./configs/config.json") as f:
    bot_config = json.load(f)

snipe_data = {}

@plugin.command()
@lightbulb.option("index", "the index of the message to snipe", required=False, default=1, type=int)
@lightbulb.option("channel", "the channel to snipe messages from", required=False, default=None, type=hikari.GuildChannel)
@lightbulb.command("snipe", "snipe a deleted message", aliases=['sniper'])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _snipe(ctx: lightbulb.Context) -> None:
    channel = ctx.options.channel
    index = ctx.options.index

    if not channel:
        channel_id = ctx.event.message.channel_id
    else:
        channel_id = channel.id
    
    try:
        snipe_list = snipe_data[str(channel_id)]
    except:
        return await ctx.respond("Nothing was deleted recently", reply=True)
    
    if snipe_list == []:
        return await ctx.respond("Nothing was deleted recently", reply=True)
    
    try:
        data = snipe_list[(index - 1)]
    except:
        return await ctx.respond("Nothing was deleted recently", reply=True)
    
    embed = hikari.Embed(
        color = bot_config['color']['default']
    )
    embed.set_author(name=f"{data['user']}", icon=data['avatar'])
    embed.timestamp = data['time']
    embed.set_footer(text = f"ID: {data['id']}")

    if data['content'] != None:
        embed.description = data['content']
    
    if data['attachment'] != None:
        embed.set_image(data['attachment'])

    await ctx.respond(embed=embed)

@plugin.listener(hikari.GuildMessageDeleteEvent)
async def _on_message_delete(message: hikari.GuildMessageDeleteEvent) -> None:
    msg = message.old_message
    if not msg:
        return
    
    if msg.author.is_bot == True or msg.author.is_system == True:
        return

    global snipe_data

    data = {
        "id": int(msg.author.id),
        "user": str(msg.author),
        "avatar": str(msg.author.avatar_url),
        "content": msg.content,
        "time": msg.created_at
    }

    if msg.attachments != ():
        data['attachment'] = str((msg.attachments[0]).url)
    else:
        data['attachment'] = None

    try:
        snipe_data[str(msg.channel_id)] = [data] + snipe_data[str(msg.channel_id)]
    except KeyError:
        snipe_data[str(msg.channel_id)] = []
        snipe_data[str(msg.channel_id)] = [data] + snipe_data[str(msg.channel_id)]

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)