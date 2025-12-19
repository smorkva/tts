"""
Audio preparation script for XTTS-v2 voice cloning.
Converts audio files to the required format: WAV, 22050 Hz, mono.
"""

import argparse
import subprocess
import sys
from pathlib import Path


SAMPLE_RATE = 22050
CHANNELS = 1


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_audio_duration(input_path: Path) -> float:
    """Get audio duration in seconds using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(input_path)
        ],
        capture_output=True,
        text=True
    )
    return float(result.stdout.strip())


def convert_audio(
    input_path: Path,
    output_path: Path,
    start: float = None,
    duration: float = None
) -> bool:
    """
    Convert audio to XTTS-v2 compatible format.

    Args:
        input_path: Source audio file
        output_path: Destination WAV file
        start: Start time in seconds (optional)
        duration: Duration in seconds (optional)

    Returns:
        True if successful, False otherwise
    """
    cmd = ["ffmpeg", "-y", "-i", str(input_path)]

    if start is not None:
        cmd.extend(["-ss", str(start)])

    if duration is not None:
        cmd.extend(["-t", str(duration)])

    cmd.extend([
        "-ar", str(SAMPLE_RATE),
        "-ac", str(CHANNELS),
        "-acodec", "pcm_s16le",
        str(output_path)
    ])

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Prepare audio for XTTS-v2 voice cloning"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input audio file (any format)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output WAV file (default: input_prepared.wav)"
    )
    parser.add_argument(
        "-s", "--start",
        type=float,
        default=None,
        help="Start time in seconds"
    )
    parser.add_argument(
        "-d", "--duration",
        type=float,
        default=None,
        help="Duration in seconds (recommended: 10-15)"
    )

    args = parser.parse_args()

    if not check_ffmpeg():
        print("Error: FFmpeg not found. Please install FFmpeg first.")
        sys.exit(1)

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    output = args.output or args.input.with_stem(f"{args.input.stem}_prepared").with_suffix(".wav")
    output.parent.mkdir(parents=True, exist_ok=True)

    print(f"Input:  {args.input}")
    print(f"Output: {output}")

    input_duration = get_audio_duration(args.input)
    print(f"Input duration: {input_duration:.1f}s")

    if convert_audio(args.input, output, args.start, args.duration):
        output_duration = get_audio_duration(output)
        print(f"Output duration: {output_duration:.1f}s")
        print(f"Format: WAV, {SAMPLE_RATE} Hz, mono")

        if output_duration < 6:
            print("Warning: Audio is shorter than 6 seconds. Quality may suffer.")
        elif output_duration > 30:
            print("Warning: Audio is longer than 30 seconds. Consider trimming.")
        else:
            print("Audio is ready for voice cloning!")
    else:
        print("Error: Conversion failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
