# 2019 Emir Erbasan (humanova)

# Counting channel moderation bot for r/CubeWorld Server
# discord.gg/cubeworld

import asyncio
import os
import datetime

import discord
from discord.ext import commands
from discord.ext.commands import Bot

import env_set
env_set._set()

cm_channel_id = '622529718612262933'
c_channel_id = '493837739616108566'
mole_advice_keywords = ['mole', 'advice', ':bruh:']

################################

Client = discord.Client()
client = commands.Bot(command_prefix="!")


@client.event
async def on_ready():
    print("Logged in as %s." % (client.user.name))


@client.event
async def on_message(message):

    if message.channel.id == cm_channel_id:

        if message.content.startswith("!cc "):

            msg = message.content.split(" ")
            role = discord.utils.get(message.server.roles, name="Can't Count")

            # get user from msg mentions
            if not len(message.mentions) == 0:
                user = message.mentions[0]
                try:
                    await client.add_roles(user, role)

                    embed = discord.Embed(title=" ", description=f"User <@{user.id}> successfully got CC'd.", color=0x75df00)
                    embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
                    await client.send_message(message.channel, embed=embed)

                except Exception as e:
                    embed = discord.Embed(title=" ", description=f"Error while CC'ing <@{user.id}>\n```{e}```", color=0xFF0000)
                    embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
                    await client.send_message(message.channel, embed=embed)

            # get user from user_id
            elif len(msg) == 2:
                try:
                    user_id = msg[1]
                    user = discord.utils.get(message.server.members, id=user_id)
                    try:
                        await client.add_roles(user, role)

                        embed = discord.Embed(title=" ", description=f"User <@{user.id}> successfully got CC'd.", color=0x75df00)
                        embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
                        await client.send_message(message.channel, embed=embed)

                    except Exception as e:
                        embed = discord.Embed(title=" ", description=f"Error while CC'ing <@{user.id}>\n```{e}```", color=0xFF0000)
                        embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
                        await client.send_message(message.channel, embed=embed)
                except:
                    embed = discord.Embed(title=" ", description=f"Couldn't find any user attached to given user_id : `{user_id}`", color=0xe5e500)
                    embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
                    await client.send_message(message.channel, embed=embed)

            # wrong usage of !cc command
            else:
                print(f"Command '{message.content}' has more than 1 argument.")
                # no need to notify the channel ?..

    # mod specific commands
    if 'Discord Server Mods' in [y.name for y in message.author.roles]:

        # random mole advice
        if all(keyword in message.content for keyword in mole_advice_keywords):
            # placeholder quote for now
            await client.send_message(message.channel, "Life is just a stream of :bruh: moments.")


@client.event
async def on_message_delete(message):

    # notify deleted messages in #counting
    if message.channel.id == c_channel_id:

        is_count_mod = False
        if 'Count Mod' in [y.name for y in message.author.roles]:
            is_count_mod = True

        embed = discord.Embed(title="Delete Notification", color=0xe5e500)
        embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        embed.add_field(name="Author", value=f"<@{message.author.id}>", inline=False)
        embed.add_field(name="Message", value=message.content, inline=False)
        embed.set_footer(text=f"Is Count Mod : {str(is_count_mod)}")

        await client.send_message(discord.Object(id=cm_channel_id), embed=embed)

token = os.environ['BOT_TOKEN']
client.run(token)
