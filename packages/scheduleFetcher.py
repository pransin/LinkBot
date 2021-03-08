import os
import pymongo
import re
import validators
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


 ####################### Convenience Functions  ########################   

def argParser(*args):

    if (len(args) > 5):
        raise Exception("Too many arguments")
    keys = [1, 2, 3, 4, 5]
    argDict = {key: None for key in keys}
    for i in range(len(args)):
        argDict[ParseHelper(args[i])] = args[i]            
    return tuple([argDict[i] for i in keys if argDict[i] is not None])
        
    
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
    raise Exception("Unexpected arguments!")

def get_course(name):
    return courses.find_one({"name": name})

def get_schedule(name, section='N/A'):
    if section == 'N/A':
        return schedules.find({"course": get_course(name)['_id']})
    return schedules.find_one({"course": get_course(name)['_id'], "section": section})   

#########################################################################################

def register_course(*arguments):
    if len(arguments) != 5:
        # await ctx.send('Usage: Course, day, time, section, link')
        raise Exception("Invalid number of Arguments.")
    else:
        args = argParser(*arguments) 
        course = courses.find_one_and_update({"name": args[0]}, {"$set": {"name": args[0]}}, upsert= True, return_document = pymongo.ReturnDocument.AFTER)
        sched = schedules.find_one({"course": course['_id'], "section": args[1]})
        if sched is None:
            schedules.insert_one({"course": course['_id'], "day": args[2].upper(), "time": args[3], "section": args[1], "link": [args[4]]})
        else:
            raise Exception("Already registered! Use add_link to add a link to the record.")   

#adds meet link corresponding to a course
def add_link(*args):
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
def get_link(name, section='N/A'):            
    sched = get_schedule(name, section)
    if isinstance(sched, pymongo.cursor.Cursor):
        links = []
        for doc in sched:
            links.extend(doc['link'])
        return links
    else:
        return sched['link']

def deregister(*args):
    if len(args) == 2:
        status = schedules.delete_many({"course": get_course(args[0])['_id'], "section":args[1]})
        if schedules.find_one({"course": get_course(args[0])['_id']}) is None:
            courses.delete_one({"name": args[0]})
    elif len(args) == 1:
        status = schedules.delete_many({"course":  get_course(args[0])['_id']})
        courses.delete_one({"name": args[0]})
    else:
        return -1
    return status.deleted_count

def remove_link(*args):
    sched = get_schedule(args[0], args[1])
    if args[2] in sched['link']:
        sched['link'].remove(args[2])
        schedules.update_one(sched, {"$set": {"link": sched['link']}})  #Probably wrong. Link is being set to old link and not deleted. @ingenium-cipher fix this. 
        return 1
    return 0


def remove_all():
    courses.drop()
    schedules.drop()

def show_all():
    all_courses = []
    for x in courses.find():  
        all_courses.append(x['name'])
    return all_courses
