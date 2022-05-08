import hikari
import lightbulb
import json
import miru
import re

plugin = lightbulb.Plugin("listener")
ephemeral = hikari.MessageFlag.EPHEMERAL
lregex = r"https:\/\/discord\.com\/channels\/\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\/\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\/\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d"
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
    
    link_split = (match.group()).split("/")
    guild_id = int(link_split[4])
    channel_id = int(link_split[5])
    message_id = int(link_split[6])

    if guild_id != message.message.guild_id:
        return

    msg = await message.message.app.rest.fetch_message(channel=channel_id, message=message_id)

    if not msg:
        return

    view = miru.View()
    view.add_item(miru.Button(label="Message", url=str(match.group())))

    # New webhook
    webhook = await message.message.app.rest.create_webhook(message.message.channel_id, f"{msg.author.username}", avatar=str(msg.author.avatar_url), reason="Message link preview")

    # Execute webhook
    if msg.embeds != []:
        await webhook.execute(embed=msg.embeds[0], components=view.build())
    else:
        embed=hikari.Embed(description=f"{msg.content}", color=bot_config['color']['default'])
        embed.set_footer(text=f"# {(await msg.fetch_channel()).name}")
        embed.timestamp = msg.created_at
        embed.set_author(name=f"{msg.author} ({msg.author.id})", icon=str(msg.author.avatar_url))

        await webhook.execute(embed=embed, components=view.build())

    # Delete webhook
    await message.message.app.rest.delete_webhook(webhook)
    
@plugin.listener(hikari.PresenceUpdateEvent)
async def _status_update(ctx: hikari.PresenceUpdateEvent) -> None:
    status_log = 942621300394975232
    status_role = 942621461695324180
    if ctx.guild_id != 832105614577631232:
        return
    
    status_list = ['discord.gg/1vs', '.gg/1vs', 'https://discord.com/1vs', 'https://discord.com/invite/1vs', 'discord.com/invite/1vs']

    presence = ctx.presence
    status = presence.activities[0].state
    member = await ctx.app.rest.fetch_member(ctx.guild_id, ctx.user_id)
    role = ctx.app.cache.get_role(status_role)
    roles = member.get_roles()

    if member.is_bot == True or member.is_system == True:
        return

    if role in roles:
        count = 0
        for s in status_list:
            if s not in status:
                count += 1
            else:
                return
        
        if count == len(status_list):
            await member.remove_role(role)
            channel = await ctx.app.rest.fetch_channel(status_log)
            embed=hikari.Embed(color=bot_config['color']['red'], description=f"Removed {role.mention} from {member.mention}\n**New Status:** {status}")
            return await channel.send(embed=embed)

    elif role not in roles:
        for s in status_list:
            if s in status:
                await member.add_role(role)
                channel = await ctx.app.rest.fetch_channel(status_log)
                embed=hikari.Embed(color=bot_config['color']['green'], description=f"Added {role.mention} to {member.mention}\n**New Status:** {status}")
                return await channel.send(embed=embed)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)