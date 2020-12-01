# 2020 Emir Erbasan (humanova)
# MIT License, see LICENSE for more details

import discord
from utils import confparser, default
from discord.ext import commands

class Info(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.config = confparser.get("config.json")

    @commands.command(aliases=['developer'])
    async def dev(self, ctx):
        """ Sends developer info """
        embed = discord.Embed(title=" ", color=0x75df00)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name="Developer", value=f"<@{self.config.owners[0]}>", inline=False)
        embed.add_field(name="GitHub", value="https://github.com/humanova", inline=False)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Info(bot))