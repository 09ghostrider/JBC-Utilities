import hikari
import lightbulb
import json
import miru
import re
import datetime
from bot.utils.checks import botban_check

plugin = lightbulb.Plugin("listener")
plugin.add_checks(botban_check)
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
        embed.set_author(name=f"{msg.author}", icon=str(msg.author.avatar_url))

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
    try:
        status = presence.activities[0].state
        if not status:
            status = ""
    except IndexError:
        return
    member = await ctx.app.rest.fetch_member(ctx.guild_id, ctx.user_id)
    role = ctx.app.cache.get_role(status_role)
    roles = member.get_roles()

    if member.is_bot == True or member.is_system == True:
        return

    if role in roles:
        for s in status_list:
            if s in status:
                return
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

@plugin.listener(hikari.MemberCreateEvent)
async def _on_member_join(ctx: hikari.MemberCreateEvent) -> None:
    member = ctx.member
    created = round(member.created_at.timestamp())
    current = round(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())
    diff = current - created
    if diff <= 259200:
        try:
            await member.send(f"You were banned from **{ctx.get_guild().name}**\nReason: Account too young to be allowed.")
        except:
            pass
        await member.ban(delete_message_days=0, reason="Account too young to be allowed")
    elif diff <= 604800:
        role =  ctx.app.cache.get_role(896416813611638866)
        try:
            await member.send(f"You were blacklisted in **{ctx.get_guild().name}**\nReason: Account age too young.")
        except:
            pass
        await member.add_role(role, reason="Account age too young")

# @plugin.listener(hikari.MessageCreateEvent)
# async def _on_message(message: hikari.MessageCreateEvent) -> None:
#     if message.author_id != 270904126974590976:
#         return
    
#     e = message.message.embeds
#     if e == []:
#         return
    
#     e1 = e[0]
#     if not e1.title:
#         return
    
#     if e1.title == "Successful Trade!":
#         trade = e1
#         user1 = e1.fields[0].name
#         user2 = e1.fields[1].name

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)