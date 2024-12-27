import os
import logging
import asyncio
from collections import deque
from typing import Deque
from dotenv import load_dotenv
import discord
import discord.ext
import discord.ext.commands
from audio_player import create_audio_player, UnmappedUrlException, AudioInfo


if not os.getenv('PRODUCTION_ENV'):
    load_dotenv()

command_prefix = os.getenv('COMMAND_PREFIX')

if not command_prefix:
    raise Exception('COMMAND_PREFIX environment variable is not defined')

logger = logging.getLogger('discord')
'''Logger for the bot.'''

# We need the `message_content` intent to read commands.
# https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html
intents = discord.Intents.default()
intents.message_content = True

bot = discord.ext.commands.Bot(command_prefix=command_prefix, intents=intents)
'''The bot.'''

queue: Deque[AudioInfo] = deque()
'''Queue containing songs that are waiting to be played'''

skip_signal: bool = False
'''
Global boolean variable used to signal to the bot to skip the current song.
'''

stop_signal: bool = False
'''
Global boolean variable used to signal to the bot to stop playing and clear the
queue.
'''


@bot.event
async def on_ready():
    '''
    Executes once the bot is ready.
    '''
    logger.info(f'Ready: {bot.user}')


@bot.command()
async def ping(ctx: discord.ext.commands.Context):
    '''
    Ping command to make sure the bot is working properly. The bot will just
    respond with 'Pong!'.
    '''
    logger.info(f'Received ping command from {ctx.author}')
    await ctx.send('Pong!')


@bot.command()
async def play(ctx: discord.ext.commands.Context, url: str):
    '''
    Plays audio from a URL.
    '''
    global queue
    global skip_signal
    global stop_signal

    logger.info(f'Received play command from {ctx.author} for URL {url}')

    # Make sure the user that gave the command is in a voice channel
    voice_state = ctx.author.voice
    voice_channel = voice_state.channel if voice_state is not None else None
    if not voice_channel:
        await ctx.send(
            'The `play` command must be sent while in a voice channel!'
        )
        return

    # Make sure the bot is in the voice channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        voice_client = await voice_channel.connect()

    try:
        # Get audio player based on the URL
        audio_player = create_audio_player(url)
        audio_info = audio_player.fetch()

        # If the bot is already playing something, just add the audio to queue
        if voice_client.is_playing() or voice_client.is_paused():
            queue.append(audio_info)
            await ctx.send(f'Added {audio_info.title} to the queue')
            return

        # The audio that is currently playing
        currently_playing: AudioInfo = audio_info

        while True:
            # Play the audio
            voice_client.play(currently_playing.source)
            await ctx.send(f'Playing {currently_playing.title}')

            # Keep running in a while loop so that the bot can listen for skip
            # or stop signals
            while voice_client.is_playing() or voice_client.is_paused():
                # Handle stop signal
                if stop_signal:
                    await ctx.send(
                        f'Stopping {currently_playing.title} and clearing queue.'
                    )
                    queue.clear()
                    voice_client.stop()
                    # Set the stop signal to false since it has now been handled
                    stop_signal = False
                    break

                # Handle skip signal
                if skip_signal:
                    await ctx.send(f'Skipping {currently_playing.title}.')
                    voice_client.stop()
                    # Set the skip signal to false since it has now been handled
                    skip_signal = False
                    break

                # Sleep (asynchronously) so that it's not an infinite loop
                await asyncio.sleep(1)

            # Stop when there is nothing in the queue
            if len(queue) == 0:
                break
            else:
                # If there are more audios in the queue, take the next audio to
                # play
                currently_playing = queue.popleft()
    except UnmappedUrlException as e:
        await ctx.send(
            f'ERROR: URL {url} could not be mapped to an audio player'
        )
    except Exception as e:
        logger.error(e)
        await ctx.send(f'ERROR: Unknown error {e}')


@bot.command()
async def skip(ctx: discord.ext.commands.Context):
    '''
    Skips the currently-playing song.

    The logic to skip the audio happens in the `play` method.
    '''
    global skip_signal

    logger.info(f'Received skip command from {ctx.author}')

    # Make sure the user that gave the command is in a voice channel
    voice_state = ctx.author.voice
    voice_channel = voice_state.channel if voice_state is not None else None
    if not voice_channel:
        await ctx.send(
            'The `skip` command must be sent while in a voice channel!'
        )
        return

    # Make sure the bot is in the voice channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await ctx.send('Skip? I\'m not even here!')
        return

    # Make sure the bot is currently playing something
    if voice_client.is_playing() or voice_client.is_paused():
        # Send the signal
        skip_signal = True
    else:
        await ctx.send('Skip? I\'m not even playing anything!')


@bot.command()
async def stop(ctx: discord.ext.commands.Context):
    '''
    Stops the currently-playing audio and clears the queue.

    The logic to stop the audio and clear the queue happen in the `play` method.
    '''
    global stop_signal

    logger.info(f'Received stop command from {ctx.author}')

    # Make sure the user that gave the command is in a voice channel
    voice_state = ctx.author.voice
    voice_channel = voice_state.channel if voice_state is not None else None
    if not voice_channel:
        await ctx.send(
            'The `stop` command must be sent while in a voice channel!'
        )
        return

    # Make sure the bot is in the voice channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await ctx.send('Stop? I\'m not even here!')
        return

    # Make sure the bot is currently playing something
    if voice_client.is_playing() or voice_client.is_paused():
        # Send the stop signal
        stop_signal = True
    else:
        await ctx.send('Stop? I\'m not even playing anything!')


@bot.command()
async def pause(ctx: discord.ext.commands.Context):
    '''
    Pauses the currently-playing audio.

    The logic to pause the audio happens in the `play` method.
    '''

    logger.info(f'Received pause command from {ctx.author}')

    # Make sure the user that gave the command is in a voice channel
    voice_state = ctx.author.voice
    voice_channel = voice_state.channel if voice_state is not None else None
    if not voice_channel:
        await ctx.send(
            'The `pause` command must be sent while in a voice channel!'
        )
        return

    # Make sure the bot is in the voice channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await ctx.send('Pause? I\'m not even here!')
        return

    # Make sure the bot is not already paused
    if voice_client.is_paused():
        await ctx.send('I\'m already paused!!!')
        return

    # Make sure the bot is currently playing something
    if voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send('Pause? I\'m not even playing anything!')


@bot.command()
async def resume(ctx: discord.ext.commands.Context):
    '''
    Resumes the currently-paused audio.

    The logic to resume the audio happens in the `play` method.
    '''

    logger.info(f'Received resume command from {ctx.author}')

    # Make sure the user that gave the command is in a voice channel
    voice_state = ctx.author.voice
    voice_channel = voice_state.channel if voice_state is not None else None
    if not voice_channel:
        await ctx.send(
            'The `resume` command must be sent while in a voice channel!'
        )
        return

    # Make sure the bot is in the voice channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await ctx.send('Resume? I\'m not even here!')
        return

    # Make sure the bot is not already playing
    if voice_client.is_playing():
        await ctx.send('I\'m already playing!!!')
        return

    # Make sure the bot is currently paused
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send('Resume? I\'m not even paused!')


if __name__ == '__main__':
    # Get bot token from environment
    bot_token = os.getenv('BOT_TOKEN')

    # Make sure the `BOT_TOKEN` environment variable is set
    if not bot_token:
        raise Exception('BOT_TOKEN environment variable is not defined')

    # Run the bot
    bot.run(bot_token)
