# 2019 Emir Erbasan (humanova)

# bot for r/CubeWorld Server
# discord.gg/cubeworld

import asyncio
import os
import datetime

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.utils import get

import hastebin

from cwdb import cwdb
db = cwdb()
import env_set
env_set._set()

server_id = '171682573662027776'
cm_channel_id = '622529718612262933'
c_channel_id = '493837739616108566'
cm_role_id = '507794225610358797'
cc_role_id = '505783639380852748'

auto_cc_mode = False
################################

Client = discord.Client()
client = commands.Bot(command_prefix="!")


def isCountMod(user):
    if cm_role_id in [y.id for y in user.roles]:
        return True
    return False


async def checkCC():

    server = client.get_server(server_id)
    cc_role = discord.utils.get(server.roles, id=cc_role_id)
    while not client.is_closed:
        uncc_list = db.checkUncc()
        if not len(uncc_list) == 0:
            for userid in uncc_list:

                user = discord.utils.get(server.members, id = userid)
                if not user == None:
                    await client.remove_roles(user, cc_role)

                    embed = discord.Embed(title=" ", description=f"User <@{user.id}> got UNCC'd.", color=0x75df00)
                    embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
                    await client.send_message(discord.Object(id=cm_channel_id), embed=embed)

                    # send_message API limit sleep (in case of uncc'ing more than 30 people)
                    await asyncio.sleep(1)

        # sleep for 1 hour
        await asyncio.sleep(3600)


async def updateCCDatabase():

    server = client.get_server(server_id)
    cc_members = []

    for member in server.members:
        if cc_role_id in [y.id for y in member.roles]:
            cc_members.append(member)
    
    cc_members = db.updateCCTable(cc_members)

    cc_log = f"{len(cc_members)} users are updated.\n\n"
    for mem in cc_members:
        cc_log += f"{mem.id}, {mem.name}#{mem.discriminator}\n"

    return cc_log


async def ccMember(member, is_perm=False, days=None):

    server = client.get_server(server_id)
    role = discord.utils.get(server.roles, id=cc_role_id)

    try:
        await client.add_roles(member, role)
        db_user = None
        if not days:
            db_user = db.ccUser(member.id, member.name, is_perm)
        else:
            db_user = db.ccUserDays(member.id, member.name, is_perm, days=days)

        penalty_days = db_user['penaltyDays']

        ban_description = str()
        if is_perm:
            ban_description = f"User <@{member.id}> successfully got CC'd. (perm ban)"
        else:
            ban_description = f"User <@{member.id}> successfully got CC'd. (Banned for `{penalty_days} days`)"

        embed = discord.Embed(title=" ", description=ban_description, color=0x75df00)
        embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        await client.send_message(discord.Object(id=cm_channel_id), embed=embed)

    except Exception as e:
        print(e)
        embed = discord.Embed(title=" ", description=f"Error while CC'ing <@{member.id}>", color=0xFF0000)
        embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        await client.send_message(discord.Object(id=cm_channel_id), embed=embed)


@client.event
async def on_ready():

    print("Logged in as %s." % (client.user.name))
    await checkCC()


@client.event
async def on_message(message):

    if not message.author.bot:
        
        #!tweet -- mention members with "Tweets" role
        if message.content == "!tweet" and message.author.server_permissions.manage_roles:
            
            role = get(message.server.roles, name="Tweets")
            # set tweets role mentionable then mention ppl
            try:
                await client.edit_role(server=message.server, role=role, mentionable=True)
                await client.send_message(message.channel, f"<@&{role.id}>")
                await client.edit_role(server=message.server, role=role, mentionable=False)
            except Exception as e:
                print("error while mentioning tweet role")
                print(e)
            
            await client.delete_message(message)

        #!cc @mention , !cc userid -- give "Can't Count" role to member
        if (message.content.startswith("!cc ") or message.content.startswith("!ccperm ") or message.content.startswith("!ccdays ")) and message.channel.id == cm_channel_id:

            msg = message.content.split(" ")
            ccdays = None
            is_perm = False
            if msg[0] == "!ccperm":
                is_perm = True
            if msg[0] == "!ccdays":
                ccdays = int(msg[2])
            
            # get user from msg mentions
            if not len(message.mentions) == 0:
                user = message.mentions[0]
                await ccMember(user, is_perm=is_perm, day=ccdays)
                
            # get user from user_id
            elif len(msg) >= 2:
                try:
                    user_id = msg[1]
                    user = discord.utils.get(message.server.members, id=user_id)
                    await ccMember(user, is_perm=is_perm, days=ccdays)

                except:
                    embed = discord.Embed(title=" ", description=f"Couldn't find any user attached to given user_id : `{user_id}`", color=0xe5e500)
                    embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
                    await client.send_message(message.channel, embed=embed)

            # wrong usage of !cc command
            else:
                print(f"Command '{message.content}' has more than 1 argument.")
                # no need to notify the channel ?..
        
        #!cclist -- upload cc'd users table from database
        if message.content == "!cclist" and message.channel.id == cm_channel_id:
            
            table = db.getCCTable()
            table_url = await hastebin.post(table)

            embed = discord.Embed(title=" ", description=f"Current CC Table : {table_url}", color=0xe5e500)
            embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)

            await client.send_message(message.channel, embed=embed)

        if message.content == "!ccupdate" and message.channel.id == cm_channel_id:

            cc_log = await updateCCDatabase()
            log_url = await hastebin.post(cc_log)
            
            embed = discord.Embed(title=" ", description=f"CC Table Update : {log_url}", color=0xe5e500)
            embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)

            await client.send_message(message.channel, embed=embed)
        
        #!ccauto 1/0 -- toggle auto-cc mode on/off
        if message.content.startswith("!ccauto") and message.channel.id == cm_channel_id:

            global auto_cc_mode
            msg = message.content.split(" ")

            if msg[1] == '1' or msg[1].upper() == 'TRUE':
                auto_cc_mode = True

            elif msg[1] == '0' or msg[1].upper() == 'FALSE':
                auto_cc_mode = False

            embed = discord.Embed(title=" ", description=f"Auto-CC is set to : {auto_cc_mode}", color=0xe5e500)
            embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)

            await client.send_message(message.channel, embed=embed)

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

        # !serverinfo -- show server info
        if message.content == "!serverinfo":
            
            srv = message.server
            mem_count = srv.member_count
            bot_count = 0

            for mem in srv.members:
                if mem.bot:
                    bot_count += 1

            human_count = mem_count - bot_count
            t_channel_count, v_channel_count = 0, 0

            for chan in srv.channels:
                if chan.type == discord.ChannelType.text:
                    t_channel_count += 1
                else:
                    v_channel_count += 1
            
            embed = discord.Embed(title=' ', color=0x0DCFA0)
            embed.set_author(name=srv.name, icon_url=srv.icon_url)
            embed.add_field(name="Owner", value=f"{str(srv.owner)}", inline=True)
            embed.add_field(name="Region", value=srv.region, inline=True)
            embed.add_field(name="Text Channels",value=str(t_channel_count), inline=True)
            embed.add_field(name="Voice Channels",value=str(v_channel_count), inline=True)
            embed.add_field(name="Members", value=mem_count, inline=True)
            embed.add_field(name="Roles",value=str(len(srv.roles)), inline=True)
            embed.add_field(name="Humans",value=human_count, inline=True)
            embed.add_field(name="Bots",value=bot_count, inline=True)
        
            embed.set_footer(text=f"ID: {message.server.id} | Created at•18/04/2016")
            await client.send_message(message.channel,embed=embed)

    # mod specific commands
    if not message.server == None and not message.author.bot:
        try:
            if 'Discord Server Mods' in [y.name for y in message.author.roles]:

                if message.content == "!cmds":
                    embed = discord.Embed(title="Commands", color=0xe5e500)
                    embed.add_field(name="cc,ccperm", value="`!cc @user/userid` : give Can't Count role to user")
                    embed.add_field(name="cclist", value="`!cclist` : sends a list of CC'd users")
                    embed.add_field(name="ccauto", value="`!ccauto true/false` : toggle auto-cc mode on/off")
                    embed.add_field(name="croom", value="`!croom room-name @mentions` : create a temp room and add mentioned")
                    embed.add_field(name="droom", value="`!droom` : delete current temp room")
                    embed.add_field(name="addroom", value="`!addroom @mentioned` : add mentioned user to current room")
                    embed.add_field(name="removeroom", value="`!removeroom @mentioned` : remove mentioned user from current room")
                    embed.add_field(name="serverinfo", value="`!members` : sends server info")
                    embed.add_field(name="tweet", value="`!tweet` : mention Tweets role")
                    
                    embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
                    await client.send_message(message.channel, embed=embed)

        except Exception as e:
            print(e)
    

@client.event
async def on_member_join(member):

    if member.server.id == server_id and not member.bot:

        if db.isCC(member.id):

            await ccMember(member, is_perm=False)
            cc_time = db.getCCTimeLeft(member.id)

            embed = discord.Embed(title=" ", description=f"[REJOINED SERVER] User <@{member.id}> successfully got CC'd. (Banned for `{cc_time}` days)", color=0x75df00)
            embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
            await client.send_message(discord.Object(id=cm_channel_id), embed=embed)


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

            if auto_cc_mode:
                await ccMember(message.author)


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

            if auto_cc_mode:
                await ccMember(message.author)

token = os.environ['BOT_TOKEN']
client.run(token)
