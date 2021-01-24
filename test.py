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
    
    #adds meet link corresponding to a course
    @staticmethod
    async def add_link(ctx, *args):
        query = {"subject": args[0], "section": args[1]}
        coll.update_one(query, {"$push": {"link": args[2]}})
        await ctx.send(f'Link added (if course exists) to {args[0]} {args[1]}')

    #retrieving link(s) of a subject from the db
    @staticmethod
    async def get_link(ctx, *args):
        query = {"subject": args[0], "section": args[1]}
        myquery = coll.find_one(query)
        if myquery is not None:
            await ctx.send('\n'.join(myquery['link']))
        else:
            await ctx.send('No such record.')
    
    @staticmethod
    async def deregister(ctx, *args):
        coll.delete_one({"subject": args[0], "section": args[1]})
        await ctx.send('Course deregistered.')

@bot.event
async def on_ready():
    print('Bot Ready')
  

@bot.command()
async def ping(ctx):
    await ctx.send(f'I am just {round(bot.latency * 1000)}ms away from you :cupid:.')

# Registers the course in the database
@bot.command(aliases=['register', 'add'])
async def register_course(ctx, *args):
    if len(args) != 4:
        await ctx.send('Usage: Course, time, section, link')
    else:
        Schedule(args[0], args[1], args[2], args[3])
        await ctx.send(f'{args[0]} registered.')

@bot.command()
async def deregister(ctx, *args):
    await Schedule.deregister(ctx, *args)

@bot.command(aliases = ['add_link'])
async def addlink(ctx, *args):
    await Schedule.add_link(ctx, *args)

@bot.command()
async def getlink(ctx, *args):
    await Schedule.get_link(ctx, *args)

bot.run(BOT_TOKEN)