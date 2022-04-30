import hikari
import lightbulb

plugin = lightbulb.Plugin("errorHandler")
ephemeral = hikari.MessageFlag.EPHEMERAL
error = "<a:RedCross:944235488808665109>"

@plugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    e = False
    embed = hikari.Embed(title=f"{error} Error", color="FF0000")
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        embed.description = f"> Something went wrong during invocation of command `{event.context.command.name}`."
        e = True

    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.NotOwner):
        embed.description = f"> You are not the owner of this bot."
    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        embed.description = f"> This command is on cooldown. Retry in `{exception.retry_after:.2f}` seconds."
    elif isinstance(exception, lightbulb.errors.CheckFailure):
        embed.description = f"> You do not have the right permissions to use this command"
    elif isinstance(exception, lightbulb.errors.NotEnoughArguments):
        args = ""
        for arg in exception.missing_options:
            args = args + f"`{arg.name}`, "
        args = args[:-2]
        embed.description = f"> Missing required argument(s): {args}"
    elif isinstance(exception, lightbulb.errors.CommandNotFound):
        return
    elif isinstance(exception, lightbulb.errors.OnlyInDM):
        embed.description = f"> This command can only be used in DMs"
    elif isinstance(exception, lightbulb.errors.OnlyInGuild):
        embed.description = f"> This command can only be used in a guild"
    elif isinstance(exception, TypeError):
        embed.description = "> Invalid option type"
    else:
        embed.description = f"> There was a error with this command"
        e = True

    try:
        await event.context.respond(embed=embed, flags=ephemeral, reply=True)
    except:
        try:
            await event.context.respond(embed=embed, reply=True)
        except:
            await event.context.respond(embed=embed)
    
    if e == True:
        raise exception

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)