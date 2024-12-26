import logging
from dotenv import dotenv_values
import discord
import discord.ext
import discord.ext.commands


logger = logging.getLogger('discord')

intents = discord.Intents.default()
intents.message_content = True

bot = discord.ext.commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    logger.info(f'Ready: {bot.user}')


@bot.command()
async def hello(ctx: discord.ext.commands.Context, arg):
    logger.info(f'Received hello command with arg {arg}')
    await ctx.send('Hi lol')


if __name__ == '__main__':
    config = dotenv_values(".env")
    if 'BOT_TOKEN' not in config or not config['BOT_TOKEN']:
        raise Exception('BOT_TOKEN must be defined in .env file')
    bot.run(config['BOT_TOKEN'])
