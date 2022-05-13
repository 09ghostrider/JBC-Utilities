import lightbulb
import hikari

async def edit_perms(ctx:lightbulb.Context, lorul:str, cid:int, rid:int, p):
    reason = f"Action requested by {ctx.event.message.author} ({ctx.event.message.author.id})"

    c = await ctx.app.rest.fetch_channel(cid)
    perms = c.permission_overwrites
    try:
        perm = perms[rid]
        allow = perm.allow
        deny = perm.deny
    except KeyError:
        allow = hikari.Permissions.NONE
        deny = hikari.Permissions.NONE

    if lorul == "lock":
            allow &= ~p
            deny |= p
    elif lorul == "unlock":
        deny &= ~p
        allow |= p
    elif lorul == "reset":
        deny &= ~p
    
    await ctx.app.rest.edit_permission_overwrites(
        channel = cid,
        target = rid,
        allow = allow,
        deny = deny,
        reason = reason,
        target_type = hikari.PermissionOverwriteType.ROLE
    )