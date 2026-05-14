import discord
import wavelink
import prevQueue


def embedBuilder(title, author, duration, link, requester, thumbnail, guild_name, guild_icon, source):

    embed = discord.Embed(color=discord.Color.blue(
    ), title="Now Playing", description=f"**[{title}]({link})**")

    embed.set_thumbnail(url=thumbnail)
    embed.set_author(name=guild_name, icon_url=guild_icon)
    embed.add_field(name="Uploader", value=author, inline=True)
    embed.add_field(name="Duration", value=duration, inline=True)
    embed.add_field(name="Source", value=source, inline=True)
    embed.add_field(name="Requester", value=requester, inline=True)

    return embed


class SourceSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(options=[
            discord.SelectOption(
                label="YouTube Music (Default)", value='ytm', default=True),
            discord.SelectOption(label="YouTube", value='yt', default=False)
        ])


class QueueModal(discord.ui.Modal, title="Add to Queue"):

    song = discord.ui.TextInput(
        label="Song Title or URL", placeholder="e.g. Never Gonna Give You Up or https://(music.)youtube.com/*", required=True)

    source = discord.ui.Label(text="Source", component=SourceSelect())

    async def on_submit(self, interaction: discord.Interaction):

        if not interaction.guild.voice_client:
            await interaction.user.voice.channel.connect(self_deaf=True, cls=wavelink.Player)

        query = self.song.value
        source = self.source.component.values[0]
        vc: wavelink.Player = interaction.guild.voice_client

        if source == 'ytm':
            tracks = await wavelink.Playable.search(query, source=wavelink.TrackSource.YouTubeMusic)
        else:
            tracks = await wavelink.Playable.search(query, source=wavelink.TrackSource.YouTube)

        if not tracks:
            await interaction.response.send_message('No tracks Found')
            return

        track: wavelink.Playable = tracks[0]
        track.extras = {"requester": interaction.user.mention}

        vc.text_channel = interaction.channel

        await interaction.response.send_message(f"Added **{track.title} - {track.author}**")

        if vc.playing:
            await vc.queue.put_wait(track)
            return

        await vc.play(track)


class View(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(emoji="⏸️", style=discord.ButtonStyle.green)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):

        player: wavelink.Player = interaction.guild.voice_client
        message: discord.Message = player.message
        embed: discord.Embed = message.embeds[0]

        await interaction.response.defer()
        if not player.paused:
            await player.pause(True)
            button.emoji = "▶️"
            button.style = discord.ButtonStyle.red
            embed.color = discord.Color.yellow()
            embed.title = "Playback Paused"
            player.message = await message.edit(view=self, embed=embed)
        else:
            await player.pause(False)
            button.emoji = "⏸️"
            button.style = discord.ButtonStyle.green
            embed.color = discord.Color.blue()
            embed.title = "Now Playing"
            player.message = await message.edit(view=self, embed=embed)

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):

        player: wavelink.Player = interaction.guild.voice_client
        message: discord.Message = player.message
        embed: discord.Embed = message.embeds[0]
        await interaction.response.defer()
        embed.color = discord.Color.red()
        embed.title = "Playback Stopped"
        await interaction.followup.send(f"{interaction.user.mention} has stopped the playback")
        await interaction.edit_original_response(view=None, embed=embed)
        await player.disconnect()

    @discord.ui.button(emoji="⏮️")
    async def previous(self, interaction: discord.Interaction, button: discord.Button):

        player: wavelink.Player = interaction.guild.voice_client

        if player.queue.history.count <= 1:
            await interaction.response.send_message("Already at the first song in the Queue", ephemeral=True)
            return

        player.queue.put_at(0, player.current)

        player.queue.history.delete(player.queue.history.count - 1)
        await player.play(player.queue.history.get_at(player.queue.history.count - 1))

    @discord.ui.button(emoji="⏭️")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):

        player: wavelink.Player = interaction.guild.voice_client
        try:
            await player.play(player.queue.get())
        except wavelink.exceptions.QueueEmpty:
            await interaction.response.send_message('Already at the last song in the Queue', ephemeral=True)

    @discord.ui.button(emoji="➕")
    async def add_to_queue(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(QueueModal())

    @discord.ui.button(emoji="➖")
    async def remove_from_queue(self, interaction: discord.Interaction, Button: discord.Button):

        if interaction.guild.voice_client.queue.is_empty:
            await interaction.response.send_message("Current Queue is Empty", ephemeral=True)
            return
        await interaction.response.send_message("Use **``/remove <Song Title>``** to remove a song from the current queue", ephemeral=True)
