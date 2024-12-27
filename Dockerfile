# Use an official Python runtime as a base image
FROM python:3.10-slim

# Install FFmpeg and other system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopus-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the bot's code and requirements
COPY requirements.txt ./
COPY main.py ./
COPY audio_player.py ./

# Copy test sound
COPY sound_effect.mp3 ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the entry point to run the bot
CMD ["python", "main.py"]
