#!/usr/bin/env python3
"""
Synthesize speech using XTTS-v2 voice cloning.

Usage:
    python scripts/synthesize.py "Привет, как дела?" -o output.wav
    python scripts/synthesize.py "Текст для синтеза" --speaker data/speaker.wav -o output.wav
"""

import argparse
from pathlib import Path

import torch
from TTS.api import TTS


def main():
    parser = argparse.ArgumentParser(description="Synthesize speech with XTTS-v2")
    parser.add_argument("text", help="Text to synthesize")
    parser.add_argument(
        "-s", "--speaker",
        default="data/speaker.wav",
        help="Path to speaker reference audio (default: data/speaker.wav)"
    )
    parser.add_argument(
        "-o", "--output",
        default="outputs/output.wav",
        help="Output path (default: outputs/output.wav)"
    )
    parser.add_argument(
        "-l", "--language",
        default="ru",
        help="Language code (default: ru)"
    )
    args = parser.parse_args()

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Check speaker file exists
    speaker_path = Path(args.speaker)
    if not speaker_path.exists():
        print(f"Error: Speaker file not found: {args.speaker}")
        return 1

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading XTTS-v2 model on {device}...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False).to(device)

    print(f"Synthesizing: {args.text[:50]}...")
    tts.tts_to_file(
        text=args.text,
        file_path=str(output_path),
        speaker_wav=str(speaker_path),
        language=args.language
    )

    print(f"Saved to: {args.output}")
    return 0


if __name__ == "__main__":
    exit(main())
