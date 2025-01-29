# Quick Audio Cloner

A powerful and user-friendly voice cloning tool that allows you to clone voices from audio samples and generate speech in multiple languages using state-of-the-art AI technology.

## Features

- 🎯 Voice Cloning: Clone any voice from WAV audio samples
- 🌍 Multi-language Support: Generate speech in various languages
- 🎥 YouTube Integration: Download voice samples directly from YouTube videos
- 🔊 Audio Processing: Automatic silence removal and audio cleaning
- 🖥️ Cross-platform: Works on Windows, macOS, and Linux
- 🎛️ User-friendly CLI Interface: Easy-to-use menu system

## Requirements

- Python 3.10.16 (or lower, **mandatory for TTS to be installed**)
- Internet connection for model download (first run only) and voice download (if needed)

## Installation

**_NOTE: Skip this section if you are using `uv` (recommended)_**

```bash
pip install -r requirements.txt
```

Then, copy the .env.example file to .env:

```bash
cp .env.example .env
```

And adjust it accordingly. Anyway, you can override the configuration at runtime.

## Usage

**_NOTE: If you are using `uv`, dependencies will be resolved in a .venv file at runtime_**

**IMPORTANT: The included voice sample is noisy and short, so the result might be low quality. Use a better one for production. Sorry.**

### Using uv

```bash
uv run src/main.py
```

### Normal python

```bash
python src/main.py
```

## Overview

The application provides an interactive menu with the following options:

1. Start voice cloning with current settings
2. Select a target voice from available samples
3. Set a custom sentence to generate
4. Choose the target language
5. Download new voice samples from YouTube
6. Reset settings to default
7. Exit (duh)

## Voice Sample Guidelines

- Use clear, high-quality audio samples
- Samples should be in WAV format
- Ideal sample length: 10-30 seconds
- Avoid background noise or music
- Place voice samples in the `data/` directory

## Supported Languages

Use two-letter language codes (e.g., 'en' for English, 'fr' for French, 'es' for Spanish)
