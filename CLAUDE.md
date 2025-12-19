# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fine-tuning Coqui XTTS-v2 model for Russian speech synthesis (TTS).

## Technology Stack

- **Base Model**: coqui/XTTS-v2 (multilingual TTS with voice cloning)
- **Framework**: Coqui TTS (https://github.com/coqui-ai/TTS)
- **Language**: Python 3.10+
- **GPU**: CUDA required for training

## Common Commands

```bash
# Install dependencies
pip install TTS

# Download base model
tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 --list_speaker_idxs

# Run inference with base model
tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 \
    --text "Привет, мир!" \
    --language_idx ru \
    --speaker_wav speaker.wav \
    --out_path output.wav

# Fine-tuning (typical command structure)
python train.py --config config.json --restore_path <xtts_checkpoint>
```

## Dataset Requirements

- Audio: WAV format, 22050 Hz sample rate, mono
- Transcriptions: Text files with corresponding audio transcripts
- Recommended: LJSpeech-style format or Coqui TTS metadata format

## Scripts

### prepare_audio.py
Prepare audio files for voice cloning (convert to WAV 22050 Hz mono).

```bash
# Basic conversion
python scripts/prepare_audio.py input.mp3

# Trim to specific segment (start at 10s, duration 15s)
python scripts/prepare_audio.py input.mp3 -s 10 -d 15

# Custom output path
python scripts/prepare_audio.py input.mp3 -o data/speaker.wav
```

## Project Structure

```
tts/
├── data/           # Training datasets and speaker samples
├── configs/        # Training configurations
├── scripts/        # Data preprocessing and utility scripts
│   └── prepare_audio.py
├── checkpoints/    # Model checkpoints
└── outputs/        # Generated audio samples
```
