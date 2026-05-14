import discord
import wavelink
import bot
import embeds
from discord import app_commands

bot = bot.bot


async def queue_autocomplete(
    interaction: discord.Interaction,
    current: str
):
    player = interaction.guild.voice_client

    if not player:
        return []

    choices = []

    for index, song in enumerate(player.queue):
        text = f"{song.title} - {song.author}"

        if (
            current.lower() in song.title.lower()
            or current.lower() in song.author.lower()
        ):
            choices.append(
                app_commands.Choice(
                    name=text[:100],
                    value=str(index)
                )
            )

    return choices[:25]


@bot.tree.command(name='play', description='Play a song!')
async def connect(interaction: discord.Interaction):

    if not interaction.user.voice:
        await interaction.response.send_message("You are not in a voice channel", ephemeral=True)
        return

    await interaction.response.send_modal(embeds.QueueModal())


@bot.tree.command(name='queue', description='Take a look at the current queue')
async def queue(interaction: discord.Interaction):

    if not interaction.guild.voice_client:
        await interaction.response.send_message("I'm not connected to any voice channels")
        return

    player: wavelink.Player = interaction.guild.voice_client
    if player.queue.is_empty:
        await interaction.response.send_message("Current Queue is Empty", ephemeral=True)
        return

    queueEmbeds = embeds.QueueEmbed(player=player)

    await interaction.response.send_message(embed=queueEmbeds[0], view=embeds.QueueView(embeds=queueEmbeds), ephemeral=True)


@bot.tree.command(name="remove", description="Removes a song from the current queue")
@app_commands.autocomplete(song=queue_autocomplete)
async def remove(interaction: discord.Interaction, song: str):

    if not interaction.guild.voice_client:
        await interaction.response.send_message("I'm not playing any song", ephemeral=True)
        return

    player: wavelink.Player = interaction.guild.voice_client

    if player.queue.is_empty:
        await interaction.response.send_message("Current Queue is empty", ephemeral=True)
        return

    await interaction.response.send_message(f"Removed **{player.queue.peek(int(song)).title} - {player.queue.peek(int(song)).author}**")
    player.queue.delete(int(song))
