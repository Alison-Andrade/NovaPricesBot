import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv('.env')
client = commands.Bot(command_prefix='$')
client.remove_command('help')

TOKEN = os.getenv('TOKEN')

# Load cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


# Commands
@client.command()
async def help(ctx):
    embed = discord.Embed(colour=discord.Colour.orange())
    embed.set_author(name='Help')
    embed.add_field(name='ping', value='Returns Pong', inline=False)

    await ctx.send(embed=embed)

client.run(TOKEN)
