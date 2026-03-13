---
name: audio-transcriber
description: >
  Transcribe audio or video files to text using fal.ai Scribe V2. Use when the user
  wants to transcribe, get a transcript, do speech to text, extract text from audio
  or video, or generate subtitles/SRT from a recording.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Requires credentials.json or FAL_KEY environment variable (fal.ai API key), fal-client Python package
---

# Audio Transcriber

Transcribe audio and video files to text using ElevenLabs Scribe V2 via fal.ai. Supports speaker diarization, audio event tagging, word-level timestamps, and multiple output formats.

See `references/fal-api.md` for setup, Python patterns, and error handling.
See `references/scribe-v2-api.md` for input/output schema details and language codes.

## API Endpoint

`fal-ai/elevenlabs/speech-to-text/scribe-v2`

## Parameters

### Required
- `audio_url` (string): URL of the audio/video file to transcribe (use `fal_client.upload_file()` for local files)

### Optional
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `language_code` | string | auto-detect | Language code (`eng`, `fra`, `spa`, `deu`, `jpn`, etc.) |
| `diarize` | boolean | true | Annotate who is speaking |
| `tag_audio_events` | boolean | true | Tag laughter, applause, music, etc. |
| `keyterms` | list[string] | [] | Bias terms for domain-specific vocabulary (adds 30% cost) |

## CLI Script

### Markdown transcript (default)

Speaker-labeled sections with timestamps, language/confidence header:

```bash
python3 scripts/fal_generate.py \
    --endpoint transcribe \
    --audio /path/to/recording.m4a \
    --language fra \
    --transcript-format markdown \
    --output transcript.md
```

### Plain text

Raw transcribed text only:

```bash
python3 scripts/fal_generate.py \
    --endpoint transcribe \
    --audio /path/to/recording.m4a \
    --transcript-format plain \
    --output transcript.txt
```

### SRT subtitles

SubRip subtitle format grouped by speaker and pauses:

```bash
python3 scripts/fal_generate.py \
    --endpoint transcribe \
    --audio /path/to/recording.m4a \
    --transcript-format srt \
    --output subtitles.srt
```

### With domain-specific bias terms

```bash
python3 scripts/fal_generate.py \
    --endpoint transcribe \
    --audio /path/to/meeting.mp3 \
    --language eng \
    --keyterms "Kubernetes" "PostgreSQL" "microservices" \
    --transcript-format markdown \
    --output meeting-notes.md
```

## Tips

- Specify `--language` when known for better accuracy and faster processing
- Use `--keyterms` for domain-specific vocabulary (legal, medical, technical) — adds 30% cost
- Speaker diarization is on by default; disable with `--no-diarize` for single-speaker recordings
- Audio event tagging catches laughter, applause, music — disable with `--no-tag-events` if not needed
- Supports all audio/video formats that fal.ai accepts (mp3, m4a, wav, mp4, etc.)
- Markdown format is best for meeting notes and interviews; SRT for subtitles; plain for downstream processing
- Pricing: $0.008 per minute of audio (very affordable — a 1-hour recording costs ~$0.48)
