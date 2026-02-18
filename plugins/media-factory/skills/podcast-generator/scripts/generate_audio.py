#!/usr/bin/env python3
"""Generate podcast audio using Google Gemini TTS.

Reads a dialog transcript (with director's notes) and produces a WAV file
using the Gemini multi-speaker text-to-speech API.
"""

import argparse
import base64
import json
import os
import re
import sys
import wave
from pathlib import Path


DEFAULT_MODEL = "gemini-2.5-pro-preview-tts"
DEFAULT_ATHENA_VOICE = "Autonoe"
DEFAULT_GIZMO_VOICE = "Achird"

MAX_TRANSCRIPT_WORDS = 1200  # 1200 words ≈ 437s (~7.3 min), safe under Gemini's ~11 min ceiling
TRANSCRIPT_MARKER = "### TRANSCRIPT"


def save_wav(filename, pcm_data, channels=1, rate=24000, sample_width=2):
    """Write raw PCM data to a WAV file."""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)


def resolve_credentials():
    """Resolve Gemini API key and optional gateway URL/token.

    Checks scripts/credentials.json first, then falls back to environment
    variables. Returns {"api_key": str|None, "gateway_url": str, "gateway_token": str}.
    """
    api_key = None
    gateway_url = ""
    gateway_token = ""

    # Check credentials.json next to this script
    creds_path = Path(__file__).parent / "credentials.json"
    if creds_path.is_file():
        with open(creds_path, "r", encoding="utf-8") as f:
            creds = json.load(f)
        key = creds.get("gemini_api_key", "")
        if key and key != "YOUR_GEMINI_API_KEY_HERE":
            api_key = key
        gateway_url = creds.get("gateway_url", "")
        gateway_token = creds.get("gateway_token", "")

    # Fall back to environment variables
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")
    if not gateway_url:
        gateway_url = os.environ.get("AI_GATEWAY_URL", "")
    if not gateway_token:
        gateway_token = os.environ.get("AI_GATEWAY_TOKEN", "")

    return {"api_key": api_key, "gateway_url": gateway_url, "gateway_token": gateway_token}


def _preflight():
    """Check dependencies and API key. Returns (genai, types, creds_dict)."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print(
            "Error: 'google-genai' is not installed. Run: uv pip install google-genai pypdf",
            file=sys.stderr,
        )
        sys.exit(1)

    creds = resolve_credentials()
    if not creds["api_key"]:
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

    return genai, types, creds


def _apply_hint(preamble, hint):
    """Append a continuation note to the preamble when a BREAK hint is present."""
    if hint:
        return preamble + f"\n\n> Continuation note: {hint}"
    return preamble


# Regex for ### BREAK with optional [hint text]
_BREAK_RE = re.compile(r"^\s*###\s+BREAK(?:\s+\[([^\]]*)\])?\s*$", re.MULTILINE)


def split_dialog(text):
    """Split dialog at Claude-authored ### BREAK markers.

    Returns a list of complete dialog texts (preamble + transcript chunk).
    If the transcript exceeds MAX_TRANSCRIPT_WORDS and has no BREAK markers,
    the function raises SystemExit with a message asking Claude to add them.
    """
    # Find the transcript marker
    match = re.search(r"(?i)^(###\s+TRANSCRIPT)\s*$", text, re.MULTILINE)
    if not match:
        return [text]

    marker_end = match.end()
    preamble = text[:marker_end]
    transcript_body = text[marker_end:]

    word_count = len(transcript_body.split())
    has_breaks = bool(_BREAK_RE.search(transcript_body))

    # Happy path: short transcript, no breaks needed
    if word_count <= MAX_TRANSCRIPT_WORDS and not has_breaks:
        return [text]

    # Has BREAK markers — split at them
    if has_breaks:
        segments = _BREAK_RE.split(transcript_body)
        # _BREAK_RE.split produces [text0, hint0, text1, hint1, ..., textN]
        # where hintN is the captured group (None if no hint)
        chunks = []
        for i in range(0, len(segments), 2):
            segment_text = segments[i].strip()
            if not segment_text:
                continue
            # Hint precedes this segment (from the BREAK before it)
            hint = segments[i - 1] if i > 0 and segments[i - 1] else None
            chunk_preamble = _apply_hint(preamble, hint)
            seg_words = len(segment_text.split())
            if seg_words > MAX_TRANSCRIPT_WORDS:
                print(
                    f"Warning: Segment {len(chunks) + 1} is {seg_words} words "
                    f"(limit: {MAX_TRANSCRIPT_WORDS}). Consider adding another "
                    f"### BREAK within this segment.",
                    file=sys.stderr,
                )
            chunks.append(chunk_preamble + "\n\n" + segment_text)
        return chunks

    # No BREAK markers but transcript is too long — error
    print(
        f"Error: Transcript is {word_count} words "
        f"(limit: {MAX_TRANSCRIPT_WORDS} per chunk).\n"
        f"Add ### BREAK markers at natural narrative transitions to split "
        f"into segments of 800-1200 words.\n"
        f"Example:  ### BREAK\n"
        f"          ### BREAK [The conversation deepens — more reflective pacing]",
        file=sys.stderr,
    )
    sys.exit(1)


def generate_audio_single(text, model=None, athena_voice=None, gizmo_voice=None):
    """Call Gemini TTS and return raw PCM audio bytes (single API call)."""
    genai, types, creds = _preflight()

    model = model or DEFAULT_MODEL
    athena_voice = athena_voice or DEFAULT_ATHENA_VOICE
    gizmo_voice = gizmo_voice or DEFAULT_GIZMO_VOICE

    client_kwargs = {"api_key": creds["api_key"]}
    if creds["gateway_url"]:
        http_opts = {"base_url": creds["gateway_url"]}
        if creds["gateway_token"]:
            http_opts["headers"] = {
                "cf-aig-authorization": f"Bearer {creds['gateway_token']}"
            }
        client_kwargs["http_options"] = types.HttpOptions(**http_opts)
    client = genai.Client(**client_kwargs)

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
    sys.stdout.reconfigure(line_buffering=True)

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
