import discord
from discord.ext import commands
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
is_prod = os.environ['IS_HEROKU']

# MONGO_URL = os.environ['MONGO_URL']
if is_prod == 'True':
    BOT_TOKEN = os.environ['BOT_TOKEN']
    bot = commands.Bot(command_prefix = '$')
else:
    BOT_TOKEN = os.environ['TEST_TOKEN']
    bot = commands.Bot(command_prefix = '~')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    print(f'Bot Ready')
  

@bot.command(brief='The name says it all')
async def ping(ctx):
    await ctx.send(f'I am just {round(bot.latency * 1000)}ms away from you :cupid:.')

@bot.command(brief="Dev Command")
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command(brief="Dev Command")
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')

@bot.command(brief="Dev Command")
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')
    



bot.run(BOT_TOKEN)