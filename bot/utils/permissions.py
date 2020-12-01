import discord
from . import confparser
from discord.ext import commands

config = confparser.get("config.json")
owners = config.owners
cm_role_id = config.cm_role_id


def is_owner(ctx):
    return ctx.author.id in owners

def is_count_mod(ctx):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        return True if is_owner(ctx) else False
    else:
        return True if int(cm_role_id) in [r.id for r in ctx.author.roles] else False

async def check_permissions(ctx, perms, *, check=all):
    if ctx.author.id in owners:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())

def has_permissions(*, check=all, **perms):
    async def pred(ctx):
        return await check_permissions(ctx, perms, check=check)
    return commands.check(pred)

def can_send(ctx):
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.permissions_for(ctx.guild.me).send_messages

def can_embed(ctx):
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.permissions_for(ctx.guild.me).embed_links

def can_react(ctx):
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.permissions_for(ctx.guild.me).add_reactions