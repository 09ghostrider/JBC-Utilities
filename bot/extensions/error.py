import hikari
import lightbulb

plugin = lightbulb.Plugin("errorHandler")
ephemeral = hikari.MessageFlag.EPHEMERAL
error = "<a:cross:940923957979254795>"

@plugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    embed = hikari.Embed(title=f"{error} Error", color="FF0000")
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        embed.description = f"> Something went wrong during invocation of command `{event.context.command.name}`."
        await event.context.respond(embed=embed, reply=True, flags=ephemeral)
        raise event.exception

    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.NotOwner):
        embed.description = f"> You are not the owner of this bot."
    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        embed.description = f"> This command is on cooldown. Retry in `{exception.retry_after:.2f}` seconds."
    if isinstance(exception, lightbulb.errors.CheckFailure):
        embed.description = f"> You do not have the right permissions to use this command"
    elif isinstance(exception, lightbulb.errors.NotEnoughArguments):
        args = ""
        for arg in exception.missing_options:
            args = args + f"`{arg.name}`, "
        args = args[:-2]
        embed.description = f"> Missing required argument(s): {args}"
    elif isinstance(exception, lightbulb.errors.OnlyInDM):
        embed.description = f"> This command can only be used in DMs"
    elif isinstance(exception, lightbulb.errors.OnlyInGuild):
        embed.description = f"> This command can only be used in a guild"
    elif isinstance(exception, TypeError):
        embed.description = "> Invalid option type"
    # elif isinstance(exception, lightbulb.errors.CommandNotFound):
    #     embed.description = f"> Unknown command / is currently disabled"
    else:
        embed.description = f"> There was a error with this command"
        raise exception

    try:
        await event.context.respond(embed=embed, flags=ephemeral, reply=True)
    except:
        await event.context.respond(embed=embed, reply=True)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)