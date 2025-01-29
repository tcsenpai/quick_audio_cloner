import yt_dlp
import os
from pathlib import Path
import random
import time
import re
import argparse
from libs.audio_cleaner import clean_audio


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to lowercase, no spaces, no special characters.
    """
    # Remove file extension first
    base = os.path.splitext(filename)[0]
    # Replace spaces and special chars with underscore, convert to lowercase
    sanitized = re.sub(r"[^a-zA-Z0-9]", "_", base).lower()
    # Remove consecutive underscores
    sanitized = re.sub(r"_+", "_", sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip("_")
    return f"{sanitized}.wav"


def download_youtube_audio(
    url: str, custom_name: str = None, output_path: str = None
) -> str:
    """
    Download audio from YouTube video and convert to WAV format.

    Args:
        url (str): YouTube video URL (supports both youtube.com and youtu.be)
        custom_name (str, optional): Custom name for the output file
        output_path (str, optional): Path to save the WAV file. If None, uses ./data

    Returns:
        str: Path to the downloaded WAV file
    """
    print("Starting download process...")

    # Set default output path to ./data
    if output_path is None:
        output_path = Path("data")
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_path}")

    # Configure yt-dlp options with custom filename template
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ],
        # Use temporary filename template
        "outtmpl": str(output_path / "%(title)s.%(ext)s"),
        "quiet": False,  # Show some progress
        "no_warnings": True,
        "retries": 10,
        "fragment_retries": 10,
        "retry_sleep": lambda _: random.uniform(1, 5),
        "source_address": "0.0.0.0",
        "headers": {
            "User-Agent": get_random_user_agent(),
        },
        "progress_hooks": [lambda d: print(f"Downloading: {d['status']}")],
    }

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("Fetching video information...")
                # Extract video info first
                info = ydl.extract_info(url, download=False)
                temp_filename = (
                    ydl.prepare_filename(info)
                    .replace(".webm", ".wav")
                    .replace(".m4a", ".wav")
                )

                # Create sanitized filename based on custom name or video title
                if custom_name:
                    sanitized_filename = (
                        output_path / f"{sanitize_filename(custom_name)}"
                    )
                else:
                    print("No custom name provided, using video title...")
                    sanitized_filename = output_path / sanitize_filename(
                        os.path.basename(temp_filename)
                    )

                print(f"Final filename will be: {sanitized_filename}")

                # Download if sanitized file doesn't exist
                if not sanitized_filename.exists():
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                    print("Starting download and conversion...")
                    ydl.download([url])
                    print("Download complete, renaming file...")
                    os.rename(temp_filename, sanitized_filename)
                else:
                    print("File already exists, skipping download.")

                print("Process completed successfully!")
                return str(sanitized_filename)

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_attempts - 1:
                raise Exception(
                    f"Failed to download after {max_attempts} attempts: {str(e)}"
                )
            print(f"Retrying in {(attempt + 1) ** 2} seconds...")
            time.sleep((attempt + 1) ** 2)
            ydl_opts["headers"]["User-Agent"] = get_random_user_agent()


def get_random_user_agent() -> str:
    """Return a random user agent string to avoid detection."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    ]
    return random.choice(user_agents)


def download_from_cli() -> str:
    """
    Handle command line interface for downloading YouTube audio.
    Returns the path to the downloaded file.
    """
    parser = argparse.ArgumentParser(description="Download YouTube audio as WAV")
    parser.add_argument("--url", "-u", help="YouTube URL (youtube.com or youtu.be)")
    parser.add_argument("--output", "-o", help="Output directory (optional)")
    args = parser.parse_args()

    # Get URL from argument or prompt
    url = args.url
    if not url:
        url = input("Enter YouTube URL: ").strip()

    # Get custom name
    custom_name = input(
        "Enter a name for the voice (press Enter to use video title): "
    ).strip()
    custom_name = custom_name if custom_name else None

    # Get output path
    output_path = args.output

    try:
        output_file = download_youtube_audio(url, custom_name, output_path)
        print("[*] Cleaning audio from silence...")
        clean_audio(output_file)
        print(f"\nSuccessfully saved to: {output_file}")
        return output_file
    except Exception as e:
        print(f"\nError: {str(e)}")
        raise


if __name__ == "__main__":
    download_from_cli()
