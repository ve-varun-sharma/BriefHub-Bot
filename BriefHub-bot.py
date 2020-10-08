import discord
import os
from discord.ext import commands 
import random
import wikipedia
import logging
import traceback
import requests
import smtplib
import os
from config import PYBOT_EMAIL, PYBOT_PW
from autoscraper import AutoScraper
from dotenv import load_dotenv  
load_dotenv() 

# Discord Security Tokens which are fetched from the .env file 
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  
GUILD_TOKEN = os.getenv('DISCORD_GUILD')
nl = '\n'
# client = discord.Client()  # starts the discord client.
briefbot = commands.Bot(command_prefix='$') # sets up discord client and decorator commands

@briefbot.event 
async def on_ready():  # method expected by client. This runs once when connected
    print(f'We have logged in as {briefbot.user}')  

@briefbot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to my Discord Server!')


@briefbot.event
async def on_message(test_message):
    if test_message.content == 'Easter Egg':
        await test_message.channel.send('You have found the first clue to the easter egg. What is green, has the armor of a dragon, yet it comes from where the damned reside for an eternity.')
    
    await briefbot.process_commands(test_message)

@briefbot.event
async def on_message(message):
    if message.author == briefbot.user:
        return
    
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    await briefbot.process_commands(message)


@briefbot.event
async def on_member_join(member):
    print(f'{member} has joined the server.')

@briefbot.event
async def on_member_remove(member):
    print(f'{member} has left the server.')

@briefbot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hey {member.name}, welcome to my Discord server!')

# @briefbot.command(search_words=['whatis','whereis'])
# async def whatis(ctx, *, search_term):
#     brainbot = wikipedia.summary(search_term, auto_suggest=False, redirect=False, sentences=3)
#     await ctx.channel.send(f"Success~! I have found results/nHere is what I found for '{search_term}':/n{brainbot}")
#     if  wikipedia.exceptions.PageError(pageid=None) == True:
#         await ctx.channel.send(f"Hmm, it doesn't look I found anything for '{search_term}'./nhere are some alternative suggestions: {wikipedia.search(search_term, results=10, suggestion=False)} ")
#     if  wikipedia.exceptions.PageError(pageid=None) == True or wikipedia.exceptions.DisambiguationError == True:
#         await ctx.channel.send(f"Hmm, it still doesn't look I found anything for '{search_term}'. /nHere is what recovered: {(wikipedia.exceptions.DisambiguationError.options)}")

@briefbot.command(search_words=['whatis','whereis'])
async def whatis(ctx, *, search_term):
    brainbot = wikipedia.summary(search_term, auto_suggest=False, redirect=False, sentences=3)
    try:
        await ctx.channel.send(f"Success! 🚀 Here is what I found for '{search_term}':{nl}{brainbot}")
    except wikipedia.exceptions.DisambiguationError as e:
        await ctx.channel.send(f"Hmm, it doesn't look I found anything for '{search_term}'.{nl}here are some alternative suggestions: {e} ")


@briefbot.command(search_words=['everythingabout','tellmeeverything','fullsend'])
async def everythingabout(ctx, *, search_term):
    brainbot = wikipedia.summary(search_term, auto_suggest=False, redirect=False, sentences=15)
    await ctx.channel.send(f"Success! 🚀 I have found results/nHere is what I found for '{search_term}':{nl}{brainbot}")
    if  wikipedia.exceptions.PageError(pageid=None) == True:
        await ctx.channel.send(f"Hmm, it doesn't look I found anything for '{search_term}'./nhere are some alternative suggestions: {wikipedia.search(search_term, results=10, suggestion=False)} ")
    if  wikipedia.exceptions.PageError(pageid=None) == True or wikipedia.exceptions.DisambiguationError == True:
        await ctx.channel.send(f"Hmm, it still doesn't look I found anything for '{search_term}'. {nl}Here is what recovered: {(wikipedia.exceptions.DisambiguationError.options)}")


@briefbot.command()
async def whois(ctx, *args):
    try:
        whois_url = 'https://www.facebook.com/search/top/?q=' + str(args)
        search4person = requests.get(whois_url)
        await ctx.channel.send(f"Success! 🚀 I have found you results for the person you're looking for!{nl}Here is who I found for {args}/n{search4person}")
    except requests.exceptions.Timeout as et:
        await ctx.channel.send(et)
        # Maybe set up for a retry, or continue in a retry loop
    except requests.exceptions.TooManyRedirects as tr:
        await ctx.channel.send(tr)
        # Tell the user their URL was bad and try a different one
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        raise SystemExit(e)

@briefbot.command()
async def ping(ctx):
    await ctx.send(f'pong! {round(briefbot.latency * 1000)}ms')

# 8ball command gives a randomized answer from the 8ball answer list
@briefbot.command(aliases=['8ball', 'eightball'])
async def _8ball(ctx, *, question):
    responses = [
                'As I see it, yes.',
                'Ask again later.',
                'Better not tell you now.',
                'Cannot predict now.',
                'Concentrate and ask again.',
                'Don’t count on it.',
                'It is certain.',
                'It is decidedly so.',
                'Most likely.',
                'My reply is no.',
                'My sources say no.',
                'Outlook not so good.',
                'Outlook good.',
                'Reply hazy, try again.',
                'Signs point to yes.',
                'Very doubtful.',
                'Without a doubt.',
                'Yes.',
                'Yes – definitely.',
                'You may rely on it.']
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

# Briefbot autoscrapper which can get data from most websites. 
@briefbot.command(find_words=['search', 'look for', 'get', 'find', 'scrape'])
async def scrape(ctx, url: str, wanted_list: str):
    # url = ''
    # wanted_list = ['']
    botscraper = AutoScraper()
    print(type(url))
    print(type(wanted_list))
    scrape_result = botscraper.build(url, wanted_list)
    print(scrape_result)
    results_message = '\r\n'.join(['BriefHub bot has found results! 🚀',
                        f"Here is what I found for * {wanted_list} * on * {url} * : {str(scrape_result)}",
                        ':-)'])
     
    await ctx.send(results_message)

# Send instant email directly from the Discord Chat without having to log in or leave the window.
@briefbot.command()
async def sendemail(ctx, recipient, *content):
    try:
        subject = 'Discord Email from BriefHub'
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(PYBOT_EMAIL, PYBOT_PW)
        message = 'subject: {}\n\n{}'.format(subject, str(content))
        server.sendmail(PYBOT_EMAIL, recipient, message)
        server.quit()
        print('Success: Email Sent!')
        await ctx.channel.send(f"Success!🚀 {nl} You're Discord Email has been sent!")

    except Exception as error:
        error = "Failed to connect to server. Email not sent."
        print(error)
        await ctx.channel.send(f"Sorry, that didn't seem to work {nl} Here is a report:{nl}{Exception}")

# A command that mirror prints back the message the user typed out
@briefbot.command()
async def printthis(ctx, *args):
    response = ""
    for arg in args:
        response = response +  " " + arg
    await ctx.channel.send(response)

from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt

@briefbot.command()
async def stocknews (ctx, arg):
    ts = TimeSeries(key='BYMSO9FUQY633Q7W', output_format='pandas')
    data = ts.get_intraday(symbol= arg, interval='1min', outputsize='full')
    data['close'].plot()
    print(plt.title(f'Intraday Times Series for the {arg} stock (1 min)'))
    print(plt.show())
    await ctx.channel.send(plt.show)

import requests
import json
@briefbot.command()
async def showmethemonney (ctx, arg):
    arg = ticker
    key = 'BYMSO9FUQY633Q7W'
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&apikey={}'.format(ticker, key)
    await ctx.channel.send(url)


# Briefbot Help command list
@briefbot.command(help_words=['help', 'assistance', 'help!'])
async def bot_help(ctx):
    help_message = '\r\n'.join(['$help: Returns all of the commands and what they do.',
                        '$ping: Returns the ping latency from the server',
                        '$get: Returns web scraping results for specific information',
                        "$sendemail: Sends an instal email. Quote the receiver address, and quote the message.",
                        "$printthis: Simply echos the message you typed",
                        "$scrape: Enter any URL and headtitles from the link and it will return summary information",
                        "$stocknews: Enter a Stock Ticker symbol and this returns daily adjusted stock info",
                        "$8ball: Ask any question and it will return 8 ball classic answers",
                        "$whatis: Returns brief information about anything. Answers retrieved from Wikipedia.",
                        "$everythingabout: Returns more information than $whatis",
                        "$about: Returns randomized general information about BriefHub Bot"])
    await ctx.channel.send(help_message)

# Briefbot tells the user a small summary about itself
@briefbot.command(about_words=['about', 'aboutBriefBot',])
async def about(ctx):
    about_responses = [
                "Hey there! I'm BriefBot, your personal assistant on Discord. Please let me know how I can help you!.",
                "I am BriefBot from BriefHub. I am here to help optimize your productivity and spice up your workflow!.",
                "Hello there, I'm an AMA Bot. Ask me anything! (Hint, enter: $bot_help)"]
    await ctx.send(f'{random.choice(about_responses)}')

# Discord command error function that returns the appropiate errors and exceptions for cases
async def on_command_error(self, ctx, exception):
        self.stats.increment("RPGBot.errors", tags=["RPGBot:errors"], host="scw-8112e8")
        logging.info(f"Exception in {ctx.command} {ctx.guild}:{ctx.channel} {exception}")
        exception = getattr(exception, "original", exception)
        traceback.print_tb(exception.__traceback__)
        print(exception)
        try:
            if isinstance(exception, commands.MissingRequiredArgument):
                await ctx.send(f"```{exception}```")
            elif isinstance(exception, TimeoutError):
                await ctx.send(await (ctx, "This operation ran out of time! Please try again"))
            elif isinstance(exception, discord.Forbidden):
                await ctx.send(await (ctx, "Error: This command requires the bot to have permission to send links."))
            else:
                await ctx.send(f"`{exception} If this is unexpected, please report this to the bot creator`")
        except discord.Forbidden:
            pass 

briefbot.run(DISCORD_TOKEN)