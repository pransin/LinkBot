#!/usr/bin/python3

import discord
from discord.ext import commands
from keyconfig import *
import datetime
from HLTV import (
    get_important_match_results,
    get_best_players,
    get_important_upcoming_matches,
    get_live_matches,
    get_match_results,
    get_top_teams,
    get_upcoming_matches
)

# bot = commands.Bot(command_prefix = '$')

client = discord.Client()

lecture_dict = {
    '$mup': 'pass', 
    '$sas': 'pass', 
    '$mue': 'pass', 
    '$consys': 'pass', 
    '$poe': 'pass'
}

csgo_dict = {
    '$live': get_live_matches(),
    '$upcoming': get_upcoming_matches(),
    '$results': get_match_results(offset=95),
    '$top': get_top_teams(),
    '$gods': get_best_players(time_filter=14)
}

class Schedule():

    def __init__(self, subject, time, section, link):
        self.subject = subject
        self.time = time
        self.section = section
        self.link = link

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
        await message.channel.send('Hello!')
        # await message.channel.send(
        #     f"{message.author.mention}\n ```Time: 9 AM\n Link: Blah blah```")
    
    msg = message.content

    if any(word in msg for word in lecture_dict.keys()):
        await message.channel.send(
            f"Hey, {message.author.mention}! " +
             "Here's the link you requested: " + 
             lecture_dict[msg])

    if any(word in msg.split for word in csgo_dict.keys()):
        await message.channel.send(
            csgo_dict[msg] # This won't work. Try csgo_dict[msg][:11]. Reason: 2000 word limit being exceeded
        )

# @bot.command()
# async def add(ctx, *args):
#     print(args)
#     await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))

client.run(BOT_TOKEN)
# bot.run(BOT_TOKEN)
