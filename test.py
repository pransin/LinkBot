import discord
from discord.ext import commands
from keyconfig import *
import pymongo
from datetime import datetime

bot = commands.Bot(command_prefix = '$')
myclient = pymongo.MongoClient(MONGO_URL)
db = myclient["linkbot"]
client = discord.Client()

class Schedule():

    def __init__(self, subject, time, section, link):
        coll = db["bot"]
        schedule_dict = {"subject": subject, "time": time, "section": section, "link": link}
        coll.insert_one(schedule_dict)

@bot.event
async def on_ready():
    print('Bot Ready')

@bot.command()
async def add(ctx, *args):
    print(args)
    Schedule(args[0], args[1], args[2], args[3])
    await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))

@bot.command()
async def ping(ctx):
    await ctx.send(f'I am just {round(bot.latency * 1000)}ms away from you :cupid:.')

@bot.command(aliases=['register'])
async def register_course(ctx, arg):
    await ctx.send(f'{arg} registered.')

bot.run(BOT_TOKEN)