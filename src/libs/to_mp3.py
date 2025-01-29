from pathlib import Path
from pydub import AudioSegment


def convert_to_mp3(wav_path: str, bitrate: str = "192k") -> str:
    """
    Convert a WAV file to MP3 format in the same directory.

    Args:
        wav_path (str): Path to the WAV file
        bitrate (str): MP3 bitrate (default: "192k")

    Returns:
        str: Path to the created MP3 file
    """
    # Convert string path to Path object
    wav_path = Path(wav_path)

    # Check if input file exists and is WAV
    if not wav_path.exists():
        raise FileNotFoundError(f"File not found: {wav_path}")
    if wav_path.suffix.lower() != ".wav":
        raise ValueError(f"Input file must be a WAV file, got: {wav_path.suffix}")

    # Create output path with same name but .mp3 extension
    mp3_path = wav_path.with_suffix(".mp3")

    try:
        # Load WAV and export as MP3
        audio = AudioSegment.from_wav(str(wav_path))
        audio.export(str(mp3_path), format="mp3", bitrate=bitrate)
        return str(mp3_path)
    except Exception as e:
        raise Exception(f"Error converting WAV to MP3: {str(e)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert WAV to MP3")
    parser.add_argument("wav_path", help="Path to the WAV file to convert")
    parser.add_argument("--bitrate", default="192k", help="MP3 bitrate (default: 192k)")

    args = parser.parse_args()

    try:
        output_path = convert_to_mp3(args.wav_path, args.bitrate)
        print(f"Successfully converted to: {output_path}")
    except Exception as e:
        print(f"Error: {str(e)}")
