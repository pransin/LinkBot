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

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    print(message.author)
    # print(client)
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        # await message.channel.send('Hello!')
        await message.channel.send(
            f"{message.author.mention}\n ```Time: 9 AM\n Link: Blah blah```")

@bot.command()
async def add(ctx, *args):
    print(args)
    Schedule(args[0], args[1], args[2], args[3])
    await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))

# client.run('ODAxNzU2NTIzMjAxNDI5NTE0.YAlT8w.X93uh8DNfOp3vbVBUcS0kgYQrU8')
bot.run(BOT_TOKEN)