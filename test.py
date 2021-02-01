import discord
from discord.ext import commands
import pymongo
from datetime import datetime
import schedule
import validators
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
is_prod = os.environ['IS_HEROKU']

MONGO_URL = os.environ['MONGO_URL']
if is_prod:
    BOT_TOKEN = os.environ['BOT_TOKEN']
    bot = commands.Bot(command_prefix = '$')
else:
    BOT_TOKEN = os.environ['TEST_TOKEN']
    bot = commands.Bot(command_prefix = '~')

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

    @staticmethod
    def get_course(name):
        return courses.find_one({"name": name})

    @staticmethod
    def get_schedule(name, section):
        return schedules.find_one({"course": Schedule.get_course(name)['_id'], "section": section})

    def __init__(self, subject, day, time, section, link):
        if validators.url(link):
            course = courses.find_one_and_update({"name": subject}, {"$set": {"name": subject}}, upsert= True, return_document = pymongo.ReturnDocument.AFTER)
            sched = schedules.find_one({"course": course['_id'], "section": section})
            if sched is None:
                schedules.insert_one({"course": course['_id'], "day": day.lower(), "time": time, "section": section, "link": [link]})
            else:
                if link in sched['link']:
                    raise Exception("Link already added!")
                else:
                    schedules.update_one({"query": sched}, {"$push": {"link": link}})
        else:
            raise Exception("Invalid URL format.")
    
    #adds meet link corresponding to a course
    @staticmethod
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

    #retrieves link(s) of a subject from the db
    @staticmethod
    def get_link(*args):
        sched = Schedule.get_schedule(args[0], args[1])
        if sched:
            return sched['link'], 1
        return None, 0
    
    @staticmethod
    def deregister(*args):
        if Schedule.get_course(args[0]):
            courses.delete_one({"name": args[0]})
            return 1
        else:
            return 0

    @staticmethod
    def remove_link(*args):
        sched = Schedule.get_schedule(args[0], args[1])
        if args[2] in sched['link']:
            sched['link'].remove(args[2])
            schedules.update_one(sched, {"$set": {"link": sched['link']}})   
            return 1
        return 0


    @staticmethod
    async def remove_all():
        courses.drop()
        schedules.drop()

@bot.event
async def on_ready():
    print('Bot Ready')
  

@bot.command(brief='The name says it all')
async def ping(ctx):
    await ctx.send(f'I am just {round(bot.latency * 1000)}ms away from you :cupid:.')

# Registers the course in the database
@bot.command(aliases=['register', 'add'], brief='Add a course to the DB')
async def register_course(ctx, *args):
    if len(args) != 5:
        await ctx.send('Usage: Course, day, time, section, link')
    else:
        try:
            Schedule(args[0], args[1], args[2], args[3], args[4])
            await ctx.message.add_reaction('\U0001F44C')
        except Exception as e:
            await ctx.send(f'{e}')

@bot.command(brief='Supposedly deregisters all sections of a course')
async def deregister(ctx, *args):
    status = Schedule.deregister(*args)
    if status:
        await ctx.message.add_reaction('\U0001F44C')
    else:
        await ctx.send("Course does not exist.")


@bot.command(aliases = ['add_link'], brief='Adds link to a course. Usage: <Course> <Section>')
async def addlink(ctx, *args):
    status = Schedule.add_link(*args)
    if status == 1:
        await ctx.message.add_reaction('\U0001F44C')
    elif status == 2:
        await ctx.send(f'Link already exists!')
    elif status == 0:
        await ctx.send('Invalid URL Format.')

@bot.command(brief='Retrieves link to a course. Usage: <Course> <Section>')
async def getlink(ctx, *args):
    links, status = Schedule.get_link(*args)
    if status:
        if len(links):
            temp_links = []
            for link in links:
                temp_links.append("<" + link + ">")
            await ctx.send('\n'.join(temp_links))
        else:
            await ctx.send("No links added :pensive:")
    else:
        await ctx.send("No such record.")

@bot.command(brief='Removes given link *****')
async def remove_link(ctx, *args):
    status = Schedule.remove_link(args[2])
    if status:
        await ctx.send(f"Link removed from {args[0]} {args[1]}")
    else:
        await ctx.send("Link not present.")


# Removes all courses and (maybe) all related collections
@bot.command(brief='Deregisters all courses. Use with caution!')
async def clear_database(ctx):
    await Schedule.remove_all()
    await ctx.send('Database cleared.')

bot.run(BOT_TOKEN)
