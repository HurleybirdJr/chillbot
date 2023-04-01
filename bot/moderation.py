import discord
import sys
from discord.ext import commands
from discord import app_commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        # Variables to pre-load
        self.vars_loaded = False
        self.get_vars()
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name='Report Message',
            callback=self.report_message,
        )
        self.bot.tree.add_command(self.ctx_menu)

    def get_vars(self):
        if not self.vars_loaded:
            try:
                print(f"`Moderation` variables loaded")
                self.vars_loaded = True
            except AttributeError:
                return None

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    async def cog_load(self):
        print(f"`Moderation` cog loaded")
        self.get_vars()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:  # Don't reply to itself. Could again be client for you
            return
        if not message.guild:
            if "!secret" in message.content.lower():
                # await message.response.send_modal(Report())
                # chillsynth_id = self.bot.get_guild(int(os.getenv("DEBUG_GUILD_ID")))
                # log_channel = discord.utils.get(chillsynth_id.channels, name="moderator-chat")

                sys.stdout.write(f"DM received from {message.author.display_name}")

    @app_commands.default_permissions(moderate_members=True)
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        """Gets bot latency"""
        embed = discord.Embed(title='**Current Latency**',
                              description=f"Retrieved latest bot latency",
                              color=0xeee657)
        embed.add_field(name=None, value=f'Latency: **{round(self.bot.latency * 1000)}**ms')
        await interaction.response.send_message(embed=embed)

    # Removes image posting permissions from specified user
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.command(name="noimg", description="Toggle noimg role for user")
    async def noimg(self, interaction: discord.Interaction, member: discord.Member):
        noimg_role = discord.utils.get(interaction.guild.roles, name="no img :(")
        va_role = discord.utils.get(interaction.guild.roles, name="Visual Artist")
        en_msg = "Removed image posting permissions"
        dis_msg = "Restored image posting permissions"

        if noimg_role not in member.roles:
            await member.add_roles(noimg_role, reason=en_msg)
            if va_role in member.roles:
                await member.remove_roles(va_role, reason=en_msg)
            fin_msg = en_msg
        else:
            await member.remove_roles(noimg_role, reason=en_msg)
            fin_msg = dis_msg

        await interaction.response.send_message(f"{fin_msg} for user {member.mention}")

    @app_commands.default_permissions(use_application_commands=True)
    @app_commands.checks.has_permissions(use_application_commands=True)
    async def report_message(self, interaction: discord.Interaction, message: discord.Message) -> None:
        await interaction.response.send_message(
            f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
        )
        report_log_channel = discord.utils.get(interaction.guild.channels, name="moderator-chat")
        # Handle report by sending it into a log channel
        # log_channel = discord.utils.get(interaction.guild.channels, name="moderator-chat")
        embed = discord.Embed(title='Reported Message',
                              colour=discord.Colour.red())
        if message.content:
            embed.description = message.content

        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.timestamp = message.created_at

        url_view = discord.ui.View()
        url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

        # await report_log_channel.send(f"{mod_role.mention}")  # Tag Moderators
        await report_log_channel.send(embed=embed, view=url_view)

    @app_commands.command()
    async def create_invite(self, interaction: discord.Interaction, channel: discord.TextChannel,
                            age: int, uses: int):
        invite = await channel.create_invite(max_age=age, max_uses=uses)
        await interaction.channel.send(f"Successfully created invite: {str(invite)} for channel <#{channel.id}>")

# USER REPORT MODAL
# class Report(discord.ui.Modal, title='Report'):
#     report = discord.ui.TextInput(
#         label="What are you reporting?",
#         style=discord.TextStyle.long,
#         placeholder="Please include as much detail as you can...",
#         required=True,
#         min_length=1,
#         max_length=2000
#     )
#
#     async def on_submit(self, interaction: discord.Interaction):
#         report_embed = discord.Embed(title=f"User Report",
#                                      description=f"**{self.report}**\n\nUser ID:{interaction.user.id}",
#                                      timestamp=datetime.now(),
#                                      colour=discord.Colour.red())
#         user_avatar = interaction.user.display_avatar
#         report_embed.set_author(name=interaction.user, icon_url=user_avatar.url)
#         report_embed.set_thumbnail(url=user_avatar.url)
#
#         chillsynth_id = self.bot.get_guild(int(os.getenv("DEBUG_GUILD_ID")))
#         log_channel = discord.utils.get(chillsynth_id.channels, name="moderator-chat")
#
#         log_channel.send(embed=report_embed)
#         sys.stdout.write(f"DM Report Received from {interaction.user.display_name}")
#
#     async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
#         await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
#
#         print(error)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
