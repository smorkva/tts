#!/usr/bin/env python3
"""
TTS Server using XTTS-v2 voice cloning.

Usage:
    python scripts/server.py

API:
    POST /synthesize
    {
        "text": "Текст для синтеза",
        "speaker": "speaker.wav",  # filename in data/ folder
        "language": "ru"  # optional, default: ru
    }
    Returns: audio/wav file
"""

import io
import wave
from pathlib import Path

import numpy as np
import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from TTS.api import TTS

# Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"

app = FastAPI(title="XTTS-v2 TTS Server")

# Global model instance
tts_model: TTS = None


class SynthesizeRequest(BaseModel):
    text: str
    speaker: str = "speaker.wav"
    language: str = "ru"


@app.on_event("startup")
async def load_model():
    """Load TTS model on startup."""
    global tts_model

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading XTTS-v2 model on {device}...")

    tts_model = TTS(MODEL_NAME, gpu=False)
    tts_model.to(device)

    print(f"Model loaded successfully on {device}")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "model_loaded": tts_model is not None,
        "device": str(next(tts_model.synthesizer.tts_model.parameters()).device) if tts_model else None
    }


@app.get("/speakers")
async def list_speakers():
    """List available speaker samples."""
    speakers = []
    for ext in ["*.wav", "*.mp3", "*.opus", "*.flac"]:
        speakers.extend([f.name for f in DATA_DIR.glob(ext)])
    return {"speakers": speakers}


@app.post("/synthesize")
async def synthesize(request: SynthesizeRequest):
    """Synthesize speech from text."""
    if tts_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Find speaker file
    speaker_path = DATA_DIR / request.speaker
    if not speaker_path.exists():
        # Try subdirectories
        matches = list(DATA_DIR.glob(f"**/{request.speaker}"))
        if matches:
            speaker_path = matches[0]
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Speaker file not found: {request.speaker}"
            )

    # Synthesize to memory buffer
    wav = tts_model.tts(
        text=request.text,
        speaker_wav=str(speaker_path),
        language=request.language
    )

    # Convert to WAV bytes
    buffer = io.BytesIO()
    wav_np = np.array(wav, dtype=np.float32)
    wav_int16 = (wav_np * 32767).astype(np.int16)

    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(22050)
        wf.writeframes(wav_int16.tobytes())

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=output.wav"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
