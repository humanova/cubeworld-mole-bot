# 2019 Emir Erbasan (humanova)

# Counting channel moderation bot for r/CubeWorld Server
# discord.gg/cubeworld

import asyncio
import os
import datetime

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.utils import get

import env_set
env_set._set()

import mole_word

cm_channel_id = '622529718612262933'
c_channel_id = '493837739616108566'
mole_advice_keywords = ['mole', 'advice', ':bruh:']

################################

Client = discord.Client()
client = commands.Bot(command_prefix="!")

def isCountMod(user):
    if 'Count Mod' in [y.name for y in user.roles]:
        return True
    return False


@client.event
async def on_ready():
    print("Logged in as %s." % (client.user.name))


@client.event
async def on_message(message):

    if not message.author.bot:
        
        # CC command
        if message.content.startswith("!cc ") and message.channel.id == cm_channel_id:

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


        # !croom name @mentions -- create room
        if message.content.startswith("!croom ") and message.author.server_permissions.manage_channels:

            msg = message.content.split(" ")
            if len(message.mentions) > 0:
                chan_name = f"temp-{msg[1]}"
                
                chan_role = await client.create_role(message.server, name=chan_name)
                for member in message.mentions:
                    await client.add_roles(member, chan_role)
                
                bot_role = get(message.server.roles, name="CountMasterMole")
                mod_role = get(message.server.roles, name="Discord Server Mods")
                def_role = get(message.server.roles, name="@everyone")
                

                overwrites = [
                    (def_role, discord.PermissionOverwrite(read_messages=False)),
                    (bot_role, discord.PermissionOverwrite(read_messages=True, send_messages=True)),
                    (mod_role, discord.PermissionOverwrite(read_messages=True, send_messages=True)),
                    (chan_role, discord.PermissionOverwrite(read_messages=True, send_messages=True))
                ]

                channel = None
                try:
                    channel = await client.create_channel(message.server, chan_name, overwrites[0], overwrites[1], overwrites[2], overwrites[3])
                except Exception as e:
                    print(f"error while creating channel named : {chan_name}")
                    print(e)

                if not channel == None:
                    embed = discord.Embed(title="Temporary Room", color=0x75df00)
                    embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
                    embed.add_field(name="Creator", value=f"<@{message.author.id}>", inline=False)
                    embed.add_field(name="Room Name", value=chan_name, inline=True)
                    embed.add_field(name="Command", value=message.content, inline=False)

                    await client.send_message(channel, embed=embed)


        # !droom -- delete room
        if message.content == "!droom" and message.author.server_permissions.manage_channels:
            if message.channel.name.startswith("temp-"):
                await client.delete_role(message.server, get(message.server.roles, name=message.channel.name))
                await client.delete_channel(message.channel)
        


        # !addroom @mentions -- add mentioned members to room
        if message.content.startswith("!addroom ") and message.author.server_permissions.manage_channels:
            msg = message.content.split(" ")

            if len(message.mentions) > 0:
                role_name = message.channel.name
                role = get(message.server.roles, name=role_name)

                for member in message.mentions:
                    await client.add_roles(member, role)


        # !removeroom @mentions -- remove mentioned members from room
        if message.content.startswith("!removeroom ") and message.author.server_permissions.manage_channels:
            msg = message.content.split(" ")

            if len(message.mentions) > 0:
                role_name = message.channel.name
                role = get(message.server.roles, name=role_name)

                for member in message.mentions:
                    await client.remove_roles(member, role)


    # mod specific commands
    if not message.server == None and not message.author.bot:
        try:
            if 'Discord Server Mods' in [y.name for y in message.author.roles]:

                if message.content == "!cmds":
                    embed = discord.Embed(title="Commands", color=0xe5e500)
                    embed.add_field(name="cc", value="`!cc @user/userid` : give Can't Count role to user")
                    embed.add_field(name="croom", value="`!croom room-name @mentions` : create a temp room and add mentioned")
                    embed.add_field(name="droom", value="`!droom` : delete current temp room")
                    embed.add_field(name="addroom", value="`!addroom @mentioned` : add mentioned user to current room")
                    embed.add_field(name="removeroom", value="`!removeroom @mentioned` : remove mentioned user from current room")
                    embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
                    await client.send_message(message.channel, embed=embed)

                # random mole advice
                if all(keyword in message.content for keyword in mole_advice_keywords):
                    await client.send_message(message.channel, mole_word.GetRandomMoleWords())

        except Exception as e:
            print(e)
    

@client.event
async def on_message_delete(message):

    if not message.author.bot and not message.server == None:

        # notify deleted messages in #counting
        if message.channel.id == c_channel_id:

            embed = discord.Embed(title="Delete Notification", color=0xe5e500)
            embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
            embed.add_field(name="Author", value=f"<@{message.author.id}>", inline=False)
            embed.add_field(name="Message", value=message.content, inline=False)
            embed.set_footer(text=f"Is Count Mod : {str(isCountMod(message.author))}")

            await client.send_message(discord.Object(id=cm_channel_id), embed=embed)


@client.event
async def on_message_edit(old_message, message):

    if not message.author.bot and not message.server == None:

        # notify count mods in case of message edit in #counting
        if message.channel.id == c_channel_id:

            embed = discord.Embed(title="Edit Notification", color=0xe5e500)
            embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
            embed.add_field(name="Author", value=f"<@{message.author.id}>", inline=False)
            embed.add_field(name="Old Message", value=old_message.content, inline=False)
            embed.add_field(name="New Message", value=message.content, inline=False)
            embed.set_footer(text=f"Is Count Mod : {str(isCountMod(message.author))}")

            await client.send_message(discord.Object(id=cm_channel_id), embed=embed)

token = os.environ['BOT_TOKEN']
client.run(token)
