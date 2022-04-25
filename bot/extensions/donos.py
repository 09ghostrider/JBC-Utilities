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

plugin = lightbulb.Plugin("donations")
ephemeral = hikari.MessageFlag.EPHEMERAL

load_dotenv()
mongoclient = os.getenv("DATABASE")
with open("./secrets/prefix") as f:
    prefix = f.read().strip()

donor_roles = {
    "5000000": 851467779500802169,
    "25000000": 851467810713632808,
    "50000000": 851467811338321970,
    "100000000": 851631415040671816,
    "250000000": 851631453414359071,
    "500000000": 851631177085222952,
    "750000000": 851631180336070739,
    "1000000000": 851631182776893482,
    "2000000000": 954550639776657449,
    "3000000000": 954550731921313792,
    "4000000000": 954550735528419368,
    "5000000000": 954550744390971492
}

@lightbulb.Check
def perms_check(ctx: lightbulb.Context) -> None:
    cluster = MongoClient(mongoclient)
    configs = cluster["donations"]["server_configs"]

    config = configs.find_one({"guild": ctx.interaction.guild_id})
    if config == None:
        return False
    
    roles = ctx.interaction.member.get_roles()
    for r in config["req"]:
        role = ctx.app.cache.get_role(r)
        if role in roles:
            return True
    return False

@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("donation", "maintain and manage donations of a member", aliases=["dono"])
@lightbulb.implements(lightbulb.SlashCommandGroup)
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
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _add(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
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

    guild_id = ctx.interaction.guild_id

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
    
    embed=hikari.Embed(title=f"Note Taken", description=f"**ID:** #{note_id}\n**Amount:** {amount}\n**Note:** {note}", color=random.randint(0x0, 0xffffff))
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
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _remove(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    note_id = ctx.options.note_id
    guild_id = ctx.interaction.guild_id

    cluster = MongoClient(mongoclient)
    donos = cluster["donations"]["donations"]

    dono = donos.find_one({
        "note_id": {"$eq": note_id},
        "guild": {"$eq": guild_id}
    })
    if dono == None:
        await ctx.respond("Unknown Note ID", flags=ephemeral)
        return
    
    a = dono["amount"]
    n = dono["note"]
    embed=hikari.Embed(title="Note Deleted", color=random.randint(0x0, 0xffffff), description=f"**Amount:** {a}\n**Note:** {n}")
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
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _show(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE, flags=ephemeral)
    member = ctx.options.member
    if member == None:
        member = ctx.interaction.member
    guild_id = ctx.interaction.guild_id

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
        embed=hikari.Embed(color=random.randint(0x0, 0xffffff), description=f"Donor: {member} ({member.id})\nTotal Donation(s): {total_count}\nTotal Amount: {total_donation}")
        embed.set_thumbnail(member.avatar_url)
        pages.append(embed)

    else:
        for n1 in range(0, total_pages):
            embed=hikari.Embed(color=random.randint(0x0, 0xffffff), description=f"Donor: {member} ({member.id})\nTotal Donation(s): {total_count}\nTotal Amount: {total_donation}")
            # embed.set_footer(text=f"{member}", icon=member.avatar_url)
            embed.set_thumbnail(member.avatar_url)
            for n2 in range(0, 9):
                try:
                    n_id = notes[0]["note_id"]
                    a = notes[0]["amount"]
                    no = notes[0]["note"]
                    embed.add_field(name=f"Note #{n_id}", value=f"Amount: {a}\nNote: {no}", inline=True)
                    notes.pop(0)
                except:
                    pass
            pages.append(embed)

    navigator = nav.NavigatorView(pages=pages)
    await ctx.respond("Shown Below", flags=ephemeral)
    await navigator.send(ctx.interaction.channel_id)

@_donation.child
@lightbulb.add_checks(lightbulb.owner_only| lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR) | perms_check)
@lightbulb.option("note", "the new note", required=False, type=str, default=None)
@lightbulb.option("amount", "the new amount", required=False, type=str, default=None)
@lightbulb.option("note_id", "the note to edit", required=True, type=int)
@lightbulb.command("edit", "edit a note of a member", aliases=["e"], inherit_checks=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _show(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    note_id = ctx.options.note_id
    guild_id = ctx.interaction.guild_id
    amount = ctx.options.amount
    note = ctx.options.note

    if note == None and amount == None:
        await ctx.respond("You cant edit a note without mention what to edit", reply=True, flags=ephemeral)
        return

    cluster = MongoClient(mongoclient)
    donos = cluster["donations"]["donations"]

    dono = donos.find_one({
        "note_id": {"$eq": note_id},
        "guild": {"$eq": guild_id}
    })

    if dono == None:
        await ctx.respond("Unknown Note ID", flags=ephemeral)
        return
    
    if amount != None:
        try:
            amount2 = int(amount)
        except:
            try:
                if "e" in amount:
                    first_digit, how_many_zeros = amount.split("e")
                    amount2 = int(f"{first_digit}{'0' * int(how_many_zeros)}")
                else:
                    await ctx.respond("Invalid amount", reply=True, flags=ephemeral)
                    return
            except:
                await ctx.respond("Invalid amount", reply=True, flags=ephemeral)
                return
        if amount2 <= 0:
            await ctx.respond("Invalid amount", reply=True, flags=ephemeral)
            return
        dono["amount"] = amount2
    
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


def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)