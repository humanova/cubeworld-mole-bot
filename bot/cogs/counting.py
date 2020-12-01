# 2020 Emir Erbasan (humanova)
# MIT License, see LICENSE for more details

import discord
import traceback
from utils import confparser, default, permissions, hastebin
from discord.ext import commands, tasks
import tinydb
import datetime
import asyncio
import tabulate
import sys

class Counting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.config = confparser.get("config.json")
        self.cc_table = tinydb.TinyDB('../db/cc-database.json')
        self.auto_cc_mode = False

        self.guild = self.bot.get_guild(id=int(self.config.guild_id))
        self.mod_channel = self.guild.get_channel(channel_id=int(self.config.mod_channel_id))
        self.counting_channel = self.guild.get_channel(channel_id=int(self.config.counting_channel_id))
        self.cm_role = self.guild.get_role(role_id=int(self.config.cm_role_id))
        self.cc_role = self.guild.get_role(role_id=int(self.config.cc_role_id))

        self.cc_control_task.start()

    def cog_unload(self):
        self.cc_control_task.cancel()

    @tasks.loop(minutes=30)
    async def cc_control_task(self):
        usr = tinydb.Query()
        q_res = self.cc_table.search(usr.isCC == True)
        curr_timestamp = datetime.datetime.now().timestamp()

        uncc_list = [mem['userid'] for mem in q_res if mem['is_perm'] is False and curr_timestamp > mem['uncc_timestamp']]
        # uncc from db
        for m_id in uncc_list:
            self.uncc_user_db(m_id)
        # uncc from guild
        to_be_uncced_member = [discord.utils.get(self.guild.members, id=user_id) for user_id in uncc_list]
        for member in [member for member in to_be_uncced_member if member is not None]:
            self.uncc_user_db(member.id)
            await member.remove_roles(self.cc_role)
            embed = discord.Embed(title=" ", description=f"User <@{member.id}> got UNCC'd.", color=0x75df00)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await self.mod_channel.send(embed=embed)
            await asyncio.sleep(1)  # in case of exceeding send_message API limit

    async def init_cc_table(self):
        cc_members = [member for member in self.guild.members if self.cc_role in member.roles]

        usr = tinydb.Query()
        q_res = self.cc_table.search(usr.isCC == True)
        db_cc_ids = [u['userid'] for u in q_res]
        # remove already cc'ed members from the list
        not_cced_db_members = [mem for mem in cc_members if mem.id not in db_cc_ids]

        # cc users who aren't cced in db
        for mem in not_cced_db_members:
            await self.cc_user(mem.id, mem.name)

        # uncc not cc'ed (in db) member
        not_cced_guild_members = [u['userid'] for u in q_res if u['userid'] not in [m.id for m in cc_members]]
        for mem_id in not_cced_guild_members:
            self.uncc_user_db(mem_id)

        print(f"{len(not_cced_db_members)} users got cc'd with initcctable command")
        print(f"{len(not_cced_guild_members)} users got uncc'd with initcctable command")

        log = f"uncced {len(not_cced_guild_members)} users.\n\n"
        log += "\n".join([f"{mem}, {str(self.guild.get_member(user_id=mem))}" for mem in not_cced_guild_members])
        log += f"\n------------------------\ncced {len(not_cced_db_members)} users.\n\n"
        log += "\n".join([f"{mem.id}, {str(mem)}" for mem in not_cced_db_members])
        return log

    async def cc_user(self, user_id, username: str, days: int=7, is_perm=False):
        user = tinydb.Query()
        q_res = self.cc_table.search(user.userid == user_id)
        member = self.guild.get_member(user_id=int(user_id))

        cc_datetime = datetime.datetime.now()
        uncc_datetime = datetime.datetime.now() + datetime.timedelta(days=days)

        user_data = {'userid': user_id,
                     'username': username,
                     'isCC': True,
                     'is_perm': is_perm,
                     'ccCount': 1,
                     'penaltyDays': days,
                     'cc_date': cc_datetime.strftime("%c"),
                     'uncc_date': uncc_datetime.strftime("%c"),
                     'cc_timestamp': cc_datetime.timestamp(),
                     'uncc_timestamp': uncc_datetime.timestamp()
                     }
        try:
            if not q_res:
                self.cc_table.insert(user_data)
            else:
                cc_count = q_res[0]['ccCount']
                user_data['ccCount'] = cc_count + 1
                self.cc_table.upsert(user_data, user.userid == user_id)
            await member.add_roles(self.cc_role)
        except Exception as e:
            print(f"error in cc_user : {e}")
            return None
        return self.cc_table.search(user.userid == user_id)[0]

    def uncc_user_db(self, user_id):
        user = tinydb.Query()
        self.cc_table.update({'isCC': False}, user.userid == user_id)
        return self.cc_table.search(user.userid == user_id)[0]

    def get_cc_timeleft(self, user_id):
        user = tinydb.Query()
        data = self.cc_table.search(user.userid == user_id)[0]

        end_date = datetime.datetime.fromtimestamp(int(data['uncc_timestamp']))
        td = end_date - datetime.datetime.now()
        diff = td.days, td.seconds // 3600, (td.seconds // 60) % 60

        return diff

    def is_cc(self, user_id):
        user = tinydb.Query()
        q_res = self.cc_table.search(user.userid == user_id)
        return True if q_res else False

    def get_user(self, user_id):
        user = tinydb.Query()
        data = self.cc_table.search(user.userid == user_id)[0]
        return data if data else None

    def get_cc_table(self):
        user = tinydb.Query()
        q_res = self.cc_table.search(user.isCC == True or user.is_perm == True)

        cc_users = [[0 for x in range(4)] for y in range(len(q_res))]
        for idx, mem in enumerate(q_res):
            diff = self.get_cc_timeleft(mem['userid'])
            time_left_str = f"{diff[0]}d {diff[1]}h"

            data = []
            cc_users[idx][0] = mem['userid']
            cc_users[idx][1] = mem['username']
            cc_users[idx][2] = time_left_str
            cc_users[idx][3] = mem['is_perm']
            cc_users.append(data)
        table = tabulate.tabulate(cc_users, ["userid", "username", "time_left", "is_perm"], tablefmt="ortabgtbl")

        return table

    def get_cc_embed(self, member, days=None, is_perm=False):
        ban_description = f"User <@{member.id}> successfully got CC'd. "
        ban_description += "(perm ban)" if is_perm else f"(Banned for `{days} days`)"
        embed = discord.Embed(title=" ", description=ban_description, color=0x75df00)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        return embed

    def get_cc_error_embed(self, member):
        embed = discord.Embed(title=" ", description=f"Error while CC'ing <@{member.id}>", color=0xFF0000)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        return embed

    def get_message_event_embed(self, event_title: str, message: discord.Message, new_message: discord.Message=None):
        embed = discord.Embed(title=event_title, color=0xe5e500)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name="Author", value=f"<@{message.author.id}>", inline=False)
        if new_message:
            embed.add_field(name="Old Message", value=message.content, inline=False)
            embed.add_field(name="New Message", value=new_message.content, inline=False)
        else:
            embed.add_field(name="Message", value=message.content, inline=False)
        is_count_mod = True if self.cm_role in message.author.roles else False
        embed.set_footer(text=f"Is Count Mod : {str(is_count_mod)}")
        return embed

    @commands.command()
    @commands.check(permissions.is_count_mod)
    async def cc(self, ctx, member: discord.Member, duration=7):
        """ cc user """
        try:
            usr = await self.cc_user(user_id=member.id, username=str(member), days=duration)
            await self.mod_channel.send(embed=self.get_cc_embed(member, usr['penaltyDays']))
        except Exception as e:
            print(f"error in cc {e}")
            await  self.mod_channel.send(embed=self.get_cc_error_embed(member))

    @commands.command()
    @commands.check(permissions.is_count_mod)
    async def ccperm(self, ctx, member: discord.Member):
        """ perm cc user """
        try:
            usr = await self.cc_user(user_id=member.id, username=str(member), is_perm=True)
            await  self.mod_channel.send(embed=self.get_cc_embed(member, is_perm=True))
        except Exception as e:
            print(f"error in ccperm : {e}")
            await  self.mod_channel.send(embed=self.get_cc_error_embed(member))

    @commands.command()
    @commands.check(permissions.is_count_mod)
    async def ccauto(self, ctx, mode: str):
        """ change auto cc mode"""
        if mode.lower() == "true" or mode.lower() == "on" or mode == "1":
            self.auto_cc_mode = True
        elif mode.lower() == "false" or mode.lower() == "off" or mode == "0":
            self.auto_cc_mode = False
        else:
            return
        embed = discord.Embed(title=" ", description=f"Auto-CC is set to : {self.auto_cc_mode}", color=0xe5e500)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        await self.mod_channel.send(embed=embed)

    @commands.command()
    @commands.check(permissions.is_count_mod)
    async def cclist(self, ctx):
        """ get cc'ed user list """
        try:
            table = self.get_cc_table()
            table_url = await hastebin.post(table)

            embed = discord.Embed(title=" ", description=f"Current CC Table : {table_url}", color=0xe5e500)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

            await ctx.send(embed=embed)
        except Exception as e:
            print(f"error in cclist {e}")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def initcctable(self, ctx):
        """ update cc table """
        try:
            cc_log = await self.init_cc_table()
            log_url = await hastebin.post(cc_log)

            embed = discord.Embed(title=" ", description=f"CC Table Update : {log_url}", color=0xe5e500)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

            await self.mod_channel.send(embed=embed)
        except Exception as e:
            print(f"error in ccupdate {e}")
            await self.mod_channel.send("initcctable failed")

    # events -----------
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if self.is_cc(member.id):
            usr = self.get_user()
            usr = await self.cc_user(member.id, username=str(member), days=usr['penaltyDays']+7, is_perm=False)
            embed = discord.Embed(title=" ", description=f"[REJOINED SERVER] User <@{member.id}> successfully got CC'd."
                                                         f" (Banned for `{usr['penaltyDays']}` days)", color=0x75df00)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await self.mod_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.channel == self.counting_channel:
            embed = self.get_message_event_embed(event_title="Delete Notification", message=message)
            await self.mod_channel.send(embed=embed)

            if self.auto_cc_mode:
                usr = await self.cc_user(message.author.id, username=str(message.author))
                await self.mod_channel.send(embed=self.get_cc_embed(message.author, usr['penaltyDays']))

    @commands.Cog.listener()
    async def on_message_edit(self, old_msg, new_msg):
        if old_msg.channel == self.counting_channel:
            embed = self.get_message_event_embed(event_title="Edit Notification", message=old_msg, new_message=new_msg)
            await self.mod_channel.send(embed=embed)

            if self.auto_cc_mode:
                usr = await self.cc_user(old_msg.author.id, username=str(old_msg.author))
                await self.mod_channel.send(embed=self.get_cc_embed(old_msg.author, usr['penaltyDays']))


def setup(bot):
    bot.add_cog(Counting(bot))
