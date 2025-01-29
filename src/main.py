from pathlib import Path
import torch
from TTS.api import TTS
import os
import dotenv
from libs.to_mp3 import convert_to_mp3
from libs.youtube_wav import download_from_cli
import os

tts = None
SPEAKER_WAV = None
LANGUAGE = None
SENTENCE = None

def load_config():
    global SPEAKER_WAV, LANGUAGE, SENTENCE
    # Load environment variables from .env file
    dotenv.load_dotenv()

    # Load configuration from environment variables
    SPEAKER_WAV = os.getenv("SPEAKER_WAV")  # Path to speaker voice sample
    LANGUAGE = os.getenv("LANGUAGE", "en")  # Target language for TTS
    SENTENCE = os.getenv("SENTENCE", "Hello there mortal!")

def load_model():
    global tts
    # Determine if CUDA is available for GPU acceleration
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Initialize the TTS model
    # Using XTTS v2 model which supports multiple languages
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)


def tts_audio(output_path: str = "./output/out.wav"):
    """
    Converts text to speech using the XTTS v2 model.

    Args:
        text (str): The text to convert to speech
        output_path (str): Path where the output WAV file will be saved

    Note:
        Uses environment variables:
        - SPEAKER_WAV: Path to a reference audio file for voice cloning
        - LANGUAGE: Target language code (e.g., "en", "es", "fr")
    """
    tts.tts_to_file(
        text=SENTENCE,
        speaker_wav=SPEAKER_WAV,
        language=LANGUAGE,
        file_path=output_path,
    )


def print_settings():
    """Print current settings in a formatted box."""
    # Get terminal width (default to 60 if can't determine)
    try:
        width = os.get_terminal_size().columns
        width = min(80, width)  # Cap at 80 chars
    except:
        width = 60

    # Create box elements
    h_line = "─" * (width - 2)
    top = f"┌{h_line}┐"
    bottom = f"└{h_line}┘"

    # Format settings with consistent spacing
    settings = [
        ("Speaker Voice", SPEAKER_WAV),
        ("Language", LANGUAGE),
        ("Target Sentence", SENTENCE),
    ]

    # Print formatted box
    print("\n" + top)
    print("│ Current Settings:".ljust(width - 1) + "│")
    print("│" + "─" * (width - 2) + "│")

    for label, value in settings:
        # Truncate value if too long
        max_value_length = width - len(label) - 7  # Account for spacing and box chars
        if len(value) > max_value_length:
            value = value[: max_value_length - 3] + "..."

        line = f"│ {label}: {value}"
        print(line.ljust(width - 1) + "│")

    print(bottom + "\n")


def start_job():
    """Start the TTS job with current settings."""
    print("\nStarting job...")
    outfile = input(
        "Insert an output filename or press enter to use the default (out.wav): "
    )
    outfile = outfile.strip()
    if outfile == "" or not outfile:
        outfile = "./output/out.wav"
    else:
        outfile = "./output/" + outfile

    load_model()
    tts_audio(outfile)
    print(f"\nAudio saved to: {outfile}")

    # Ask to play the file
    play_response = (
        input("\nWould you like to play the output file? [y/N] ").strip().lower()
    )
    if play_response in ["y", "yes"]:
        try:
            import platform

            system = platform.system()

            if system == "Windows":
                import winsound

                winsound.PlaySound(outfile, winsound.SND_FILENAME)
            elif system == "Darwin":  # macOS
                import subprocess

                subprocess.run(["afplay", outfile])
            elif system == "Linux":
                import subprocess

                subprocess.run(["aplay", outfile])
            else:
                print(f"Unsupported operating system: {system}")

        except Exception as e:
            print(f"Error playing audio: {str(e)}")
    # Ask to convert to mp3
    convert_response = (
        input("\nWould you like to convert the output file to mp3? [y/N] ").strip().lower()
    )
    if convert_response in ["y", "yes"]:
        convert_to_mp3(outfile)

def set_target_voice():
    """Set the target voice for TTS."""
    # Show the list of voices in data
    print("\nAvailable voices in data/:")
    data_path = Path("data")
    data_path.mkdir(exist_ok=True)

    # Get all .wav files and strip extensions
    voices = [f.stem for f in data_path.glob("*.wav")]

    if not voices:
        print("No voices found. Use option 4 to download a voice first.")
        return

    # Print numbered list
    for i, voice in enumerate(voices, 1):
        print(f"{i}. {voice}")

    # Get user selection
    while True:
        try:
            choice = input("\nSelect a voice number (or 0 to cancel): ").strip()
            if choice == "0":
                return

            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(voices):
                selected_voice = voices[choice_idx]
                global SPEAKER_WAV
                SPEAKER_WAV = str(data_path / f"{selected_voice}.wav")
                print(f"\nSelected voice: {selected_voice}")
                break
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")


def set_target_sentence():
    """Set the target sentence for TTS."""
    print("\nSetting target sentence...")
    global SENTENCE
    new_sentence = input("What should your voice say?\n")
    new_sentence = new_sentence.strip()
    if new_sentence == "" or not new_sentence:
        print("No sentence has been detected. Using the current settings.\n")
    else:
        SENTENCE = new_sentence


def set_language():
    """Set the target language for TTS"""
    print("\nSetting target sentence...")
    global LANGUAGE
    new_language = input(
        "What should be the language used (two letters e.g. en,it,fr) ?\n"
    )
    new_language = new_language.strip()
    if new_language == "" or not new_language or (not len(new_language) == 2):
        print("No language has been detected. Using the current settings.\n")
    else:
        LANGUAGE = new_language


def download_voice():
    """Download voice from YouTube."""
    print("\nDownloading voice from YouTube...")
    download_from_cli()


def menu():
    """Display and handle the main menu."""
    menu_options = {
        "Main Options": [
            ("1", "Start the job using current settings", start_job),
            ("2", "Set a target voice", set_target_voice),
            ("3", "Set a target sentence", set_target_sentence),
            ("4", "Set a language", set_language),
        ],
        "Utilities": [
            ("5", "Download a voice from YouTube", download_voice),
            ("6", "Reset settings to .env", load_config),
            ("7", "Exit", None),
        ],
    }

    while True:
        print("\n" + "=" * 60 + "\n")
        print_settings()

        # Print menu with categories
        for category, options in menu_options.items():
            print(f"\n{category}:")
            print("─" * 40)
            for key, label, _ in options:
                print(f"{key}. {label}")

        choice = input("\nEnter your choice (1-7): ").strip()

        # Find and execute the selected function
        for category in menu_options.values():
            for key, _, func in category:
                if choice == key:
                    if func:  # Execute function if it exists
                        func()
                    elif key == "7":  # Exit case
                        print("\nGoodbye!")
                        return
                    break
            else:
                continue
            break
        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    print("Welcome to Easy Voice Cloner!")
    load_config()
    menu()
