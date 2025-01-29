from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import os
import argparse


def clean_audio(
    wav_path: str, min_silence_len: int = 100, silence_thresh: int = -40
) -> str:
    """
    Remove silence from the beginning and end of a WAV file.

    Args:
        wav_path (str): Path to the input WAV file
        min_silence_len (int): Minimum length of silence in milliseconds
        silence_thresh (int): Silence threshold in dB

    Returns:
        str: Path to the cleaned audio file
    """
    # Validate input file
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"Audio file not found: {wav_path}")

    # Load audio file
    audio = AudioSegment.from_wav(wav_path)

    # Detect non-silent chunks
    nonsilent_ranges = detect_nonsilent(
        audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh
    )

    if not nonsilent_ranges:
        return wav_path  # Return original if no non-silent ranges found

    # Get start and end times of non-silent audio
    start_trim = nonsilent_ranges[0][0]
    end_trim = nonsilent_ranges[-1][1]

    # Trim the audio
    cleaned_audio = audio[start_trim:end_trim]

    # Generate output filename
    output_path = wav_path.rsplit(".", 1)[0] + ".wav"

    # Export cleaned audio
    cleaned_audio.export(output_path, format="wav")

    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean silence from WAV files")
    parser.add_argument("wav_path", help="Path to the WAV file to clean")
    parser.add_argument(
        "--min-silence",
        type=int,
        default=100,
        help="Minimum length of silence in milliseconds (default: 100)",
    )
    parser.add_argument(
        "--silence-thresh",
        type=int,
        default=-40,
        help="Silence threshold in dB (default: -40)",
    )

    args = parser.parse_args()

    try:
        output_path = clean_audio(
            args.wav_path,
            min_silence_len=args.min_silence,
            silence_thresh=args.silence_thresh,
        )
        print(f"Cleaned audio saved to: {output_path}")
    except Exception as e:
        print(f"Error: {str(e)}")
