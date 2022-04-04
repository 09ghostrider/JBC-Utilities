import hikari
import lightbulb
import random
import miru
import pymongo
from pymongo import MongoClient
import datetime
from miru.ext import nav

plugin = lightbulb.Plugin("donations")

with open("./secrets/prefix") as f:
    prefix = f.read().strip()

with open("./secrets/db") as f:
    mongoclient = f.read().strip()

@lightbulb.Check
def perms_check(ctx: lightbulb.Context) -> None:
    cluster = MongoClient(mongoclient)
    configs = cluster["donations"]["server_configs"]

    config = configs.find_one({"guild": ctx.event.message.guild_id})
    if config == None:
        return False
    
    for r in config["req"]:
        role = ctx.app.cache.get_role(r)
        if role in ctx.member.get_roles():
            return True
    return False

@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("donation", "maintain and manage donations of a member", aliases=["dono"])
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
@lightbulb.option("amount", "the amount to add", type=int, required=True)
@lightbulb.option("member", "the member to add donation", type=hikari.Member, required=True)
@lightbulb.command("add", "add amount to a members donation", aliases=["a", "sn", "setnote", "+"], inherit_checks=True)
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def _add(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    amount = int(ctx.options.amount)
    note = ctx.options.note

    if amount <= 0:
        await ctx.respond("Invalid amount", reply=True)
        return
    
    if member.is_bot == True:
        await ctx.respond("You can not add donation to bots", reply=True)
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

    embed=hikari.Embed(title=f"Note Taken", description=f"**ID:** #{note_id}\n**Amount:** {amount}\n**Note:** {note}", color=random.randint(0x0, 0xffffff))
    embed.set_thumbnail(member.avatar_url)
    embed.set_footer(text=f"{member.username}'s Donation")
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
        await ctx.respond("Unknown Note ID")
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
    await navigator.send(ctx.event.message.channel_id)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)