import datetime
import hikari
import lightbulb
import json
from pymongo import MongoClient
from miru.ext import nav
from bot.utils.checks import botban_check
from dotenv import load_dotenv
import os
import miru

plugin = lightbulb.Plugin("snipe")
plugin.add_checks(botban_check)
ephemeral = hikari.MessageFlag.EPHEMERAL

load_dotenv()
mongoclient = os.getenv("DATABASE")
with open("./configs/config.json") as f:
    bot_config = json.load(f)

snipe_data = {}

@lightbulb.Check
def perms_check(ctx: lightbulb.Context) -> None:
    cluster = MongoClient(mongoclient)
    configs = cluster["snipe"]["server_configs"]

    config = configs.find_one({"guild": ctx.event.message.guild_id})
    if config == None:
        return False
    
    roles = ctx.event.message.member.get_roles()
    for r in config["req"]:
        role = ctx.app.cache.get_role(r)
        if role in roles:
            return True
    return False

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | perms_check)
@lightbulb.option("index", "the index of the message to snipe", required=False, default=1, type=int)
@lightbulb.option("channel", "the channel to snipe messages from", required=False, default=None, type=hikari.GuildChannel)
@lightbulb.command("snipe", "snipe a deleted message", aliases=['sniper'])
@lightbulb.implements(lightbulb.PrefixCommandGroup)
async def _snipe(ctx: lightbulb.Context) -> None:
    channel = ctx.options.channel
    index = ctx.options.index

    if not channel:
        channel_id = ctx.event.message.channel_id
        channel = ctx.get_channel()
    else:
        channel_id = channel.id
    
    try:
        snipe_list = snipe_data[str(channel_id)]
    except:
        return await ctx.respond("Nothing was deleted recently", reply=True)
    
    if snipe_list == []:
        return await ctx.respond("Nothing was deleted recently", reply=True)
    
    pages = []
    for data in snipe_list:
        embed = hikari.Embed(
            color = bot_config['color']['default']
        )
        embed.set_author(name=f"{data['user']} ({data['id']})", icon=data['avatar'])
        embed.timestamp = data['time']
        embed.set_footer(text = f"# {channel.name}")

        if data['content'] != None:
            embed.description = data['content']
        
        if data['attachment'] != None:
            embed.set_image(data['attachment'])
        pages.append(embed)

    navigator = nav.NavigatorView(pages=pages, buttons=[miru.ext.nav.buttons.NextButton(style=hikari.ButtonStyle.PRIMARY, emoji=hikari.Emoji.parse(bot_config['emoji']['blue_arrowL'])), miru.ext.nav.buttons.StopButton(style=hikari.ButtonStyle.DANGER, emoji=hikari.Emoji.parse(bot_config['emoji']['cross'])), miru.ext.nav.buttons.PrevButton(style=hikari.ButtonStyle.PRIMARY, emoji=hikari.Emoji.parse(bot_config['emoji']['blue_arrowR']))])
    await navigator.send(channel_id)


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