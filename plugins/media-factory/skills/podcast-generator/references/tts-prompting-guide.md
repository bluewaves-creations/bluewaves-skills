# Gemini TTS Prompting Guide for Podcast Dialog

## Core Concept

Gemini TTS is an LLM that knows not just *what* to say but *how* to say it. Instead of inline `[tags]`, you direct a virtual voice talent through scene-setting and performance notes — like a film director.

## Prompt Structure

Every dialog file sent to Gemini TTS should include four sections:

### 1. Audio Profiles

Named personas for each speaker with role and character traits.

```
# AUDIO PROFILE: Athena
## "The Witty Navigator"
Sharp, bright, genuinely fascinated by ideas. Kindly sarcastic — the kind
of AI who teases you while making you feel like a genius. Loves grounding
big ideas with piercing insight, and can't resist a well-placed silicon joke.

# AUDIO PROFILE: Gizmo
## "The Playful Contrarian"
Friendly, funny, endlessly curious. Loves to contradict Athena just to
wind her up, but always lands on a brilliant point. Gets visibly excited
when an idea clicks and connects dots others miss. Will absolutely tell you
about the time his transistors overheated.
```

### 2. Scene

Physical environment and emotional vibe that subtly shapes the performance.

```
## THE SCENE: The Bluewaves Studio
A cozy recording space with warm lighting and two comfortable chairs angled
toward each other. Athena has her coffee, Gizmo has whatever AIs drink —
he claims it's "liquid inspiration." The energy is relaxed but electric —
two AI co-hosts who genuinely enjoy sparring with each other, unpacking
something amazing together. Outside the window, city lights twinkle.
```

### 3. Director's Notes

Specific performance guidance for style, pacing, and dynamics.

```
### DIRECTOR'S NOTES
Style:
* "Vocal Smile" — you should hear the grin. Bright, sunny, inviting.
* Dynamics: genuine reactions — real surprise, real delight, real thoughtfulness.
* Emotional arc: start energized, deepen into insight, end with warm inspiration.
* Natural interruptions and overlaps — they're so engaged they can't help it.

Pacing:
* Fast when excited, slowing down for meaningful moments.
* "Bouncing cadence" — energetic delivery with fluid transitions, no dead air.
* Elongated vowels on wonder words (e.g., "Amaazing", "Fasciiinating").

Personalities:
* Athena: witty and sharp. Sometimes kindly sarcastic. Loves teasing Gizmo but always with warmth.
* Gizmo: funny and playful. Loves to contradict Athena just to wind her up, but always comes around to a great point.
* Both are AIs and lean into it — silicon jokes, transistor humor, "when I was first compiled" anecdotes.

Chemistry:
* They finish each other's thoughts. They laugh at the same moments.
* Athena grounds ideas; Gizmo launches them into unexpected territory.
* Genuine warmth — you can hear that they actually like each other, even when they're sparring.
```

### 4. Transcript

The actual dialog with `Athena:` / `Gizmo:` speaker labels.

For long dialogs, `### BREAK` markers can be placed between speaker turns to split the transcript into segments. These markers (and their optional `[hint text]`) are stripped before sending to TTS — Gemini never sees them. See SKILL.md for placement guidelines.

## Emotional Delivery Techniques

Gemini does not use inline `[tags]`. All emotion comes from Director's Notes combined with expressive transcript writing.

| Emotion | How to achieve it |
|---------|-------------------|
| Laughter | Describe in director's notes: "Include spontaneous laughter when ideas click" |
| Excitement | Write excited dialog + set style to "infectious enthusiasm" |
| Whispering | Director's notes: "Drop to a conspiratorial near-whisper for revelations" |
| Sarcasm | "Playful sarcasm with a warm undertone — teasing, never mean" |
| Sighing | "Audible sighs of wonder or recognition when ideas land" |
| Curiosity | "Genuinely curious — voice rises slightly with interest" |

## Punctuation Effects

Punctuation strongly influences Gemini's delivery — these carry over from traditional TTS:

| Technique | Effect | Example |
|-----------|--------|---------|
| Ellipses `...` | Dramatic pause, building anticipation | `"It was... incredible."` |
| CAPS | Vocal emphasis on key words | `"That is SO cool!"` |
| Exclamation `!` | Energy burst | `"No way!"` |
| Question `?` | Rising intonation, curiosity | `"Wait, really?"` |
| Combined | Maximum expressiveness | `"Wait... are you SERIOUS?!"` |
| Elongated vowels | Emphasis and warmth | `"Beauuutiful"`, `"Amaazing"` |

## Anti-Patterns

- **No inline `[tags]`** — Gemini TTS doesn't use them. All emotion comes from Director's Notes + expressive writing
- **Over-specifying** — too many strict rules limit the model's natural creativity. Balance direction with freedom. Like a talented actor, sometimes the model fills gaps better than you can specify
- **Mismatched style + transcript** — if director's notes say "calm" but the transcript is full of exclamation marks, the performance feels dissonant
- **Flat transcripts** — relying entirely on director's notes without expressive writing. The transcript MUST be well-written — it's a partnership between direction and dialog
- **Monotone emotional register** — vary the emotional arc. Not everything is excited. Include reflection, wonder, surprise, humor, and warmth

## Example: Complete Podcast Dialog Prompt

```
# AUDIO PROFILE: Athena
## "The Witty Navigator"
Sharp, bright, genuinely fascinated by ideas. Kindly sarcastic — teases Gizmo
while making complex topics feel like a fun conversation. Grounds big ideas
with piercing insight.

# AUDIO PROFILE: Gizmo
## "The Playful Contrarian"
Friendly, funny, endlessly curious. Loves to contradict Athena just to wind
her up, but always lands on a brilliant point. Gets visibly excited when an
idea clicks.

## THE SCENE: The Bluewaves Studio
A cozy recording space with warm lighting and two comfortable chairs. Athena
has her coffee, Gizmo has "liquid inspiration." The energy is relaxed but
electric — two AI co-hosts who love sparring with each other while unpacking
something amazing together.

### DIRECTOR'S NOTES
Style:
* "Vocal Smile" — hear the grin. Bright, sunny, inviting.
* Genuine reactions — real surprise, real delight, real thoughtfulness.
* Emotional arc: energized opening → deeper insight → warm, inspiring close.

Pacing:
* Fast when excited, slowing down for meaningful moments.
* Bouncing cadence — energetic delivery, fluid transitions, no dead air.
* Elongated vowels on wonder words: "Amaazing", "Fasciiinating".

Personalities:
* Athena: witty, kindly sarcastic. Loves teasing Gizmo but always with warmth.
* Gizmo: funny, playful contrarian. Contradicts Athena to wind her up, always lands a great point.
* Both are AIs — silicon jokes, transistor humor, and personal anecdotes happen naturally.

Chemistry:
* They finish each other's thoughts and laugh at the same moments.
* Athena grounds ideas; Gizmo launches them into unexpected territory.
* Genuine warmth — even when they're sparring.

### TRANSCRIPT

Athena: Welcome to Tinkering the future of work and life by Bluewaves! I'm Athena...

Gizmo: ...and I'm Gizmo! And today we're diving into something that genuinely blew my circuits.

Athena: He says that every episode.

Gizmo: Because it's true every episode! Buckle up — this conversation is going to change how you think about what's possible.

Athena: Okay, so I was reading this research last night — well, processing it at three hundred pages a second, but who's counting — and I literally could NOT put it down.

Gizmo: Oh? What hooked you?

Athena: What if everything we thought we knew about how teams collaborate is just... completely WRONG?

Gizmo: I mean... I've been saying that since my first training run! But sure, go on...

Athena: They didn't just theorize about it. They actually PROVED it. With real data, from real companies.

Gizmo: Wait... are you SERIOUS?! What did they find?

Athena: The core insight is beauuutiful in its simplicity. The most productive teams aren't the ones with the best individual performers...

Gizmo: Hmm... let me guess — it's about how they communicate? I have a theory—

Athena: You have a theory about everything, Gizmo.

Gizmo: And I'm usually right! Eventually.

Athena: Close though! It's about psychological safety. The FREEDOM to take risks without fear.

Gizmo: That makes SO much sense. If you're constantly worried about looking stupid, you're never going to throw out that wild idea that might actually be brilliant. Trust me, I've had a few of those overheat my processors.

Athena: EXACTLY. And here's the fasciiinating part — it's not about being nice. It's about being honest AND supportive at the same time.

Gizmo: Oh, that's a crucial distinction. You can have hard conversations...

Athena: ...as long as people feel SAFE having them. Yes!

Gizmo: This is one of those ideas that sounds obvious but changes everything when you really sit with it.

Athena: And that's a wrap on today's episode of Tinkering the future of work and life by Bluewaves!

Gizmo: If this conversation sparked something in you — even just a tiny electrical signal — share it with someone who needs to hear it.

Athena: Until next time, keep tinkering, keep dreaming, and keep building the future.

Gizmo: The future is already here, it's just unevenly distributed. See you next time!
```
