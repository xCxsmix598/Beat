import discord
from discord.ext import commands
import wavelink

intents = discord.Intents.all()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():

    print(f'{bot.user.name} is online')
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command/s")
    node = [wavelink.Node(
        identifier="MAIN",
        client=bot,
        uri="http://localhost:2333",
        password="youshallnotpass"
    )]
    await wavelink.Pool.connect(nodes=node)
