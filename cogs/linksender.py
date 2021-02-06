import discord
from discord.ext import commands

from dotenv import load_dotenv, find_dotenv
from packages import scheduleFetcher
load_dotenv(find_dotenv())


class Sender(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['register', 'add'], brief='Add a course to the DB')
    async def register_course(self, ctx, *args):
        if len(args) != 5:
            await ctx.send('Usage: Course, day, time, section, link')
        else:
            try:
                scheduleFetcher.register_course(args[0], args[1], args[2], args[3], args[4])
                await ctx.message.add_reaction('\U0001F44C')
            except Exception as e:
                await ctx.send(f'{e}')

    @commands.command(brief='Deregisters all sections of a course if no section is given, otherwise deregisters the given section.')
    async def deregister(self, ctx, *args):
        status = scheduleFetcher.deregister(*args)
        if status > 0:
            await ctx.message.add_reaction('\U0001F44C')
        elif status == 0:
            await ctx.send("Course does not exist.")
        else:
            await ctx.send("C'mon, that's not even valid syntax")

    @commands.command(aliases = ['add_link'], brief='Adds link to a course. Usage: <Course> <Section>')
    async def addlink(self, ctx, *args):
        status = scheduleFetcher.add_link(*args)
        if status == 1:
            await ctx.message.add_reaction('\U0001F44C')
        elif status == 2:
            await ctx.send(f'Link already exists!')
        elif status == 0:
            await ctx.send('Invalid URL Format.')
    
    @commands.command(brief='Retrieves link(s) of a course', description='Usage: $getlink [Course Name] [Section]=optional.\n Sends links of all sections of a course if section is omitted.')
    async def getlink(self, ctx, *args):
        try:
            links = scheduleFetcher.get_link(*args)
            nospam = '>\n<'
            await ctx.send(f"<{nospam.join(links)}>")
        except:
            await ctx.send("You sure that course/link has been added?")
    
    @commands.command(brief='Removes given link *****')
    async def remove_link(self, ctx, *args):
        status = scheduleFetcher.remove_link(args[2])
        if status:
            await ctx.send(f"Link removed from {args[0]} {args[1]}")
        else:
            await ctx.send("Link not present.")
    
    @commands.command(brief='Deregisters all courses. Use with caution!')
    async def clear_database(self, ctx):
        await scheduleFetcher.remove_all()
        await ctx.send('Database cleared.')

    @commands.command(brief='Shows all registered courses')
    async def show_all(self, ctx):
        all_courses = scheduleFetcher.show_all()
        ctx.send('\n'.join(all_courses))


def setup(bot):
    bot.add_cog(Sender(bot))

