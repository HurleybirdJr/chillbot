import discord
import wavelink
from discord.ext import commands
from discord import app_commands


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_player = None
        self.vars_loaded = False
        self.get_vars()

    def get_vars(self):
        if not self.vars_loaded:
            try:
                print(f"`Moderation` variables loaded")
                self.vars_loaded = True
            except AttributeError:
                return None

    async def cog_load(self):
        print(f"`Moderation` cog loaded")
        self.get_vars()
        # Creating a node is as simple as this...
        # The node will be automatically stored to the global NodePool...
        # You can create as many nodes as you like, most people only need 1...
        node: wavelink.Node = wavelink.Node(uri='http://localhost:2333', password='youshallnotpass')
        await wavelink.NodePool.connect(client=self.bot, nodes=[node])

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"Node {node.id} is ready!")

    @app_commands.command(name="connect")
    async def connect(self, interaction: discord.Interaction, *, channel: discord.VoiceChannel = None):
        try:
            channel = channel or interaction.message.author.voice.channel
        except AttributeError:
            await interaction.response.send_message('No voice channel to connect to. Please either provide / join one.')

        # vc is short for voice client...
        # Our "vc" will be our wavelink. Player as type hinted below...
        # wavelink.Player is also a VoiceProtocol...

        node = wavelink.NodePool.get_node()  # Could return None, if the Player was not found..
        self.current_player = node.get_player(interaction.guild.id)

        vc: wavelink.Player = await channel.connect(cls=wavelink.Player)
        self.current_player.autoplay = True

        await interaction.response.send_message(f"Connected to {channel}")
        return vc

    @app_commands.command(name="file")
    async def playfile(self, interaction: discord.Interaction):
        """Simple play command."""

        voice_client = discord.utils.get(interaction.client.voice_clients, guild=interaction.message.guild)
        voice_channel = interaction.message.author.voice.channel

        if voice_client:
            if not voice_client.connect():
                await voice_channel.connect()
                voice_client.play(discord.FFmpegPCMAudio(executable='C:\\FFmpeg\\bin\\ffmpeg.exe', source='NEWYEAR.mp3'))
        else:
            await voice_channel.connect()
            voice_client = discord.utils.get(interaction.client.voice_clients, guild=interaction.message.guild)
            voice_client.play(discord.FFmpegPCMAudio(executable='C:\\FFmpeg\\bin\\ffmpeg.exe', source='NEWYEAR.mp3'))


async def setup(bot):
    await bot.add_cog(Music(bot))
