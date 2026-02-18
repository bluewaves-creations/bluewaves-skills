#!/usr/bin/env python3
"""Generate podcast audio using Google Gemini TTS.

Reads a dialog transcript (with director's notes) and produces a WAV file
using the Gemini multi-speaker text-to-speech API.
"""

import argparse
import base64
import json
import os
import sys
import wave
from pathlib import Path


DEFAULT_MODEL = "gemini-2.5-pro-preview-tts"
DEFAULT_ATHENA_VOICE = "Autonoe"
DEFAULT_GIZMO_VOICE = "Achird"

MAX_TRANSCRIPT_WORDS = 1800  # safe limit per chunk (~8 min audio)
TRANSCRIPT_MARKER = "### TRANSCRIPT"


def save_wav(filename, pcm_data, channels=1, rate=24000, sample_width=2):
    """Write raw PCM data to a WAV file."""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)


def resolve_credentials():
    """Resolve Gemini API key from credentials.json or environment variable.

    Checks scripts/credentials.json first, then falls back to GEMINI_API_KEY
    environment variable. Returns the API key or None if not found.
    """
    # Check credentials.json next to this script
    creds_path = Path(__file__).parent / "credentials.json"
    if creds_path.is_file():
        with open(creds_path, "r", encoding="utf-8") as f:
            creds = json.load(f)
        key = creds.get("gemini_api_key", "")
        if key and key != "YOUR_GEMINI_API_KEY_HERE":
            return key

    # Fall back to environment variable
    return os.environ.get("GEMINI_API_KEY")


def _preflight():
    """Check dependencies and API key. Returns (genai, types, api_key)."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print(
            "Error: 'google-genai' is not installed. Run: uv pip install google-genai pypdf",
            file=sys.stderr,
        )
        sys.exit(1)

    api_key = resolve_credentials()
    if not api_key:
        print(
            "Error: Gemini API key not found.\n"
            "Option 1: Create scripts/credentials.json with your key\n"
            "          (see scripts/credentials.example.json)\n"
            "Option 2: Set the GEMINI_API_KEY environment variable\n"
            "          export GEMINI_API_KEY='your-key-here'\n"
            "Get a key at https://aistudio.google.com/apikey",
            file=sys.stderr,
        )
        sys.exit(1)

    return genai, types, api_key


def split_dialog(text):
    """Split a long dialog into chunks that stay under the TTS output limit.

    Returns a list of complete dialog texts (preamble + transcript chunk).
    Short dialogs or those without a transcript marker return as a single chunk.
    """
    import re

    # Find the transcript marker (case-insensitive)
    match = re.search(r"(?i)^(###\s+TRANSCRIPT)\s*$", text, re.MULTILINE)
    if not match:
        return [text]

    marker_end = match.end()
    preamble = text[: marker_end]
    transcript_body = text[marker_end:]

    # Check word count of transcript body
    words = transcript_body.split()
    if len(words) <= MAX_TRANSCRIPT_WORDS:
        return [text]

    # Parse into speaker turns
    lines = transcript_body.strip().splitlines()
    turns = []  # list of (list of lines) per turn
    for line in lines:
        if re.match(r"^(Athena|Gizmo)\s*:", line):
            turns.append([line])
        elif turns:
            turns[-1].append(line)
        else:
            # Lines before any speaker turn — treat as first turn
            turns.append([line])

    # Group turns into chunks under the word limit
    chunks = []
    current_lines = []
    current_words = 0
    for turn in turns:
        turn_text = "\n".join(turn)
        turn_words = len(turn_text.split())
        if current_lines and current_words + turn_words > MAX_TRANSCRIPT_WORDS:
            chunk_transcript = "\n".join(current_lines)
            chunks.append(preamble + "\n\n" + chunk_transcript)
            current_lines = list(turn)
            current_words = turn_words
        else:
            current_lines.extend(turn)
            current_words += turn_words

    # Don't forget the last chunk
    if current_lines:
        chunk_transcript = "\n".join(current_lines)
        chunks.append(preamble + "\n\n" + chunk_transcript)

    return chunks


def generate_audio_single(text, model=None, athena_voice=None, gizmo_voice=None):
    """Call Gemini TTS and return raw PCM audio bytes (single API call)."""
    genai, types, api_key = _preflight()

    model = model or DEFAULT_MODEL
    athena_voice = athena_voice or DEFAULT_ATHENA_VOICE
    gizmo_voice = gizmo_voice or DEFAULT_GIZMO_VOICE

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=model,
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker="Athena",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=athena_voice,
                                )
                            ),
                        ),
                        types.SpeakerVoiceConfig(
                            speaker="Gizmo",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=gizmo_voice,
                                )
                            ),
                        ),
                    ]
                )
            ),
        ),
    )

    data = response.candidates[0].content.parts[0].inline_data.data

    # SDK returns base64-encoded PCM; decode it
    if isinstance(data, str):
        return base64.b64decode(data)
    return data


def generate_audio(text, model=None, athena_voice=None, gizmo_voice=None):
    """Generate audio, automatically splitting long dialogs into chunks."""
    chunks = split_dialog(text)

    if len(chunks) == 1:
        return generate_audio_single(text, model=model, athena_voice=athena_voice,
                                     gizmo_voice=gizmo_voice)

    print(f"Dialog exceeds single-call limit, splitting into {len(chunks)} parts...")
    parts = []
    for i, chunk in enumerate(chunks, 1):
        pcm = generate_audio_single(chunk, model=model, athena_voice=athena_voice,
                                    gizmo_voice=gizmo_voice)
        duration = len(pcm) / (24000 * 2)  # 24kHz, 16-bit mono
        print(f"  Part {i}/{len(chunks)} generated ({duration:.0f}s)")
        parts.append(pcm)

    return b"".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="Generate podcast audio using Gemini TTS."
    )
    parser.add_argument(
        "--source-file",
        default=None,
        help="Path to dialog text file (reads from stdin if omitted)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output WAV path (default: output/podcast.wav in current directory)",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Gemini TTS model (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--athena-voice",
        default=DEFAULT_ATHENA_VOICE,
        help=f"Athena's voice name (default: {DEFAULT_ATHENA_VOICE})",
    )
    parser.add_argument(
        "--gizmo-voice",
        default=DEFAULT_GIZMO_VOICE,
        help=f"Gizmo's voice name (default: {DEFAULT_GIZMO_VOICE})",
    )
    args = parser.parse_args()

    # Read dialog text
    if args.source_file:
        if not os.path.isfile(args.source_file):
            print(f"Error: File not found: {args.source_file}", file=sys.stderr)
            sys.exit(1)
        with open(args.source_file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        if sys.stdin.isatty():
            print(
                "Error: No input. Use --source-file or pipe text via stdin.",
                file=sys.stderr,
            )
            sys.exit(1)
        text = sys.stdin.read()

    if not text.strip():
        print("Error: Input text is empty.", file=sys.stderr)
        sys.exit(1)

    # Determine output path (CWD-based default)
    default_output = os.path.join(os.getcwd(), "output", "podcast.wav")
    output_path = args.output or default_output

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # Validate dependencies and API key before starting
    _preflight()

    print(f"Generating audio with {args.model}...")
    print(f"  Athena voice: {args.athena_voice}")
    print(f"  Gizmo voice:  {args.gizmo_voice}")

    pcm_data = generate_audio(
        text,
        model=args.model,
        athena_voice=args.athena_voice,
        gizmo_voice=args.gizmo_voice,
    )

    save_wav(output_path, pcm_data)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"Audio saved to {output_path} ({size_kb:.1f} KB)")
    print(output_path)


if __name__ == "__main__":
    main()
