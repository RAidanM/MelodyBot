from abc import ABC, abstractmethod
from dataclasses import dataclass
import discord
import yt_dlp


@dataclass
class AudioInfo:
    '''
    Data class representing an audio source and its title.
    '''

    source: discord.player.AudioSource
    '''
    The audio source to be given to `discord.voice_client.VoiceClient.play`
    method.
    '''

    title: str
    '''
    The title of the audio so that the bot can send the title in a message.
    '''


class AudioPlayer(ABC):
    '''
    Abstract class representing an audio player.
    '''

    @abstractmethod
    def fetch(self) -> AudioInfo:
        '''
        Fetches audio and returns its `AudioInfo`.
        '''
        pass


class TestAudioPlayer(AudioPlayer):
    '''
    Test audio player used for debugging.
    '''

    def __init__(self):
        super().__init__()

    def fetch(self) -> AudioInfo:
        # sound_effect.mp3 is a royalty-free sound found at
        # https://pixabay.com/sound-effects/notification-22-270130/
        return AudioInfo(
            discord.FFmpegPCMAudio('./sound_effect.mp3'),
            'Test Sound'
        )


class YouTubeAudioPlayer(AudioPlayer):
    '''
    Audio player from a YouTube source.
    '''

    url: str
    '''
    The YouTube URL for the audio.
    '''

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def fetch(self) -> AudioInfo:
        ydl_options = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_options) as ydl:
                info = ydl.extract_info(self.url, download=False)

                audio_url = info['url']
                title = info['title']

                ffmpeg_options = {
                    'options': '-vn'
                }
                source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
                return AudioInfo(source, title)
        except Exception as e:
            raise Exception(e)


class UnmappedUrlException(Exception):
    '''
    Exception representing the situation where a URL could not be mapped to an
    audio player.
    '''

    def __init__(self, *args):
        super().__init__(*args)


def create_audio_player(url: str) -> AudioPlayer:
    '''
    Creates an audio player based on the URL.

    Args:
        url: The URL to be mapped to an audio player.

    Returns:
        An audio player corresponding to the given URL.

    Raises:
        UnmappedUrlException: If no audio player could be found that is mapped
        to the given URL.
    '''

    if url == 'test':
        return TestAudioPlayer()
    elif url.startswith('https://www.youtube.com/watch'):
        return YouTubeAudioPlayer(url)
    else:
        raise UnmappedUrlException('URL could not be mapped to audio player')
