import os
import discord
import discord.ext
import discord.ext.commands
from dotenv import dotenv_values


intents = discord.Intents.default()
intents.message_content = True

bot = discord.ext.commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Ready: {bot.user}')

@bot.command()
async def hello(ctx: discord.ext.commands.Context, arg):
    print('hi')
    print(arg)
    await ctx.send('Hi lol')


if __name__ == '__main__':
    config = dotenv_values(".env")
    bot.run(config['BOT_TOKEN'])
