import discord
import wavelink
import bot
from embeds import embedBuilder, View
from datetime import timedelta

bot = bot.bot


@bot.event
async def on_wavelink_track_start(payload: wavelink.TrackStartEventPayload):

    if hasattr(payload, "player"):
        player: wavelink.Player = payload.player
    if hasattr(player, "text_channel"):
        channel = getattr(player, "text_channel")
    track = payload.track
    player.message = await channel.send(view=View(), embed=embedBuilder(track.title, track.author, timedelta(milliseconds=track.length), track.uri, track.extras.requester, track.artwork, player.guild.name, player.guild.icon, track.source.capitalize()))


@bot.event
async def on_wavelink_track_end(payload: wavelink.TrackEndEventPayload):

    player: wavelink.Player = payload.player
    if hasattr(player, "text_channel"):
        channel = getattr(player, "text_channel")
    if hasattr(player, "message"):
        message: discord.Message = getattr(player, "message")
        embed: discord.Embed = message.embeds[0]
    reason = payload.reason
    track = payload.track

    # print(reason)

    if reason == 'finished':
        try:
            await player.play(player.queue.get())
            embed.color = discord.Color.red()
            try:
                await message.edit(view=None, embed=embed)
            except (discord.HTTPException, discord.NotFound):
                player.message = await channel.send(view=View(), embed=embedBuilder(track.title, track.author, timedelta(milliseconds=track.length), track.uri, track.extras.requester, track.artwork, player.guild.name, player.guild.icon, track.source.capitalize()))
        except wavelink.exceptions.QueueEmpty:
            embed.color = discord.Color.red()
            embed.title = "Queue Ended"
            try:
                await message.edit(view=None, embed=embed)
            except (discord.HTTPException, discord.NotFound):
                player.message = await channel.send(view=View(), embed=embedBuilder(track.title, track.author, timedelta(milliseconds=track.length), track.uri, track.extras.requester, track.artwork, player.guild.name, player.guild.icon, track.source.capitalize()))
            await player.disconnect()
    elif reason == 'replaced':
        embed.color = discord.Color.red()
        try:
            await message.edit(view=None, embed=embed)
        except:
            player.message = await channel.send(view=View(), embed=embedBuilder(track.title, track.author, timedelta(milliseconds=track.length), track.uri, track.extras.requester, track.artwork, player.guild.name, player.guild.icon, track.source.capitalize()))
