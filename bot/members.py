import os

from discord.ext import commands
from discord import app_commands
import discord
import pymongo
from datetime import *
import time


class Members(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # DB Setup
        self.client = pymongo.MongoClient(os.getenv("mongo_dev_uri"))
        self.db = self.client["_server"]

    async def cog_load(self):
        print(f"`Members` cog loaded")

    # USERNAME UPDATE
    @commands.Cog.listener()
    async def on_user_update(self, old: discord.Member, new: discord.Member):
        previous_username = f"{old.name}#{old.discriminator}"
        updated_username = f"{new.name}#{new.discriminator}"
        if updated_username is previous_username:  # Username matches - Ignore
            pass
        elif updated_username is not previous_username:  # Username has changed
            print(f"{previous_username} changed to {updated_username}")

            # Search DB record
            key = {"discord_user_ID": new.id}
            search_result = None
            for result in self.db.members.find(key):
                print(f"Found {updated_username} under: ObjectID:{result['_id']}")  # Report to system logs

                search_result = result

            username_updated_value = {
                "$set": {
                    "discord_username": str(f"{updated_username}"),
                    "past_usernames": {
                        "username": [
                            f"{search_result['discord_username']}",
                            f"{search_result['past_usernames']['username'][0]}",
                            f"{search_result['past_usernames']['username'][1]}",
                            f"{search_result['past_usernames']['username'][2]}",
                            f"{search_result['past_usernames']['username'][3]}"
                        ],
                        "user_date_changed": [
                            int(time.time()),
                            search_result['past_usernames']['user_date_changed'][0],
                            search_result['past_usernames']['user_date_changed'][1],
                            search_result['past_usernames']['user_date_changed'][2],
                            search_result['past_usernames']['user_date_changed'][3]
                        ]
                    }
                }
            }

            db_filter = {"discord_user_ID": search_result["discord_user_ID"]}  # Filter by userID
            self.db.members.update_one(db_filter, username_updated_value)

    # NICKNAME UPDATE
    @commands.Cog.listener()
    async def on_member_update(self, old: discord.Member, new: discord.Member):
        if new.nick == old.nick:  # No nickname changes - Ignore
            pass
        elif new.nick is not old.nick:  # Nickname has changed
            print(f"{old.nick} changed to {new.nick}")

            # Search DB record
            key = {"discord_user_ID": new.id}
            search_result = None
            for result in self.db.members.find(key):
                print(f"Found {new.name}#{new.discriminator} under: ObjectID:{result['_id']}")  # Report to system logs

                search_result = result

            nickname_updated_value = {
                "$set": {
                    "server_nickname": str(f"{new.nick}"),
                    "past_nicknames": {
                        "nickname": [
                            f"{search_result['server_nickname']}",
                            f"{search_result['past_nicknames']['nickname'][0]}",
                            f"{search_result['past_nicknames']['nickname'][1]}",
                            f"{search_result['past_nicknames']['nickname'][2]}",
                            f"{search_result['past_nicknames']['nickname'][3]}"
                        ],
                        "nick_date_changed": [
                            int(time.time()),
                            search_result['past_nicknames']['nick_date_changed'][0],
                            search_result['past_nicknames']['nick_date_changed'][1],
                            search_result['past_nicknames']['nick_date_changed'][2],
                            search_result['past_nicknames']['nick_date_changed'][3]
                        ]
                    }
                }
            }

            db_filter = {"discord_user_ID": search_result["discord_user_ID"]}  # Filter by userID
            self.db.members.update_one(db_filter, nickname_updated_value)

    # MEMBER JOIN PROCESS
    @commands.Cog.listener()
    async def on_member_join(self, new_member: discord.Member):
        if new_member.system:  # Official Discord User
            print(f"WOAH! {new_member.name}#{new_member.discriminator} is a system user :)")

        # Search DB record
        key = {"discord_user_ID": new_member.id}
        search_result = None
        for result in self.db.members.find(key):
            print(f"Existing record for {new_member.name}#{new_member.discriminator} "  # Report outcome to system logs
                  f"found: ObjectID:{result['_id']}")

            search_result = result

        if search_result is not None:  # Database entry found!
            print(f"Updating existing record for {new_member.name}#{new_member.discriminator} "
                  f"under: ObjectID:{search_result['_id']}")

            # Update Usernames
            current_full_username = str(f"{new_member.name}#{new_member.discriminator}")  # For comparing usernames
            print(current_full_username)

            if search_result["discord_username"] == current_full_username:  # Check if username needs updating
                print("Username matches!")
            else:  # Username has changed, update entry with new username
                print("Username differs! Updating...")
                username_updated_value = {
                    "$set": {
                        "discord_username": f"{new_member.name}#{new_member.discriminator}",
                        "past_usernames": {
                            "username": [
                                f"{search_result['discord_username']}",
                                f"{search_result['past_usernames']['username'][0]}",
                                f"{search_result['past_usernames']['username'][1]}",
                                f"{search_result['past_usernames']['username'][2]}",
                                f"{search_result['past_usernames']['username'][3]}"
                            ],
                            "user_date_changed": [
                                int(search_result['server_leave_date']),
                                search_result['past_usernames']['user_date_changed'][0],
                                search_result['past_usernames']['user_date_changed'][1],
                                search_result['past_usernames']['user_date_changed'][2],
                                search_result['past_usernames']['user_date_changed'][3]
                            ]
                        },
                        "past_nicknames": {
                            "nickname": [
                                f"{search_result['server_nickname']}",
                                f"{search_result['past_nicknames']['nickname'][0]}",
                                f"{search_result['past_nicknames']['nickname'][1]}",
                                f"{search_result['past_nicknames']['nickname'][2]}",
                                f"{search_result['past_nicknames']['nickname'][3]}"
                            ],
                            "nick_date_changed": [
                                int(search_result['server_leave_date']),
                                search_result['past_nicknames']['nick_date_changed'][0],
                                search_result['past_nicknames']['nick_date_changed'][1],
                                search_result['past_nicknames']['nick_date_changed'][2],
                                search_result['past_nicknames']['nick_date_changed'][3]
                            ]
                        }
                    }
                }

                db_filter = {"discord_user_ID": search_result["discord_user_ID"]}  # Filter by userID
                self.db.members.update_one(db_filter, username_updated_value)

            # Update Server Join/Leave Date
            server_updated_values = {
                "$set": {
                    "server_join_date": int(time.time()),
                    "server_leave_date": None,  # Epoch will be filled if left server
                }
            }

            query = {"discord_user_ID": search_result["discord_user_ID"]}
            self.db.members.update_one(query, server_updated_values)

        elif search_result is None:
            print(f"No record found for {new_member.name}#{new_member.discriminator}; Creating new entry.")

            # Create new entry in DB
            creation_date = new_member.created_at
            print(str(creation_date))

            self.db.members.insert_one(
                {
                    "discord_username": str(f"{new_member.name}#{new_member.discriminator}"),
                    "discord_user_ID": int(new_member.id),
                    "discord_creation_date": int(creation_date.timestamp()),  # strftime("%d/%m/%Y @ %H:%M:%S")
                    "server_nickname": str(f"{new_member.name}"),
                    "server_join_date": int(time.time()),
                    "server_leave_date": None,  # Epoch will be filled if left server
                    "is_booster": bool(False),
                    "past_usernames": {
                        "username": ["", "", "", "", ""],
                        "user_date_changed": ["", "", "", "", ""]
                    },
                    "past_nicknames": {
                        "nickname": ["", "", "", "", ""],
                        "nick_date_changed": ["", "", "", "", ""]
                    }
                }
            )
        else:
            print("Not sure what I'm supposed to do now... :/")

    @app_commands.command(name="feedback", description="Submit feedback")
    async def feedback(self, interaction: discord.Interaction):
        """Send feedback to the server team"""
        await interaction.response.send_modal(Feedback())

    @app_commands.command(name="report", description="Submit a report")
    async def report(self, interaction: discord.Interaction):
        """Send report to the mod team"""
        await interaction.response.send_modal(UserReport())


# USER REPORT MODAL
class UserReport(discord.ui.Modal, title='Report'):
    reportedUserID = discord.ui.TextInput(
        label="What would you like to report?",
        style=discord.TextStyle.short,
        placeholder="Include 'Username#0000' or user ID",
        required=True,
        min_length=6,
        max_length=38
    )

    report = discord.ui.TextInput(
        label="What would you like to report?",
        style=discord.TextStyle.long,
        placeholder="Please write as much detail as possible...",
        required=True,
        min_length=1,
        max_length=2000
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"Username / ID: {self.reportedUserID}",
                              description=f"**{self.report}**\n",
                              timestamp=datetime.now(),
                              colour=discord.Colour.red())
        user_avatar = interaction.user.display_avatar
        embed.set_author(name=f"Submitted by: {interaction.user}", icon_url=user_avatar.url)
        embed.set_thumbnail(url="https://i.imgur.com/giZ2D5T.gif")

        channel = discord.utils.get(interaction.guild.channels, name="moderator-chat")
        mod_role = interaction.guild.get_role(int(os.getenv('MOD_ROLE_ID')))
        await channel.send(f"{mod_role.mention}")
        await channel.send(embed=embed)

        await interaction.response.send_message(f'Thanks for your report, {interaction.user.name}!', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        print(error)


# USER FEEDBACK MODAL
class Feedback(discord.ui.Modal, title='Feedback'):
    feedback = discord.ui.TextInput(
        label="What would you like to feedback?",
        style=discord.TextStyle.long,
        placeholder="Type your feedback here...",
        required=True,
        min_length=0,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"User Feedback",
                              description=f"**{self.feedback}**\n\nUser ID:{interaction.user.id}",
                              timestamp=datetime.now(),
                              colour=discord.Colour.yellow())
        user_avatar = interaction.user.display_avatar
        embed.set_author(name=interaction.user, icon_url=user_avatar.url)
        embed.set_thumbnail(url=user_avatar.url)

        channel = discord.utils.get(interaction.guild.channels, name="user-feedback")
        await channel.send(embed=embed)

        await interaction.response.send_message(f'Thanks for your feedback, {interaction.user.name}!', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        print(error)


async def setup(bot):
    await bot.add_cog(Members(bot))
