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

MONGO_URL = os.environ['MONGO_URL']
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

class Schedule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def argParser(*args):
        if (len(args) > 5):
            raise Exception("Too many arguments")
        keys = [1, 2, 3, 4, 5]
        argDict = {key: None for key in keys}
        for i in range(len(args)):
            argDict[Schedule.ParseHelper(args[i])] = args[i]            
        return tuple([argDict[i] for i in keys if argDict[i] is not None])
            
    @staticmethod    
    def ParseHelper(arg):
        if validators.url(arg): #link
            return 5
        if arg.isdigit(): #time
            return 4
        if re.match(r'[mtw(th)fsMTW(TH)FS(Th)]+$', arg): #day
            return 3                                                           
        if re.match(r'[TtPpLl]\d+$', arg): #section
            return 2
        if re.match(r'[a-zA-Z0-9-]+$', arg):  #course
            return 1
        raise Exception("Error in arguments!")

    @commands.command(aliases=['register', 'add'], brief='Add a course to the DB')
    @staticmethod
    def register_course(ctx, *arguments):
        if len(arguments) != 5:
            await ctx.send('Usage: Course, section, day, time, link')
        else:
            try:
                args = Schedule.argParser(arguments) 
                course = courses.find_one_and_update({"name": args[0]}, {"$set": {"name": args[0]}}, upsert= True, return_document = pymongo.ReturnDocument.AFTER)
                sched = schedules.find_one({"course": course['_id'], "section": args[1]})
                if sched is None:
                    schedules.insert_one({"course": course['_id'], "day": args[2].upper(), "time": args[3], "section": args[1], "link": [args[4]]})
                else:
                    await ctx.send("Already registered! Use add_link to add a link to the record.")   
            
            except Exception as e:
                await ctx.send(f'{e}')

    @staticmethod
    def get_course(name):
        return courses.find_one({"name": name})

    @staticmethod
    def get_schedule(name, section='N/A'):
        if section == 'N/A':
            return schedules.find({"course": self.get_course(name)['_id']})
        return schedules.find_one({"course": self.get_course(name)['_id'], "section": section})   
    #adds meet link corresponding to a course

    def add_link(self, *args):
        if validators.url(args[2]):
            course = courses.find_one_and_update({"name": args[0]}, {"$set": {"name": args[0]}}, upsert= True, return_document = pymongo.ReturnDocument.AFTER)
            sched = schedules.find_one({"course": course['_id'], "section": args[1]})
            # adds the incoming link if the link is not already present
            if args[2] in sched['link']:
                return 2
            else:
                schedules.update_one({"course": course['_id'], "section": args[1]}, {"$push": {"link": args[2]}})
                return 1
        return 0

    #retrieves link(s) of a subject from the db
    @staticmethod
    def get_link(self, name, section='N/A'):            
        sched = self.get_schedule(name, section)
        if isinstance(sched, pymongo.cursor.Cursor):
            links = []
            for doc in sched:
                links.extend(doc['link'])
            return links
        else:
            return sched['link']
    
    @commands.command(brief='Deregisters all sections of a course if no section is given, otherwise deregisters the given section.')
    @staticmethod
    def deregister(ctx, *args):
        if len(args) == 2:
            status = schedules.delete_many({"course": Schedule.get_course(args[0])['_id'], "section":args[1]})
            if schedules.find_one({"course": Schedule.get_course(args[0])['_id']}) is None:
                courses.delete_one({"name": args[0]})
        elif len(args) == 1:
            status = schedules.delete_many({"course":  Schedule.get_course(args[0])['_id']})
            courses.delete_one({"name": args[0]})
        else:
            return -1
        if status.deleted_count > 0:
            await ctx.message.add_reaction('\U0001F44C')
        elif status == 0:
            await ctx.send("Course does not exist.")
        else:
            await ctx.send("C'mon, that's not even valid syntax")

    def remove_link(self, *args):
        sched = self.get_schedule(args[0], args[1])
        if args[2] in sched['link']:
            sched['link'].remove(args[2])
            schedules.update_one(sched, {"$set": {"link": sched['link']}})  #Probably wrong. Link is being set to old link and not deleted. @ingenium-cipher fix this. 
            return 1
        return 0
    
    async def remove_all(self):
        courses.drop()
        schedules.drop()

def setup(bot):
    bot.add_cog(Schedule(bot))
print("hi")
