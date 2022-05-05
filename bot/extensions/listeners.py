import hikari
import lightbulb
import random
import asyncio
import json
import miru
import re

plugin = lightbulb.Plugin("listeners")
ephemeral = hikari.MessageFlag.EPHEMERAL
lregex = "https:\/\/discord\.com\/channels\/\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\/\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\/\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d"
link_regex = re.compile(lregex)

with open("./configs/config.json") as f:
    bot_config = json.load(f)

@plugin.listener(hikari.MessageCreateEvent)
async def _on_message(message: hikari.MessageCreateEvent) -> None:
    if message.is_human == False:
        return

    if message.content == None or message.content == "" or message.content == False:
        return
    
    match = re.search(link_regex, message.content)
    if match == None:
        return
    
    link_split = match.split("/")
    guild_id = link_split[4]
    channel_id = link_split[5]
    message_id = link_split[6]

    if guild_id != message.message.guild_id:
        return
    
    msg = await message.message.app.rest.fetch_message(channel=channel_id, message=message_id)
    
    if msg is None:
        return
    
    content=msg.content
    embeds=msg.embeds
    
    if embeds != []:
        return await message.app.rest.create_message(channel_id, content, role_mentions=False, user_mentions=False, mentions_everyone=False)
    else:
        await message.app.rest.create_message(channel_id, content, role_mentions=False, user_mentions=False, mentions_everyone=False, embed=embeds[0])

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)