import hikari
import lightbulb
import random
import miru
import pymongo
from pymongo import MongoClient
import datetime
from miru.ext import nav
from dotenv import load_dotenv
import os
import json
from bot.utils.checks import botban_check

plugin = lightbulb.Plugin("donations")
plugin.add_checks(botban_check)
ephemeral = hikari.MessageFlag.EPHEMERAL

load_dotenv()
mongoclient = os.getenv("DATABASE")
with open("./configs/config.json") as f:
    bot_config = json.load(f)

donor_roles = bot_config['donos']['donor_roles']

@lightbulb.Check
def perms_check(ctx: lightbulb.Context) -> None:
    cluster = MongoClient(mongoclient)
    configs = cluster["donations"]["server_configs"]

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
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("donation", "maintain and manage donations of a member", aliases=["dono", "donations"])
@lightbulb.implements(lightbulb.PrefixCommandGroup)
async def _donation(ctx: lightbulb.Context) -> None:
    embed=hikari.Embed(title="=== Command Help ===", description="""donation - maintain and manage donations of a member

Usage: -donation [subcommand]
    """, color=random.randint(0x0, 0xffffff))
    embed.add_field(name="== Subcommands ==", value="""- remove - remove a members donation note
- show - check the notes of a member
- add - add amount to a members donation""")
    await ctx.respond(embed=embed)

@_donation.child
@lightbulb.add_checks(lightbulb.owner_only| lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | perms_check)
@lightbulb.option("note", "take a note for this donation", type=str, required=False, default="No Note Provided", modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.option("amount", "the amount to add", type=str, required=True)
@lightbulb.option("member", "the member to add donation", type=hikari.Member, required=True)
@lightbulb.command("add", "add amount to a members donation", aliases=["a", "sn", "setnote", "+"], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _add(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    amount = ctx.options.amount
    note = ctx.options.note

    try:
        amount = int(amount)
    except:
        try:
            if "e" in amount:
                first_digit, how_many_zeros = amount.split("e")
                amount = int(f"{first_digit}{'0' * int(how_many_zeros)}")
            else:
                await ctx.respond("Invalid amount", reply=True, flags=ephemeral)
                return
        except:
            await ctx.respond("Invalid amount", reply=True, flags=ephemeral)
            return

    if amount <= 0:
        await ctx.respond("Invalid amount", reply=True, flags=ephemeral)
        return
    
    if member.is_bot == True:
        await ctx.respond("You can not add donation to bots", reply=True, flags=ephemeral)
        return

    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    donos = cluster["donations"]["donations"]
    
    note_check = False
    while note_check == False:
        note_id = random.randint(0,999999999999999)
        n_c = donos.find_one({"note_id": {"$eq": note_id}})
        if n_c == None:
            note_check = True

    if note_check == False:
        return
        
    dono = {
        "note_id": note_id,
        "member": member.id,
        "guild": guild_id,
        "amount": amount,
        "note": note
    }
    donos.insert_one(dono)

    cluster2 = MongoClient(mongoclient)
    donos2 = cluster2["donations"]["donations"]
    dono2 = donos2.find({"guild": guild_id, "member": member.id})
    total_donation = 0
    for d in dono2:
        total_donation += d["amount"]
    
    embed=hikari.Embed(title=f"Note Taken", description=f"**ID:** #{note_id}\n**Amount:** {amount:,}\n**Note:** {note}", color=random.randint(0x0, 0xffffff))
    embed.set_thumbnail(member.avatar_url)
    embed.set_footer(text=f"{member.username}'s Donation")

    needs_roles = []
    remove_roles = []
    for dr in donor_roles:
        if int(dr) <= total_donation:
            needs_roles.append(int(donor_roles[dr]))
        else:
            remove_roles.append(int(donor_roles[dr]))
    
    member_roles = member.get_roles()

    added_roles = ""
    for r1 in needs_roles:
        role1 = ctx.app.cache.get_role(r1)
        if role1 not in member_roles:
            await member.add_role(role1)
            added_roles = added_roles + f" {role1.mention}"
    
    removed_roles = ""
    for r2 in remove_roles:
        role2 = ctx.app.cache.get_role(r2)
        if role2 in member_roles:
            await member.remove_role(role2)
            removed_roles = removed_roles + f" {role2.mention}"

    if added_roles != "":
        embed.add_field(name="Roles Added", value=added_roles)
    if removed_roles != "":
        embed.add_field(name="Roles Removed", value=removed_roles)
    
    await ctx.respond(embed=embed, reply=True)

@_donation.child
@lightbulb.add_checks(lightbulb.owner_only| lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | perms_check)
@lightbulb.option("note_id", "the id of the note to delete", required=True, type=int)
@lightbulb.command("remove", "remove a members donation note", aliases=["r", "rn", "removenote", "-"], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _remove(ctx: lightbulb.Context) -> None:
    note_id = ctx.options.note_id
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    donos = cluster["donations"]["donations"]

    dono = donos.find_one({
        "note_id": {"$eq": note_id},
        "guild": {"$eq": guild_id}
    })
    if dono == None:
        await ctx.respond("Unknown Note ID", reply=True)
        return
    
    a = dono["amount"]
    n = dono["note"]
    embed=hikari.Embed(title="Note Deleted", color=random.randint(0x0, 0xffffff), description=f"**Amount:** {a:,}\n**Note:** {n}")
    member = await ctx.app.rest.fetch_member(guild_id, dono["member"])
    
    if member != None:
        embed.set_thumbnail(member.avatar_url)
        embed.set_footer(text=f"{member.username}'s Donation")
    
    donos.delete_one({
        "note_id": note_id,
        "guild": guild_id
    })

    cluster2 = MongoClient(mongoclient)
    donos2 = cluster2["donations"]["donations"]
    dono2 = donos2.find({"guild": guild_id, "member": member.id})
    total_donation = 0
    for d in dono2:
        total_donation += d["amount"]

    needs_roles = []
    remove_roles = []
    for dr in donor_roles:
        if int(dr) <= total_donation:
            needs_roles.append(int(donor_roles[dr]))
        else:
            remove_roles.append(int(donor_roles[dr]))
    
    member_roles = member.get_roles()

    added_roles = ""
    for r1 in needs_roles:
        role1 = ctx.app.cache.get_role(r1)
        if role1 not in member_roles:
            await member.add_role(role1)
            added_roles = added_roles + f" {role1.mention}"
    
    removed_roles = ""
    for r2 in remove_roles:
        role2 = ctx.app.cache.get_role(r2)
        if role2 in member_roles:
            await member.remove_role(role2)
            removed_roles = removed_roles + f" {role2.mention}"

    if added_roles != "":
        embed.add_field(name="Roles Added", value=added_roles)
    if removed_roles != "":
        embed.add_field(name="Roles Removed", value=removed_roles)

    await ctx.respond(embed=embed, reply=True)

@_donation.child
@lightbulb.option("member", "the member to check the notes of", required=False, default=None, type=hikari.Member)
@lightbulb.command("show", "check the notes of a member", aliases=["c", "s", "notes", "ns"], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _show(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    if member == None:
        member = ctx.event.message.member
    guild_id = ctx.event.message.guild_id

    cluster = MongoClient(mongoclient)
    donos = cluster["donations"]["donations"]

    dono = donos.find({"guild": guild_id, "member": member.id})

    notes = []
    pages = []
    counter1 = 0
    page_limit = 9
    total_donation = 0

    for d in dono:
        total_donation += d["amount"]
        notes.append(d)

    total_pages1 = len(notes) % page_limit
    if total_pages1 == 0:
        total_pages = round(len(notes) / page_limit)
    else:
        total_pages = round((len(notes) // page_limit) + 1)
    total_count = len(notes)
    
    if total_pages == 0:
        embed=hikari.Embed(color=random.randint(0x0, 0xffffff), description=f"Donor: {member} ({member.id})\nTotal Donation(s): {total_count}\nTotal Amount: {total_donation:,}")
        embed.set_thumbnail(member.avatar_url)
        pages.append(embed)

    else:
        for n1 in range(0, total_pages):
            embed=hikari.Embed(color=random.randint(0x0, 0xffffff), description=f"Donor: {member} ({member.id})\nTotal Donation(s): {total_count}\nTotal Amount: {total_donation:,}")
            # embed.set_footer(text=f"{member}", icon=member.avatar_url)
            embed.set_thumbnail(member.avatar_url)
            for n2 in range(0, 9):
                try:
                    n_id = notes[0]["note_id"]
                    a = notes[0]["amount"]
                    no = notes[0]["note"]
                    embed.add_field(name=f"Note #{n_id}", value=f"Amount: {a:,}\nNote: {no}", inline=True)
                    notes.pop(0)
                except:
                    pass
            pages.append(embed)

    navigator = nav.NavigatorView(pages=pages)
    await navigator.send(ctx.event.message.channel_id)

@_donation.child
@lightbulb.add_checks(lightbulb.owner_only| lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | perms_check)
@lightbulb.option("note", "the new note", required=False, type=str, default=None, modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.option("amount", "the new amount", required=False, type=int, default=None)
@lightbulb.option("note_id", "the note to edit", required=True, type=int)
@lightbulb.command("edit", "edit a note of a member", aliases=["e"], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _show(ctx: lightbulb.Context) -> None:
    note_id = ctx.options.note_id
    guild_id = ctx.event.message.guild_id
    amount = ctx.options.amount
    note = ctx.options.note

    if note == None and amount == None:
        await ctx.respond("You cant edit a note without mention which note to edit", reply=True)
        return

    cluster = MongoClient(mongoclient)
    donos = cluster["donations"]["donations"]

    dono = donos.find_one({
        "note_id": {"$eq": note_id},
        "guild": {"$eq": guild_id}
    })

    if dono == None:
        await ctx.respond("Unknown Note ID", reply=True)
        return
    
    if amount != None:
        if amount <= 0:
            await ctx.respond("Invalid amount", reply=True)
            return
        dono["amount"] = amount
    
    if note != None:
        dono["note"] = note

    a = dono["amount"]
    n = dono["note"]
    embed=hikari.Embed(title=f"Note Updated", description=f"**ID:** #{note_id}\n**Amount:** {a}\n**Note:** {n}", color=random.randint(0x0, 0xffffff))
    member = await ctx.app.rest.fetch_member(guild_id, dono["member"])
    
    if member != None:
        embed.set_thumbnail(member.avatar_url)
        embed.set_footer(text=f"{member.username}'s Donation")

    donos.update_one({"note_id": {"$eq": note_id}, "guild": {"$eq": guild_id}}, {"$set": {"note": dono["note"], "amount": dono["amount"]}})

    cluster2 = MongoClient(mongoclient)
    donos2 = cluster2["donations"]["donations"]
    dono2 = donos2.find({"guild": guild_id, "member": member.id})
    total_donation = 0
    for d in dono2:
        total_donation += d["amount"]

    needs_roles = []
    remove_roles = []
    for dr in donor_roles:
        if int(dr) <= total_donation:
            needs_roles.append(int(donor_roles[dr]))
        else:
            remove_roles.append(int(donor_roles[dr]))
    
    member_roles = member.get_roles()

    added_roles = ""
    for r1 in needs_roles:
        role1 = ctx.app.cache.get_role(r1)
        if role1 not in member_roles:
            await member.add_role(role1)
            added_roles = added_roles + f" {role1.mention}"
    
    removed_roles = ""
    for r2 in remove_roles:
        role2 = ctx.app.cache.get_role(r2)
        if role2 in member_roles:
            await member.remove_role(role2)
            removed_roles = removed_roles + f" {role2.mention}"

    if added_roles != "":
        embed.add_field(name="Roles Added", value=added_roles)
    if removed_roles != "":
        embed.add_field(name="Roles Removed", value=removed_roles)

    await ctx.respond(embed=embed, reply=True)

@_donation.child
@lightbulb.option("item", "the item to check the value of", required=True, type=str)
@lightbulb.command("value", "check the item value")
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _value(ctx: lightbulb.Context) -> None:
    item = ctx.options.item.lower()

    cluster = MongoClient(mongoclient)
    itemlist = cluster["donations"]["itemlist"]

    itemdata = itemlist.find_one({"name": item})

    if not itemdata:
        items = itemlist.find()
        for item in items:
            if item in item['aliases']:
                itemdata = item
                break
        return await ctx.respond(hikari.Embed(description=f"""Item with name or aliase "{item}" not found.""", color=bot_config['color']['default']), reply=True)
    
    embed = hikari.Embed(
        title = f"Item Value",
        color = bot_config['color']['default'],
        description = f"""{bot_config['emoji']['blue_arrow2']} **Item:** `{itemdata['name']}`
{bot_config['emoji']['blue_arrow2']} **Value:** `⏣ {int(itemdata['value']):,}`
{bot_config['emoji']['blue_arrow2']} **Aliases: {(str(itemdata['aliases'])[1:][:-1]).replace("'", "`")}"""
    )
    await ctx.respond(embed=embed)

@_donation.child
@lightbulb.add_checks(lightbulb.owner_only | lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option("aliases", "aliases for this item", type=str, modifier=lightbulb.commands.base.OptionModifier(2))
@lightbulb.option("value", "the value of the item", type=str)
@lightbulb.option("item", "the item to add", type=str)
@lightbulb.command("add", "add a item to the item list", aliases=['+'])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _add(ctx: lightbulb.Context) -> None:
    newitem = ctx.options.item.lower()
    value = ctx.options.value
    aliases = ctx.options.aliases

    try:
        value = int(value)
    except:
        try:
            if "e" in value:
                first_digit, how_many_zeros = value.split("e")
                value = int(f"{first_digit}{'0' * int(how_many_zeros)}")
            else:
                await ctx.respond("Invalid value", reply=True, flags=ephemeral)
                return
        except:
            await ctx.respond("Invalid value", reply=True, flags=ephemeral)
            return

    if value <= 0:
        await ctx.respond("Invalid value", reply=True, flags=ephemeral)
        return
    
    if newitem in aliases:
        aliases.pop(aliases.index(newitem))
    
    cluster = MongoClient(mongoclient)
    itemlist = cluster["donations"]["itemlist"]

    itemdata = itemlist.find_one({"name": newitem})

    if itemdata:
        return await ctx.respond(hikari.Embed(description=f"""Item with name or aliase "{newitem}" already exists.""", color=bot_config['color']['default']), reply=True)

    
    items = itemlist.find()
    item_l = []
    for item in items:
        item_l.append(item['name'])
        for i in item['aliases']:
            item_l.append(i)
    
    if newitem in item_l:
        return await ctx.respond(hikari.Embed(description=f"""Item with name or aliase "{newitem}" already exists.""", color=bot_config['color']['default']), reply=True)
    
    for item in aliases:
        if item in item_l:
            return await ctx.respond(hikari.Embed(description=f"""Item with name or aliase "{item}" already exists.""", color=bot_config['color']['default']), reply=True)

    itemdata = {
        "name": newitem,
        "value": value,
        "aliases": aliases
    }

    itemlist.insert_one(itemdata)

    embed = hikari.Embed(
        title = f"New Item Value",
        color = bot_config['color']['default'],
        description = f"""{bot_config['emoji']['blue_arrow2']} **Item:** `{itemdata['name']}`
{bot_config['emoji']['blue_arrow2']} **Value:** `⏣ {int(itemdata['value']):,}`
{bot_config['emoji']['blue_arrow2']} **Aliases: {(str(itemdata['aliases'])[1:][:-1]).replace("'", "`")}"""
    )
    await ctx.respond(embed=embed)
    
@_donation.child
@lightbulb.option("item", "the item to remove", required=True, type=str)
@lightbulb.command("remove", "remove a item from item list", aliases=['-'])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _remove(ctx: lightbulb.Context) -> None:
    item = ctx.options.item.lower()

    cluster = MongoClient(mongoclient)
    itemlist = cluster["donations"]["itemlist"]
    
    itemdata = itemlist.find_one({"name": item})

    if not itemdata:
        return await ctx.respond(hikari.Embed(description=f"""Item with name "{item}" not found.""", color=bot_config['color']['default']), reply=True)

    itemlist.delete_one({"name": item})
    return await ctx.respond(hikari.Embed(description=f"""Deleted "{item}".""", color=bot_config['color']['default']), reply=True)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)