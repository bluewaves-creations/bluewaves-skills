# Gemini TTS API Reference

## Authentication

Set the `GEMINI_API_KEY` environment variable. The `google-genai` SDK reads it automatically when using `genai.Client(api_key=...)`.

```bash
export GEMINI_API_KEY='your-key-here'
```

Get a key at https://aistudio.google.com/apikey

## Generate Audio

Use `client.models.generate_content()` with `response_modalities=["AUDIO"]`.

### Single-Speaker

```python
from google import genai
from google.genai import types

client = genai.Client(api_key="...")

response = client.models.generate_content(
    model="gemini-2.5-flash-preview-tts",
    contents="Say cheerfully: Have a wonderful day!",
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Kore",
                )
            )
        ),
    ),
)
```

### Multi-Speaker

Use `MultiSpeakerVoiceConfig` with up to 2 speakers. Speaker names in the config **must match** the speaker labels in the transcript text.

```python
response = client.models.generate_content(
    model="gemini-2.5-pro-preview-tts",
    contents=transcript_text,
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker="Athena",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Autonoe",
                            )
                        ),
                    ),
                    types.SpeakerVoiceConfig(
                        speaker="Gizmo",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Achird",
                            )
                        ),
                    ),
                ]
            )
        ),
    ),
)
```

### Config Type Hierarchy

```
GenerateContentConfig
  response_modalities: ["AUDIO"]
  speech_config: SpeechConfig
    voice_config: VoiceConfig                    # single-speaker
      prebuilt_voice_config: PrebuiltVoiceConfig
        voice_name: str
    multi_speaker_voice_config: MultiSpeakerVoiceConfig  # multi-speaker
      speaker_voice_configs: list[SpeakerVoiceConfig]
        speaker: str                             # must match transcript labels
        voice_config: VoiceConfig
```

## Response Format

Audio data is at `response.candidates[0].content.parts[0].inline_data.data`.

The SDK returns base64-encoded raw PCM audio:
- Format: signed 16-bit little-endian (s16le)
- Sample rate: 24000 Hz
- Channels: 1 (mono)

### Saving as WAV

```python
import base64
import wave

data = response.candidates[0].content.parts[0].inline_data.data
pcm = base64.b64decode(data) if isinstance(data, str) else data

with wave.open("output.wav", "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)       # 16-bit = 2 bytes
    wf.setframerate(24000)
    wf.writeframes(pcm)
```

## Voice Options

30 prebuilt voices available in the `voice_name` field:

| Voice | Style | Voice | Style | Voice | Style |
|-------|-------|-------|-------|-------|-------|
| Zephyr | Bright | Puck | Upbeat | Charon | Informative |
| Kore | Firm | Fenrir | Excitable | Leda | Youthful |
| Orus | Firm | Aoede | Breezy | Callirrhoe | Easy-going |
| Autonoe | Bright | Enceladus | Breathy | Iapetus | Clear |
| Umbriel | Easy-going | Algieba | Smooth | Despina | Smooth |
| Erinome | Clear | Algenib | Gravelly | Rasalgethi | Informative |
| Laomedeia | Upbeat | Achernar | Soft | Alnilam | Firm |
| Schedar | Even | Gacrux | Mature | Pulcherrima | Forward |
| Achird | Friendly | Zubenelgenubi | Casual | Vindemiatrix | Gentle |
| Sadachbia | Lively | Sadaltager | Knowledgeable | Sulafat | Warm |

Preview voices at https://aistudio.google.com/generate-speech

## Supported Models

| Model | Single Speaker | Multi-Speaker |
|-------|---------------|---------------|
| `gemini-2.5-flash-preview-tts` | Yes | Yes |
| `gemini-2.5-pro-preview-tts` | Yes | Yes |

## Limitations

- **Text-only input, audio-only output** — no images, video, or other modalities
- **32k token context window** (~16k words) — keep dialog + director's notes under ~12k words
- **Max 2 speakers** in multi-speaker mode
- Speaker names in `SpeakerVoiceConfig` must exactly match transcript labels
