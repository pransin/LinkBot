import discord
from discord.ext import commands
from keyconfig import *
import pymongo
from datetime import datetime

bot = commands.Bot(command_prefix = '$')
myclient = pymongo.MongoClient(MONGO_URL)
db = myclient["linkbot"]
coll = db["bot"]
class Schedule():

    def __init__(self, subject, time, section, link):
        
        schedule_dict = {"subject": subject, "time": time, "section": section, "link": [link]}
        coll.insert_one(schedule_dict)
    
    @staticmethod
    async def add_link(ctx, *args):
        query = {"subject": args[0], "section": args[1]}
        coll.update_one(query, {"$push": {"link": args[2]}})
        ctx.send(f'Link added to {args[0]} {args[1]}')

@bot.event
async def on_ready():
    print('Bot Ready')
  

@bot.command()
async def ping(ctx):
    await ctx.send(f'I am just {round(bot.latency * 1000)}ms away from you :cupid:.')

@bot.command(aliases=['register', 'add'])
async def register_course(ctx, *args):
    if len(args) != 4:
        await ctx.send('Usage: Course, time, section, link')
    else:
        Schedule(args[0], args[1], args[2], args[3])
        await ctx.send(f'{args[0]} registered.')

@bot.command()
async def add_link(ctx, *args):
    await Schedule.add_link(ctx, *args)

bot.run(BOT_TOKEN)