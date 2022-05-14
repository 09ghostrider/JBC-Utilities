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
esnipe_data = {}

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
@lightbulb.option("channel", "the channel to snipe messages from", required=False, default=None, type=hikari.GuildChannel)
@lightbulb.command("snipe", "snipe a deleted message", aliases=['sniper'])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _snipe(ctx: lightbulb.Context) -> None:
    channel = ctx.options.channel

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
        embed.set_author(name=f"{data['user']}", icon=data['avatar'])
        embed.timestamp = data['time']
        embed.set_footer(text = f"# {channel.name}")

        if data['content'] != None:
            embed.description = data['content']
        
        if data['attachment'] != None:
            embed.set_image(data['attachment'])
        pages.append(embed)

    navigator = nav.NavigatorView(pages=pages, buttons=[miru.ext.nav.buttons.PrevButton(style=hikari.ButtonStyle.PRIMARY, emoji=hikari.Emoji.parse(bot_config['emoji']['blue_arrowL'])), miru.ext.nav.buttons.NextButton(style=hikari.ButtonStyle.PRIMARY, emoji=hikari.Emoji.parse(bot_config['emoji']['blue_arrowR']))])
    await navigator.send(ctx.event.message.channel_id)

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | perms_check)
@lightbulb.option("channel", "the channel to snipe messages from", required=False, default=None, type=hikari.GuildChannel)
@lightbulb.command("esnipe", "snipe a edited message", aliases=['editsnipe', 'esniper'])
@lightbulb.implements(lightbulb.PrefixCommand)
async def _snipe(ctx: lightbulb.Context) -> None:
    channel = ctx.options.channel

    if not channel:
        channel_id = ctx.event.message.channel_id
        channel = ctx.get_channel()
    else:
        channel_id = channel.id
    
    try:
        esnipe_list = esnipe_data[str(channel_id)]
    except:
        return await ctx.respond("Nothing was edited recently", reply=True)
    
    if esnipe_list == []:
        return await ctx.respond("Nothing was edited recently", reply=True)
    
    pages = []
    for data in esnipe_list:
        embed = hikari.Embed(
            color = bot_config['color']['default']
        )
        embed.set_author(name=f"{data['user']}", icon=data['avatar'])
        embed.timestamp = data['time']
        embed.set_footer(text = f"# {channel.name}")
        embed.add_field(name="Old content", value=str(data['old']))
        embed.add_field(name="New content", value=str(data['new']))
        embed.description = f"[Jump To Message]({data['url']})"
        pages.append(embed)

    navigator = nav.NavigatorView(pages=pages, buttons=[miru.ext.nav.buttons.PrevButton(style=hikari.ButtonStyle.PRIMARY, emoji=hikari.Emoji.parse(bot_config['emoji']['blue_arrowL'])), miru.ext.nav.buttons.NextButton(style=hikari.ButtonStyle.PRIMARY, emoji=hikari.Emoji.parse(bot_config['emoji']['blue_arrowR']))])
    await navigator.send(ctx.event.message.channel_id)

@plugin.listener(hikari.GuildMessageUpdateEvent)
async def _on_message_update(message: hikari.GuildMessageUpdateEvent) -> None:
    old = message.old_message
    new = message.message

    if not new:
        return
    
    if new.author.is_bot == True or new.author.is_system == True:
        return
    
    global esnipe_data

    data = {
        "id": int(new.author.id),
        "user": str(new.author),
        "avatar": str(new.author.avatar_url),
        "new": new.content,
        "old": old.content,
        "time": new.edited_timestamp,
        "url": f"https://discord.com/channels/{new.guild_id}/{new.channel_id}/{new.id}"
    }

    try:
        esnipe_data[str(new.channel_id)] = [data] + esnipe_data[str(new.channel_id)]
    except KeyError:
        esnipe_data[str(new.channel_id)] = []
        esnipe_data[str(new.channel_id)] = [data] + esnipe_data[str(new.channel_id)]

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