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
            sched = schedules.find_one({"course": course['_id'], "section": section})
            if sched is None:
                schedules.insert_one({"course": course['_id'], "day": day.lower(), "time": time, "section": section, "link": [link]})
                return 1
            else:
                if link in sched['link']:
                    return 2
                else:
                    schedules.update_one({"query": sched, "$push": {"link": link}})
        return 0
    
    #adds meet link corresponding to a course
    @staticmethod
<<<<<<< HEAD
    def add_link(*args):
        if validators.url(args[2]):
            course = courses.find_one_and_update({"name": args[0]}, {"$set": {"name": args[0]}}, upsert= True, return_document = pymongo.ReturnDocument.AFTER)
            sched = schedules.find_one({"course": course['_id'], "section": args[1]})
            if args[2] in sched['link']:
                return 2
            else:
                schedules.update_one({"course": course['_id'], "section": args[1]}, {"$push": {"link": args[2]}})
                return 1
        return 0

    #retrieving link(s) of a course from the db
=======
    async def add_link(ctx, *args):
        query = {"subject": args[0], "section": args[1]}
        print(coll.update_one(query, {"$push": {"link": args[2]}}))
        await ctx.send(f'Link added (if course exists) to {args[0]} {args[1]}')

    #retrieves link(s) of a subject from the db
>>>>>>> remove all method added
    @staticmethod
    def get_link(*args):
        sched = get_schedule(args[0], args[1])
        if sched:
            return sched['link'], 1
        return None, 0
    
    @staticmethod
    def deregister(*args):
        if get_course(args[0]):
            course = courses.delete_one({"name": args[0]})
            return 1
        else:
            return 0

    @staticmethod
    def remove_link(*args):
        sched = get_schedule(args[0], args[1])
        if args[2] in sched['link']:
            sched['link'].remove(args[2])
            schedules.update_one(sched, {"$set": {"link": sched['link']}})   
            return 1
        return 0

    @staticmethod
    def get_course(name):
        return courses.find_one({"name": name})

    @staticmethod
    def get_schedule(name, section):
        return schedules.find_one({"name": get_course()['_id'], "section": section})


    @staticmethod
    async def remove_all(ctx):
        coll.drop()
        await ctx.send('Database cleared.')
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
        status = Schedule(args[0], args[1], args[2], args[3], args[4])
        if status == 1:
            await ctx.send(f'{args[0]} {args[1]} registered.')
        elif status == 2:
            await ctx.send(f'Link already exists!')
        elif status == 0:
            await ctx.send('Invalid URL Format.')

@bot.command()
async def deregister(ctx, *args):
    status = Schedule.deregister(*args)
    if status:
        await ctx.send('Course deregistered.')
    else:
        await ctx.send("Course does not exist.")


@bot.command(aliases = ['add_link'])
async def addlink(ctx, *args):
    status = Schedule.add_link(*args)
    if status == 1:
        await ctx.send(f'Link added to {args[0]} {args[1]}.')
    elif status == 2:
        await ctx.send(f'Link already exists!')
    elif status == 0:
        await ctx.send('Invalid URL Format.')

@bot.command()
async def getlink(ctx, *args):
    links, status = Schedule.get_link(*args)
    if status:
        if len(links):
            await ctx.send('\n'.join(links))
        else:
            await ctx.send("No links added :pensive:")
    else:
        await ctx.send("No such record.")

@bot.command()
async def remove_link(ctx, *args):
    status = Schedule.remove_link(args[2])
    if status:
        await ctx.send(f"Link removed from {args[0]} {args[1]}")
    else:
        await ctx.send("Link not present.")



@bot.command()
async def remove_all(ctx):
    await Schedule.remove_all(ctx)

bot.run(BOT_TOKEN)