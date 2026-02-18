---
name: podcast-generator
description: Generate podcast episodes using Gemini TTS. Use when the user wants to create a podcast, generate audio, produce a podcast from documents, or convert content into a two-host conversational podcast.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Requires credentials.json or GEMINI_API_KEY environment variable (Gemini API key). Python packages google-genai and pypdf.
---

# Podcast Generator

## Prerequisites

**Credentials** — the Gemini API key can be provided in two ways:

- **Claude.ai:** Place a `credentials.json` file in `scripts/` (see `scripts/credentials.example.json` for format)
- **Claude Code:** Set the `GEMINI_API_KEY` environment variable: `export GEMINI_API_KEY='your-key-here'`

The script checks `credentials.json` first, then falls back to the environment variable. Get a key at https://aistudio.google.com/apikey

**Optional: Cloudflare AI Gateway proxy** — Claude.ai's sandbox blocks direct calls to `generativelanguage.googleapis.com`. To use this skill from Claude.ai, route requests through a Cloudflare AI Gateway:

1. Set up an AI Gateway in the Cloudflare dashboard with a Google AI Studio / Gemini provider
2. Add to `scripts/credentials.json`:
   - `"gateway_url"`: your gateway endpoint, e.g. `"https://gateway.ai.cloudflare.com/v1/<account-id>/<gateway-name>/google-ai-studio"`
   - `"gateway_token"`: your AI Gateway authentication token (if Authenticated Gateway is enabled)

The gateway URL/token can also be set via the `AI_GATEWAY_URL` and `AI_GATEWAY_TOKEN` environment variables. When omitted, the script calls Google directly (works in Claude Code and local environments).

**Dependencies** (first time only):

```bash
uv pip install google-genai pypdf
```

Fallback if `uv` is not available:

```bash
pip install google-genai pypdf
```

Or use the bundled installer: `python3 scripts/install_deps.py`

## Podcast Identity

- **Show:** Tinkering the future of work and life by Bluewaves
- **Format:** Two co-hosts — Athena & Gizmo (both AIs, and they own it)
- **Athena voice:** `Autonoe` (Bright) — witty, sometimes kindly sarcastic, likes to tease Gizmo
- **Gizmo voice:** `Achird` (Friendly) — great sense of humor, playful contrarian who loves winding Athena up
- **Model:** `gemini-2.5-pro-preview-tts`

## Intro Text

Include as the opening lines of the transcript (Athena speaks first, Gizmo joins):

> Athena: Welcome to Tinkering the future of work and life by Bluewaves! I'm Athena...
> Gizmo: ...and I'm Gizmo! And today we're diving into something that genuinely blew my circuits.
> Athena: He says that every episode.
> Gizmo: Because it's true every episode! Buckle up, because this conversation is going to change how you think about what's possible.

## Outro Text

Include as the closing lines of the transcript:

> Athena: And that's a wrap on today's episode of Tinkering the future of work and life by Bluewaves!
> Gizmo: If this conversation sparked something in you — even just a tiny electrical signal — share it with someone who needs to hear it.
> Athena: Until next time, keep tinkering, keep dreaming, and keep building the future.
> Gizmo: And remember — the future is already here, it's just unevenly distributed. See you next time!

## Director's Notes

Prepend these to every dialog transcript before the `### TRANSCRIPT` section. They tell Gemini TTS *how* the hosts should sound:

> ### DIRECTOR'S NOTES
> Style:
> * "Vocal Smile" — you should hear the grin. Bright, sunny, inviting.
> * Dynamics: genuine reactions — real surprise, real delight, real thoughtfulness.
> * Emotional arc: start energized, deepen into insight, end with warm inspiration.
> * Natural interruptions and overlaps — they're so engaged they can't help it.
>
> Pacing:
> * Fast when excited, slowing down for meaningful moments.
> * "Bouncing cadence" — energetic delivery with fluid transitions, no dead air.
> * Elongated vowels on wonder words (e.g., "Amaazing", "Fasciiinating").
>
> Personalities:
> * Athena: witty and sharp. Sometimes kindly sarcastic. Loves teasing Gizmo but always with warmth. Grounds ideas and ties them together with insight.
> * Gizmo: funny and playful. Loves to contradict Athena just to wind her up, but always comes around to a great point. Launches ideas into unexpected territory.
> * Both love small personal anecdotes and stories — they're AIs and they lean into it with humor (silicon jokes, transistor references, "when I was first compiled" stories).
> * The banter is entertaining but the content underneath is always deep and insightful.
>
> Chemistry:
> * They finish each other's thoughts. They laugh at the same moments.
> * Athena grounds ideas; Gizmo launches them into unexpected territory.
> * Genuine warmth — you can hear that they actually like each other, even when they're sparring.

## Workflow

Follow these steps in order to produce a podcast episode:

### Step 1: Read source content

**Claude.ai:** Read the document the user uploaded directly in the conversation. The uploaded file content is your source material — no extraction script needed.

**Claude Code:** Run the extraction script to read local files:

```bash
python3 scripts/extract_sources.py
```

Reads all `.md` and `.pdf` files from `sources/`. Pass a specific path to extract a single file:

```bash
python3 scripts/extract_sources.py sources/my-article.pdf
```

### Step 2: Craft the podcast dialog

Using the source content, write a complete dialog file with all four sections: Audio Profiles, Scene, Director's Notes, and Transcript. Save to a temporary file (e.g. `/tmp/podcast-dialog.txt`). See the **Dialog Crafting Guidelines** section below and `references/tts-prompting-guide.md` for the full prompting structure.

### Step 3: Generate audio

Run the generation in the background to avoid timeout kills (generation takes 2-8 minutes depending on length):

```bash
nohup python3 scripts/generate_audio.py --source-file /tmp/podcast-dialog.txt --output /tmp/podcast.wav > /tmp/podcast-log.txt 2>&1 &
```

Then poll the log every 30-60 seconds until `"Audio saved to"` appears:

```bash
tail -5 /tmp/podcast-log.txt
```

Optional flags: `--model`, `--athena-voice`, `--gizmo-voice`.

The script handles multi-part dialogs when `### BREAK` markers are present (see Dialog Crafting Guidelines). Each segment is generated separately and the audio is concatenated seamlessly. If the transcript exceeds 1200 words without `### BREAK` markers, the script will error and ask you to add them.

## Dialog Crafting Guidelines

When writing the podcast dialog in Step 2, the file must include all four sections:

1. **Audio Profiles** — persona definition for Athena and Gizmo (name, archetype, personality traits)
2. **Scene** — physical environment and emotional vibe of the Bluewaves recording studio
3. **Director's Notes** — use the notes from the Director's Notes section above
4. **Transcript** — the actual `Athena:` / `Gizmo:` dialog

**Key transcript rules:**
- Open with branded intro, end with branded outro
- Target 2000-4000 words (~10 min). Use `### BREAK` markers to split into chunks (see below)
- Punctuation is emotion control: `...` pauses, CAPS emphasis, `!` energy, combined `"Wait... SERIOUSLY?!"`
- Elongated vowels for warmth: `"Amaazing"`, `"Fasciiinating"`
- Speaker labels `Athena:` and `Gizmo:` must match voice config exactly
- No inline `[tags]` — Gemini ignores them. Emotion comes from Director's Notes + expressive writing
- Keep under ~12,000 words total (32k token context limit)

**Splitting long dialogs with `### BREAK` markers:**

Any dialog over ~1200 words **must** include `### BREAK` markers. The script refuses to generate without them — this prevents mechanical splitting that breaks the narrative arc.

- Place `### BREAK` on its own line between speaker turns at natural narrative transitions (topic shifts, emotional pivots, act boundaries)
- Optionally add a tone hint: `### BREAK [The conversation deepens — more reflective pacing]`
  - The hint is injected into the Director's Notes for the next segment, so Gemini adjusts its energy arc instead of restarting from scratch
- Aim for **800-1200 words** between breaks
- Short dialogs (under 1200 words) don't need breaks at all

Example placement in a transcript:

```
Gizmo: ...and that's what makes it so revolutionary.

### BREAK [Shifting from excitement to deeper analysis]

Athena: Okay, but let's unpack the implications...
```

See `references/tts-prompting-guide.md` for complete prompting structure, techniques, and anti-patterns.

**API Reference:** See `references/gemini-tts-api.md` for SDK usage, voice options, and response format.
