import config
import discord
from discord.ext import commands

bot = commands.Bot(
    command_prefix="!", intents=discord.Intents.default())


@bot.event
async def on_ready():

    await bot.tree.sync()
    # await bot.tree.sync(guild=discord.Object(config.GUILD_ID))
    print("Cleared")

bot.run(config.TOKEN)
