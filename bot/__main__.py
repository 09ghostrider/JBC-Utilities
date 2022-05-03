import os
import hikari
import lightbulb
import pathlib
import random
import miru
import json
from bot import extensions
from bot.extensions.roles import pingroles
# from bot.extensions.giveaway import giveaway_view
from dotenv import load_dotenv
from lightbulb.ext import tasks

load_dotenv()
with open("./configs/config.json") as f:
    bot_config = json.load(f)
ephemeral = hikari.MessageFlag.EPHEMERAL

bot = lightbulb.BotApp(
    token=os.getenv("TOKEN"),
    prefix=lightbulb.when_mentioned_or(bot_config["prefix"]),
    # logs={
    #     "version": 1,
    #     "incremental": True,
    #     "loggers": {
    #         "hikari": {"level": "INFO"},
    #         "hikari.ratelimits": {"level": "TRACE_HIKARI"},
    #         "lightbulb": {"level": "DEBUG"},
    #     }
    # },
    default_enabled_guilds=bot_config["default_guilds"],
    ignore_bots=True,
    owner_ids=bot_config["owner_ids"],
    case_insensitive_prefix_commands=True
)

bot.load_extensions_from(pathlib.Path(os.path.realpath(extensions.__file__)).parent, must_exist=True)
bot.load_extensions("lightbulb.ext.filament.exts.superuser")
miru.load(bot)
tasks.load(bot)

@bot.listen(hikari.StartedEvent)
async def _on_started(event:hikari.StartedEvent) -> None:
    channel = await bot.rest.fetch_channel(bot_config["logging"]["startup"])
    await channel.send("Bot has started")

    view = pingroles()
    view.start_listener()

    # view2 = giveaway_view()
    # view2.start_listener()

@bot.listen(hikari.StoppingEvent)
async def _on_ended(event:hikari.StoppingEvent) -> None:
    channel = await bot.rest.fetch_channel(bot_config["logging"]["startup"])
    await channel.send("Bot has Stopped")

@bot.command()
@lightbulb.option("extension", "The extension to reload", modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("reload", "reload a bots extension")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _reload(ctx: lightbulb.Context) -> None:
    extension = ctx.options.extension
    try:
        ctx.bot.reload_extensions(f"bot.extensions.{extension}")
        embed = hikari.Embed(description=f"Reloaded extention {extension}", color=bot_config["color"]["default"])
    except Exception as e:
        embed = hikari.Embed(description=f"Reloading extention {extension} failed.\nError: {e}", color=bot_config["color"]["default"])
    await ctx.respond(embed=embed, reply=True)

@bot.command()
@lightbulb.option("extension", "The extension to load", modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("load", "load a bots extension")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _load(ctx: lightbulb.Context) -> None:
    extension = ctx.options.extension
    try:
        ctx.bot.load_extensions(f"bot.extensions.{extension}")
        embed = hikari.Embed(description=f"Loaded extention {extension}", color=bot_config["color"]["default"])
    except Exception as e:
        embed = hikari.Embed(description=f"loading extention {extension} failed.\nError: {e}", color=bot_config["color"]["default"])
    await ctx.respond(embed=embed, reply=True)

@bot.command()
@lightbulb.option("extension", "The extension to load", modifier=lightbulb.commands.base.OptionModifier(3))
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("unload", "Unload a bots extension")
@lightbulb.implements(lightbulb.PrefixCommand)
async def _unload(ctx: lightbulb.Context) -> None:
    extension = ctx.options.extension
    try:
        ctx.bot.unload_extensions(f"bot.extensions.{extension}")
        embed = hikari.Embed(description=f"Unloaded extention {extension}", color=bot_config["color"]["default"])
    except Exception as e:
        embed = hikari.Embed(description=f"Unloading extention {extension} failed.\nError: {e}", color=bot_config["color"]["default"])
    await ctx.respond(embed=embed, reply=True)

if __name__ == "__main__":
    if os.name != "nt":
        import uvloop
        uvloop.install()

    bot.run(
        status=hikari.Status.IDLE,
        activity=hikari.Activity(
            name=f"discord.gg/1vs | jbc help",
            type=hikari.ActivityType.WATCHING,
        )
    )