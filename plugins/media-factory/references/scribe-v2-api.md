# Scribe V2 — Speech-to-Text API Reference

ElevenLabs Scribe V2 via fal.ai. Blazingly fast speech-to-text with speaker diarization, audio event tagging, and word-level timestamps.

## Endpoint

`fal-ai/elevenlabs/speech-to-text/scribe-v2`

## Pricing

- **$0.008 per minute** of input audio
- **+30%** if `keyterms` are used

## Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `audio_url` | string | yes | — | URL of audio file to transcribe |
| `language_code` | string | no | auto-detect | Language code: `eng`, `fra`, `spa`, `deu`, `jpn`, etc. |
| `diarize` | boolean | no | `true` | Annotate speaker identity |
| `tag_audio_events` | boolean | no | `true` | Tag events: laughter, applause, music, etc. |
| `keyterms` | list[string] | no | `[]` | Bias terms (up to 100, max 50 chars each). Adds 30% cost. |

## Output Schema

```json
{
  "text": "Full transcribed text as a single string",
  "language_code": "eng",
  "language_probability": 0.98,
  "words": [
    {
      "text": "Hello,",
      "type": "word",
      "start": 0.079,
      "end": 0.539,
      "speaker_id": "speaker_0"
    },
    {
      "text": " ",
      "type": "spacing",
      "start": 0.539,
      "end": 0.599,
      "speaker_id": "speaker_0"
    }
  ]
}
```

### Word Types

| `type` | Meaning |
|--------|---------|
| `word` | Spoken word with timestamps |
| `spacing` | Whitespace between words |
| `audio_event` | Non-speech event (e.g. `(laughter)`, `(applause)`) |

### Speaker IDs

When `diarize: true`, each word has a `speaker_id` field (`speaker_0`, `speaker_1`, ...). Speakers are numbered in order of first appearance.

## Language Codes

Common codes: `eng` (English), `fra` (French), `spa` (Spanish), `deu` (German), `ita` (Italian), `por` (Portuguese), `jpn` (Japanese), `zho` (Chinese), `kor` (Korean), `ara` (Arabic), `hin` (Hindi), `rus` (Russian), `nld` (Dutch), `pol` (Polish), `tur` (Turkish), `swe` (Swedish).

When omitted, the language is auto-detected and returned in `language_code` with confidence in `language_probability`.
