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
async def ping(ctx: discord.ext.commands.Context):
    logger.info(f'Received ping command from {ctx.author}')
    await ctx.send('Pong!')

@bot.command()
async def play(ctx: discord.ext.commands.Context, url: str):
    logger.info(f'Received play command from {ctx.author} for URL {url}')

    voice_state = ctx.author.voice
    voice_channel = voice_state.channel if voice_state is not None else None
    if not voice_channel:
        await ctx.send(
            'The `play` command must be sent while in a voice channel!'
        )
        return

    voice_client = await voice_channel.connect()

    # sound_effect.mp3 is a royalty-free sound found at
    # https://pixabay.com/sound-effects/notification-22-270130/
    voice_client.play(discord.FFmpegPCMAudio('./sound_effect.mp3'))

    await ctx.send('Playing')


if __name__ == '__main__':
    config = dotenv_values(".env")
    if 'BOT_TOKEN' not in config or not config['BOT_TOKEN']:
        raise Exception('BOT_TOKEN must be defined in .env file')
    bot.run(config['BOT_TOKEN'])
