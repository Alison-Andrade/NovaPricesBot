import discord
from discord.ext import commands
import os

OWNER = os.getenv('OWNER')


class OwnerCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'OwnerCommands ready!')

    ## Checks ##
    async def is_owner(self):
        return self.author.id == int(OWNER)

    @commands.command()
    @commands.check(is_owner)
    async def servers(self, ctx):
        activeservers = self.client.guilds
        embed = discord.Embed(title='Servers')
        for guild in activeservers:
            embed.add_field(name=f'> {guild.name}',
                            value='\n\u200b', inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(is_owner)
    async def reload(self, ctx):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                self.client.unload_extension(f'cogs.{filename[:-3]}')
                self.client.load_extension(f'cogs.{filename[:-3]}')
        await ctx.send('All extentions reloaded')


def setup(client):
    client.add_cog(OwnerCommands(client))
