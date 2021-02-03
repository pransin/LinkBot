import discord
from discord.ext import commands
import pymongo
from datetime import datetime
import schedule
import validators
import json
import os
import re
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



@bot.event
async def on_ready():
    print(f'Bot Ready')
  

@bot.command(brief='The name says it all')
async def ping(ctx):
    await ctx.send(f'I am just {round(bot.latency * 1000)}ms away from you :cupid:.')

# Registers the course in the database
# @bot.command()
# async def register_course(ctx, *args):
#     if len(args) != 5:
#         await ctx.send('Usage: Course, day, time, section, link')
#     else:
#         try:
#             Schedule(args[0], args[1], args[2], args[3], args[4])
#             await ctx.message.add_reaction('\U0001F44C')
#         except Exception as e:
#             await ctx.send(f'{e}')

@bot.command(brief='Deregisters all sections of a course if no section is given, otherwise deregisters the given section.')
async def deregister(ctx, *args):
    status = Schedule.deregister(*args)
#ye method se karna

@bot.command(aliases = ['add_link'], brief='Adds link to a course. Usage: <Course> <Section>')
async def addlink(ctx, *args):
    status = Schedule.add_link(*args)
    if status == 1:
        await ctx.message.add_reaction('\U0001F44C')
    elif status == 2:
        await ctx.send(f'Link already exists!')
    elif status == 0:
        await ctx.send('Invalid URL Format.')

@bot.command(brief='Retrieves link(s) of a course', description='Usage: $getlink [Course Name] [Section]=optional.\n Sends links of all sections of a course if section is omitted.')
async def getlink(ctx, *args):
    try:
        links = Schedule.get_link(*args)
        nospam = '>\n<'
        print(links)
        await ctx.send(f"<{nospam.join(links)}>")
    except:
        await ctx.send("You sure that course/link has been added?")
 
@bot.command(brief='Removes given link *****')
async def remove_link(ctx, *args):
    status = Schedule.remove_link(args[2])
    if status:
        await ctx.send(f"Link removed from {args[0]} {args[1]}")
    else:
        await ctx.send("Link not present.")

@bot.command(brief='Shows all registered courses')
async def show_all(ctx):
    for x in courses.find():  
        await ctx.send(x['name'] + '\n')
# Removes all courses and (maybe) all related collections
@bot.command(brief='Deregisters all courses. Use with caution!')
async def clear_database(ctx):
    await Schedule.remove_all()
    await ctx.send('Database cleared.')


bot.load_extension(f'cogs.linksender')
bot.run(BOT_TOKEN)