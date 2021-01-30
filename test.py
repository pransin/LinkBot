import discord
from discord.ext import commands
from keyconfig import *
import pymongo
from datetime import datetime
import schedule
import validators

bot = commands.Bot(command_prefix = '$')
myclient = pymongo.MongoClient(MONGO_URL)
db = myclient["linkbot"]

collist = db.list_collection_names()
collections = ["schedules", "users", "courses"]

for collect in collections:
    if collect not in collist:
        db.create_collection(collect)

schedules = db["schedules"]
users = db["users"]
courses = db["courses"]

class Schedule():

    def __init__(self, subject, day, time, section, link):
        if validators.url(link):
            course = courses.find_one_and_update({"name": subject}, {"$set": {"name": subject}}, upsert= True, return_document = pymongo.ReturnDocument.AFTER)
            print(course)
            sched = schedules.find_one({"subject": course['_id'], "section": section})
            if sched is None:
                schedules.insert_one({"subject": course['_id'], "day": day, "time": time, "section": section, "link": [link]})
            else:
                schedules.update_one({"query": sched, "$push": {"link": link}})
        else:
            raise Exception('Invalid URL Format.')
    
    #adds meet link corresponding to a course
    @staticmethod
    async def add_link(ctx, *args):
        if validators.url(args[2]):
            course = courses.find_one_and_update({"name": subject}, {"$set": {"name": subject}}, upsert= True, return_document = pymongo.ReturnDocument.AFTER)
            query = {"subject": course['_id'], "section": args[1]}
            schedules.update_one(query, {"$push": {"link": args[2]}})
            ctx.send(f'Link added to {args[0]} {args[1]}')
        else:
            ctx.send(f'Incorrect URL Format.')

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
    if len(args) != 5:
        await ctx.send('Usage: Course, day, time, section, link')
    else:
        try:
            Schedule(args[0], args[1], args[2], args[3], args[4])
            await ctx.send(f'{args[0]} registered.')
        except Exception as e:
            await ctx.send(f'{e}')

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