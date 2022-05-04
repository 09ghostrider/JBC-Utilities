import hikari
import lightbulb
import json
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import datetime

load_dotenv()
plugin = lightbulb.Plugin("censor")
plugin.add_checks(lightbulb.guild_only)
ephemeral = hikari.MessageFlag.EPHEMERAL

mongoclient = os.getenv("DATABASE")
with open("./configs/config.json") as f:
    bot_config = json.load(f)

@plugin.command()
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command("censor", "censor a word from being used")
@lightbulb.implements(lightbulb.PrefixCommandGroup)
async def _censor(ctx: lightbulb.Context) -> None:
    pass

@_censor.child
@lightbulb.option("word", "the word to censor", type=str, required=True)
@lightbulb.command("add", "add a word to the censor list", aliases=["+"], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _add(ctx: lightbulb.Context) -> None:
    word = ctx.options.word
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})
    
    if censor_list is None:
        censor_list = {
            "guild_id": guild_id,
            "censored": [word],
            "whitelist": {
                "role": [],
                "channel": [],
                "member": []
            },
            "punishment": {
                "action": "timeout",
                "duration": 120
            }
        }
        censor_db.insert_one(censor_list)
        return await ctx.respond(f"""Added "{word}" to censor list""", reply=True)
    
    if word in censor_list["censored"]:
        return await ctx.respond("It is already censored", reply=True)
    
    censor_list["censored"].append(word)
    censor_db.update_one({"guild_id": guild_id}, {"$set": {"censored": censor_list["censored"]}})
    await ctx.respond(f"""Added "{word}" to censor list""", reply=True)

@_censor.child
@lightbulb.option("word", "the word to uncensor", type=str, required=True)
@lightbulb.command("remove", "remove a word from the censor list", aliases=["-"], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _remove(ctx: lightbulb.Context) -> None:
    word = ctx.options.word
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})
    
    if censor_list is None:
        return await ctx.respond("It is not censored", reply=True)
    
    if word not in censor_list["censored"]:
        return await ctx.respond("It is not censored", reply=True)
    
    censor_list["censored"].pop(censor_list["censored"].index(word))
    censor_db.update_one({"guild_id": guild_id}, {"$set": {"censored": censor_list["censored"]}})
    await ctx.respond(f"""Removed "{word}" from censor list""", reply=True)

@_censor.child
@lightbulb.command("list", "check the censor list", aliases=["show"], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _list(ctx: lightbulb.Context) -> None:
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})

    if censor_list is None:
        return await ctx.respond("You have no censored words", reply=True)
    
    if censor_list["censored"] == []:
        return await ctx.respond("You have no censored words", reply=True)

    desc = ""
    for w in censor_list["censored"]:
        desc += f"\n{w}"
    embed = hikari.Embed(title="Censored words", description=desc, color=bot_config["color"]["default"])
    embed.set_footer(text=f"{len(censor_list['censored'])} words censored")
    await ctx.respond(embed=embed, reply=True)

@_censor.child
@lightbulb.command("settings", "view and edit the censor settings for this guild", aliases=["setting", "set", "s"], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubGroup)
async def _settings(ctx: lightbulb.Context) -> None:
    pass

@_settings.child
@lightbulb.command("view", "view the current setting", inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _settings_view(ctx: lightbulb.Context) -> None:
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})
    
    if censor_list is None:
        censor_list = {
            "guild_id": guild_id,
            "censored": [],
            "whitelist": {
                "role": [],
                "channel": [],
                "member": []
            },
            "punishment": {
                "action": "timeout",
                "duration": 120
            }
        }

    embed=hikari.Embed(title="CENSOR SETTINGS", color=bot_config["color"]["default"])
    embed.description = f"""{bot_config['emoji']['reply2']} **Punishment:** {censor_list['punishment']['action']}
{bot_config['emoji']['reply']} **Duration:** {datetime.timedelta(seconds = int(censor_list['punishment']['duration']))} (if punishment is timeout)"""

    f1 = ""
    if len(censor_list['whitelist']['role']) == 0:
        f1 = f"{bot_config['emoji']['reply']} None"
    elif len(censor_list['whitelist']['role']) == 1:
        f1 = f"{bot_config['emoji']['reply']} <@&{censor_list['whitelist']['role'][0]}>"
    else:
        l1 = censor_list['whitelist']['role'][:-1]
        for r1 in l1:
            f1 += f"\n{bot_config['emoji']['reply2']} <@&{r1}>"
        f1 += f"\n{bot_config['emoji']['reply']} <@&{censor_list['whitelist']['role'][-1:][0]}>"
    embed.add_field(name=f"Roles ({len(censor_list['whitelist']['role'])}):", value=f1, inline=True)

    f2 = ""
    if len(censor_list['whitelist']['channel']) == 0:
        f2 = f"{bot_config['emoji']['reply']} None"
    elif len(censor_list['whitelist']['channel']) == 1:
        f2 = f"{bot_config['emoji']['reply']} <#{censor_list['whitelist']['channel'][0]}>"
    else:
        l2 = censor_list['whitelist']['channel'][:-1]
        for r2 in l2:
            f2 += f"\n{bot_config['emoji']['reply2']} <#{r2}>"
        f2 += f"\n{bot_config['emoji']['reply']} <#{censor_list['whitelist']['channel'][-1:][0]}>"
    embed.add_field(name=f"Channels ({len(censor_list['whitelist']['channel'])}):", value=f2, inline=True)

    f3 = ""
    if len(censor_list['whitelist']['member']) == 0:
        f3 = f"{bot_config['emoji']['reply']} None"
    elif len(censor_list['whitelist']['member']) == 1:
        f3 = f"{bot_config['emoji']['reply']} <@!{censor_list['whitelist']['member'][0]}>"
    else:
        l3 = censor_list['whitelist']['member'][:-1]
        for r3 in l1:
            f3 += f"\n{bot_config['emoji']['reply2']} <@!{r1}>"
        f3 += f"\n{bot_config['emoji']['reply']} <@!{censor_list['whitelist']['member'][-1:][0]}>"
    embed.add_field(name=f"Members ({len(censor_list['whitelist']['member'])}):", value=f3, inline=True)

    await ctx.respond(embed=embed, reply=True)

@_settings.child
@lightbulb.command("whitelist", "whitelist a role, channel or member from being punished", aliases=["wl"], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubGroup)
async def _settings_whitelist(ctx: lightbulb.Context) -> None:
    pass

@_settings_whitelist.child
@lightbulb.option("role", "the role to whitelist", type=hikari.Role, required=True)
@lightbulb.command("role", "whitelist a role from being punished", inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _settings_whitelist_role(ctx: lightbulb.Context) -> None:
    role = ctx.options.role
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})
    
    if censor_list is None:
        censor_list = {
            "guild_id": guild_id,
            "censored": [],
            "whitelist": {
                "role": [role.id],
                "channel": [],
                "member": []
            },
            "punishment": {
                "action": "timeout",
                "duration": 120
            }
        }
        censor_db.insert_one(censor_list)
        return await ctx.respond(f"Added {role.mention} to whitelist", reply=True, role_mentions=False)
    
    if role.id in censor_list['whitelist']['role']:
        censor_list['whitelist']['role'].pop(censor_list['whitelist']['role'].index(role.id))
        censor_db.update_one({"guild_id": guild_id}, {"$set": {"whitelist": censor_list['whitelist']}})
        return await ctx.respond(f"Removed {role.mention} from whitelist", reply=True, role_mentions=False)
    
    censor_list['whitelist']['role'].append(role.id)
    censor_db.update_one({"guild_id": guild_id}, {"$set": {"whitelist": censor_list['whitelist']}})
    await ctx.respond(f"Added {role.mention} to whitelist", reply=True, role_mentions=False)
    


@_settings_whitelist.child
@lightbulb.option("channel", "the channel to whitelist", type=hikari.GuildChannel, required=True)
@lightbulb.command("channel", "whitelist a channel from being punished", inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _settings_whitelist_channel(ctx: lightbulb.Context) -> None:
    channel = ctx.options.channel
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})
    
    if censor_list is None:
        censor_list = {
            "guild_id": guild_id,
            "censored": [],
            "whitelist": {
                "role": [],
                "channel": [channel.id],
                "member": []
            },
            "punishment": {
                "action": "timeout",
                "duration": 120
            }
        }
        censor_db.insert_one(censor_list)
        return await ctx.respond(f"Added {channel.mention} to whitelist", reply=True, role_mentions=False)
    
    if channel.id in censor_list['whitelist']['channel']:
        censor_list['whitelist']['channel'].pop(censor_list['whitelist']['channel'].index(channel.id))
        censor_db.update_one({"guild_id": guild_id}, {"$set": {"whitelist": censor_list['whitelist']}})
        return await ctx.respond(f"Removed {channel.mention} from whitelist", reply=True, role_mentions=False)
    
    censor_list['whitelist']['channel'].append(channel.id)
    censor_db.update_one({"guild_id": guild_id}, {"$set": {"whitelist": censor_list['whitelist']}})
    await ctx.respond(f"Added {channel.mention} to whitelist", reply=True, role_mentions=False)

@_settings_whitelist.child
@lightbulb.option("member", "the member to whitelist", type=hikari.Member, required=True)
@lightbulb.command("member", "whitelist a member from being punished", inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _settings_whitelist_member(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})
    
    if censor_list is None:
        censor_list = {
            "guild_id": guild_id,
            "censored": [],
            "whitelist": {
                "role": [],
                "channel": [],
                "member": [member.id]
            },
            "punishment": {
                "action": "timeout",
                "duration": 120
            }
        }
        censor_db.insert_one(censor_list)
        return await ctx.respond(f"Added {member.mention} to whitelist", reply=True, role_mentions=False)
    
    if member.id in censor_list['whitelist']['member']:
        censor_list['whitelist']['member'].pop(censor_list['whitelist']['member'].index(member.id))
        censor_db.update_one({"guild_id": guild_id}, {"$set": {"whitelist": censor_list['whitelist']}})
        return await ctx.respond(f"Removed {member.mention} from whitelist", reply=True, role_mentions=False)
    
    censor_list['whitelist']['member'].append(member.id)
    censor_db.update_one({"guild_id": guild_id}, {"$set": {"whitelist": censor_list['whitelist']}})
    await ctx.respond(f"Added {member.mention} to whitelist", reply=True, role_mentions=False)

@_settings.child
@lightbulb.option("action", "the action to take", required=True, type=str, choices=["ban", "kick", "timeout"])
@lightbulb.command("punishment", "the punishment when a censored word is used (default = timeout)", aliases=["punish", "action"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _settings_action(ctx: lightbulb.Context) -> None:
    action = (ctx.options.action).lower()
    guild_id = ctx.event.message.guild_id

    if action in ['ban', 'b']:
        action = "ban"
    elif action in ['kick', 'k']:
        action = "kick"
    elif action in ['timeout', 'to', 'mute', 'm']:
        action = "timeout"
    else:
        return await ctx.respond("Invalid action\nAvailable actions: timeout, kick, ban", reply=True)

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})
    
    if censor_list is None:
        censor_list = {
            "guild_id": guild_id,
            "censored": [],
            "whitelist": {
                "role": [],
                "channel": [],
                "member": []
            },
            "punishment": {
                "action": action,
                "duration": 120
            }
        }
        censor_db.insert_one(censor_list)
        return await ctx.respond(f"Set the action to {action}", reply=True)
    
    censor_list['punishment']['action'] = action
    censor_db.update_one({"guild_id": guild_id}, {"$set": {"punishment": censor_list['punishment']}})
    await ctx.respond(f"Set the action to {action}", reply=True)

@_settings.child
@lightbulb.option("duration", "the duration of timeout", required=True, type=str)
@lightbulb.command("duration", "if the punishment is set to timeout, the duration of timeout (default = 120s)", aliases=["md", "tod"])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _settings_duration(ctx: lightbulb.Context) -> None:
    duration = ctx.options.duration
    guild_id = ctx.event.message.guild_id

    try:
        duration = int(duration)
    except:
        convertTimeList = {'s':1, 'm':60, 'h':3600, 'd':86400, 'S':1, 'M':60, 'H':3600, 'D':86400}
        try:
            duration = int(duration[:-1]) * convertTimeList[duration[-1]]
        except:
            return await ctx.respond("Invalid duration\nAvailable options: s, m, h, d", reply=True)
    if duration < 1:
        duration = 1

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})
    
    if censor_list is None:
        censor_list = {
            "guild_id": guild_id,
            "censored": [],
            "whitelist": {
                "role": [],
                "channel": [],
                "member": []
            },
            "punishment": {
                "action": "timeout",
                "duration": duration
            }
        }
        censor_db.insert_one(censor_list)
        return await ctx.respond(f"Set timeout duration to {datetime.timedelta(seconds = int(duration))}", reply=True)
    
    
    censor_list['punishment']['duration'] = duration
    censor_db.update_one({"guild_id": guild_id}, {"$set": {"punishment": censor_list['punishment']}})
    await ctx.respond(f"Set timeout duration to {datetime.timedelta(seconds = int(duration))}", reply=True)

@plugin.listener(hikari.MessageCreateEvent)
async def _on_message(message: hikari.MessageCreateEvent) -> None:
    if message.is_human == False:
        return
    
    if message.message.content is None:
        return

    member = message.message.member
    guild_id = message.message.guild_id
    channel_id = message.message.channel_id

    if member.id in bot_config['bot']['owner_ids']:
        return

    perms = lightbulb.utils.permissions.permissions_for(member)
    if hikari.Permissions.ADMINISTRATOR in perms:
        return

    cluster = MongoClient(mongoclient)
    censor_db = cluster["censor"]["censor"]
    censor_list = censor_db.find_one({"guild_id": guild_id})

    if censor_list is None:
        return
    if censor_list['censored'] == []:
        return
    
    if member.id in censor_list['whitelist']['member']:
        return
    
    if channel_id in censor_list['whitelist']['channel']:
        return
    
    roles = member.get_roles()
    for r in censor_list['whitelist']['role']:
        role = message.message.app.cache.get_role(r)
        if role in roles:
            return

    for word in censor_list['censored']:
        if word in message.message.content.lower():
            try:
                await message.message.delete()
            except:
                pass
            
            action = censor_list['punishment']['action']
            reason = f"Automatic action carried out for using a blacklisted word ({word})"
            guild = await message.message.app.rest.fetch_guild(message.message.guild_id)
            channel = await message.message.app.rest.fetch_channel(channel_id)

            if action == "timeout":
                try:
                    await member.edit(communication_disabled_until=(datetime.datetime.utcfromtimestamp(int(round((datetime.datetime.now(tz=datetime.timezone.utc).timestamp())+int(censor_list['punishment']['duration']))))), reason=reason)
                    action_taken = bot_config['emoji']['tick']
                    try:
                        await message.message.author.send(f"You have been put to timeout for **{datetime.timedelta(seconds=int(censor_list['punishment']['duration']))}** in **{guild.name}**\nReason: {reason}")
                        member_dm = bot_config['emoji']['tick']
                    except:
                        member_dm = bot_config['emoji']['cross']
                except:
                    action_taken = bot_config['emoji']['cross']
                    member_dm = bot_config['emoji']['cross']
                
                embed=hikari.Embed(color=bot_config['color']['default'])
                embed.set_author(name=str(member), icon=str(member.avatar_url))
                embed.description = f"""{bot_config['emoji']['blue_arrow']} **Member:** {member.mention} ({member.id})
{bot_config['emoji']['blue_arrow']} **Action:** {action}
{bot_config['emoji']['blue_arrow']} **Duration:** {datetime.timedelta(seconds=int(censor_list['punishment']['duration']))}
{bot_config['emoji']['blue_arrow']} **Reason:** {reason}
{bot_config['emoji']['blue_arrow']} **Message:** {message.message.content}"""
                embed.add_field(name="More info:", value=f"""{bot_config['emoji']['blue_arrow']} Member DM: {member_dm}
{bot_config['emoji']['blue_arrow']} Action taken: {action_taken}""")

                await message.message.app.rest.create_message(channel, embed=embed)

            elif action == "ban":
                try:
                    await message.message.author.send(f"You have banned from **{guild.name}**\nReason: {reason}")
                    member_dm = bot_config['emoji']['tick']
                except:
                    member_dm = bot_config['emoji']['cross']
                try:
                    await message.message.app.rest.ban_member(guild, member, reason=reason)
                    action_taken = bot_config['emoji']['tick']
                except:
                    action_taken = bot_config['emoji']['cross']
                
                embed=hikari.Embed(color=bot_config['color']['default'])
                embed.set_author(name=str(member), icon=str(member.avatar_url))
                embed.description = f"""{bot_config['emoji']['blue_arrow']} **Member:** {member.mention} ({member.id})
{bot_config['emoji']['blue_arrow']} **Action:** {action}
{bot_config['emoji']['blue_arrow']} **Reason:** {reason}
{bot_config['emoji']['blue_arrow']} **Message:** {message.message.content}"""
                embed.add_field(name="More info:", value=f"""{bot_config['emoji']['blue_arrow']} Member DM: {member_dm}
{bot_config['emoji']['blue_arrow']} Action taken: {action_taken}""")

                await message.message.app.rest.create_message(await message.message.app.rest.fetch_channel(channel_id), embed=embed)

            elif action == "kick":
                try:
                    await message.message.author.send(f"You have kicked from **{guild.name}**\nReason: {reason}")
                    member_dm = bot_config['emoji']['tick']
                except:
                    member_dm = bot_config['emoji']['cross']
                try:
                    await message.message.app.rest.kick_member(guild, member, reason=reason)
                    action_taken = bot_config['emoji']['tick']
                except:
                    action_taken = bot_config['emoji']['cross']
                
                embed=hikari.Embed(color=bot_config['color']['default'])
                embed.set_author(name=str(member), icon=str(member.avatar_url))
                embed.description = f"""{bot_config['emoji']['blue_arrow']} **Member:** {member.mention} ({member.id})
{bot_config['emoji']['blue_arrow']} **Action:** {action}
{bot_config['emoji']['blue_arrow']} **Reason:** {reason}
{bot_config['emoji']['blue_arrow']} **Message:** {message.message.content}"""
                embed.add_field(name="More info:", value=f"""{bot_config['emoji']['blue_arrow']} Member DM: {member_dm}
{bot_config['emoji']['blue_arrow']} Action taken: {action_taken}""")

                await message.message.app.rest.create_message(await message.message.app.rest.fetch_channel(channel_id), embed=embed)


def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)