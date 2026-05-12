import bot
import config
import events
import slash_commands

bot = bot.bot

bot.run(reconnect=True, token=config.TOKEN)
