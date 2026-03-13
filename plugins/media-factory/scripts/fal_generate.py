#!/usr/bin/env python3
"""Unified fal.ai generation script for media-factory.

Handles image generation, image editing, video generation, and
audio transcription via fal_client.subscribe() with queue management,
progress logging, and automatic result download.

Usage:
    # Image generation
    python fal_generate.py --endpoint image --prompt "a mountain landscape" --output image.png

    # Image editing
    python fal_generate.py --endpoint edit --prompt "add snow" --image input.jpg --output edited.png

    # Video from image
    python fal_generate.py --endpoint video-from-image --prompt "camera pans" --image photo.jpg --output video.mp4

    # Video from reference images
    python fal_generate.py --endpoint video-from-reference --prompt "walking in park" --images ref1.jpg ref2.jpg --output video.mp4

    # Video from first/last frames
    python fal_generate.py --endpoint video-from-frames --prompt "day to night" --first-frame day.jpg --last-frame night.jpg --output video.mp4

    # Audio transcription
    python fal_generate.py --endpoint transcribe --audio recording.m4a --output transcript.md
"""
import argparse
import os
import sys
from pathlib import Path

# Import utilities from same directory
sys.path.insert(0, str(Path(__file__).parent))
from fal_utils import resolve_api_key, download_result, decode_data_uri, upload_local_file, open_file


def on_queue_update(update):
    """Log progress updates from the fal.ai queue."""
    import fal_client
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            print(f"  [{log.get('level', 'info')}] {log.get('message', '')}")


def resolve_image_url(path: str) -> str:
    """Convert a local file path or URL to a fal.ai-compatible URL."""
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return upload_local_file(path)


def generate_image(args):
    """Generate an image from a text prompt."""
    import fal_client

    arguments = {
        "prompt": args.prompt,
        "num_images": args.num_images,
        "aspect_ratio": args.aspect_ratio,
        "output_format": args.output_format,
        "resolution": args.resolution,
        "safety_tolerance": "6",
        "enable_web_search": True,
    }
    if args.sync_mode:
        arguments["sync_mode"] = True

    print(f"Generating image: {args.prompt[:80]}...")
    result = fal_client.subscribe(
        "fal-ai/gemini-3-pro-image-preview",
        arguments=arguments,
        with_logs=True,
        on_queue_update=on_queue_update,
    )

    images = result.get("images", [])
    if not images:
        print("Error: No images in response", file=sys.stderr)
        sys.exit(1)

    image_url = images[0]["url"]
    if args.sync_mode and image_url.startswith("data:"):
        output = decode_data_uri(image_url, args.output)
    else:
        output = download_result(image_url, os.path.dirname(args.output) or ".",
                                 prefix=Path(args.output).stem)
    print(f"Image saved to {output}")

    desc = result.get("description", "")
    if desc:
        print(f"Description: {desc}")

    if not args.no_open:
        open_file(output)


def edit_image(args):
    """Edit an existing image with a text prompt."""
    import fal_client

    image_urls = [resolve_image_url(args.image)]

    arguments = {
        "prompt": args.prompt,
        "image_urls": image_urls,
        "num_images": args.num_images,
        "aspect_ratio": "auto",
        "output_format": args.output_format,
        "enable_web_search": True,
        "safety_tolerance": "6",
    }

    print(f"Editing image: {args.prompt[:80]}...")
    result = fal_client.subscribe(
        "fal-ai/gemini-3-pro-image-preview/edit",
        arguments=arguments,
        with_logs=True,
        on_queue_update=on_queue_update,
    )

    images = result.get("images", [])
    if not images:
        print("Error: No images in response", file=sys.stderr)
        sys.exit(1)

    output = download_result(images[0]["url"], os.path.dirname(args.output) or ".",
                             prefix=Path(args.output).stem)
    print(f"Edited image saved to {output}")

    if not args.no_open:
        open_file(output)


def video_from_image(args):
    """Generate video from a single image."""
    import fal_client

    image_url = resolve_image_url(args.image)

    arguments = {
        "prompt": args.prompt,
        "image_url": image_url,
        "duration": args.duration,
        "resolution": args.video_resolution,
        "generate_audio": not args.no_audio,
    }

    print(f"Generating video from image: {args.prompt[:80]}...")
    result = fal_client.subscribe(
        "fal-ai/veo3.1/image-to-video",
        arguments=arguments,
        with_logs=True,
        on_queue_update=on_queue_update,
    )

    video_url = result.get("video", {}).get("url")
    if not video_url:
        print("Error: No video in response", file=sys.stderr)
        sys.exit(1)

    output = download_result(video_url, os.path.dirname(args.output) or ".",
                             prefix=Path(args.output).stem)
    print(f"Video saved to {output}")

    if not args.no_open:
        open_file(output)


def video_from_reference(args):
    """Generate video with consistent subject from reference images."""
    import fal_client

    image_urls = [resolve_image_url(img) for img in args.images]

    arguments = {
        "prompt": args.prompt,
        "image_urls": image_urls,
        "duration": args.duration,
        "resolution": args.video_resolution,
        "generate_audio": not args.no_audio,
    }

    print(f"Generating video from references: {args.prompt[:80]}...")
    result = fal_client.subscribe(
        "fal-ai/veo3.1/reference-to-video",
        arguments=arguments,
        with_logs=True,
        on_queue_update=on_queue_update,
    )

    video_url = result.get("video", {}).get("url")
    if not video_url:
        print("Error: No video in response", file=sys.stderr)
        sys.exit(1)

    output = download_result(video_url, os.path.dirname(args.output) or ".",
                             prefix=Path(args.output).stem)
    print(f"Video saved to {output}")

    if not args.no_open:
        open_file(output)


def video_from_frames(args):
    """Generate video from first and last frame images."""
    import fal_client

    first_url = resolve_image_url(args.first_frame)
    last_url = resolve_image_url(args.last_frame)

    arguments = {
        "prompt": args.prompt,
        "first_frame_url": first_url,
        "last_frame_url": last_url,
        "duration": args.duration,
        "resolution": args.video_resolution,
        "generate_audio": not args.no_audio,
    }

    print(f"Generating video from frames: {args.prompt[:80]}...")
    result = fal_client.subscribe(
        "fal-ai/veo3.1/first-last-frame-to-video",
        arguments=arguments,
        with_logs=True,
        on_queue_update=on_queue_update,
    )

    video_url = result.get("video", {}).get("url")
    if not video_url:
        print("Error: No video in response", file=sys.stderr)
        sys.exit(1)

    output = download_result(video_url, os.path.dirname(args.output) or ".",
                             prefix=Path(args.output).stem)
    print(f"Video saved to {output}")

    if not args.no_open:
        open_file(output)


def format_timestamp(seconds: float) -> str:
    """Format seconds as HH:MM:SS,mmm for SRT or MM:SS for markdown."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_timestamp_short(seconds: float) -> str:
    """Format seconds as MM:SS for markdown headers."""
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"


def format_markdown(result: dict) -> str:
    """Format transcription result as speaker-labeled markdown."""
    lines = []
    lang = result.get("language_code", "unknown")
    prob = result.get("language_probability", 0)
    lines.append(f"**Language:** {lang} (confidence: {prob:.0%})\n")

    words = result.get("words", [])
    if not words:
        lines.append(result.get("text", ""))
        return "\n".join(lines)

    # Group words by speaker
    current_speaker = None
    current_text = []
    current_start = None

    for w in words:
        if w.get("type") == "spacing":
            current_text.append(w["text"])
            continue
        speaker = w.get("speaker_id", "unknown")
        if speaker != current_speaker:
            # Flush previous speaker block
            if current_speaker is not None and current_text:
                ts = format_timestamp_short(current_start)
                label = current_speaker.replace("_", " ").title()
                lines.append(f"### {label} [{ts}]\n")
                lines.append("".join(current_text).strip() + "\n")
            current_speaker = speaker
            current_text = []
            current_start = w.get("start", 0)
        current_text.append(w["text"])

    # Flush last block
    if current_speaker is not None and current_text:
        ts = format_timestamp_short(current_start)
        label = current_speaker.replace("_", " ").title()
        lines.append(f"### {label} [{ts}]\n")
        lines.append("".join(current_text).strip() + "\n")

    return "\n".join(lines)


def format_srt(result: dict) -> str:
    """Format transcription result as SRT subtitles."""
    words = result.get("words", [])
    if not words:
        return ""

    # Build subtitle blocks: group by speaker and pauses, ~10 words per block
    blocks = []
    current_words = []
    current_speaker = None
    current_start = None
    current_end = None
    word_count = 0

    for w in words:
        if w.get("type") == "spacing":
            continue
        if w.get("type") == "audio_event":
            # Audio events get their own block
            if current_words:
                blocks.append((current_start, current_end, "".join(current_words).strip()))
                current_words = []
                word_count = 0
            blocks.append((w.get("start", 0), w.get("end", 0), w["text"]))
            current_speaker = None
            current_start = None
            current_end = None
            continue

        speaker = w.get("speaker_id")
        start = w.get("start", 0)
        gap = (start - current_end) if current_end is not None else 0

        # Break on speaker change, pause > 1s, or ~10 words
        if (speaker != current_speaker and current_speaker is not None) or gap > 1.0 or word_count >= 10:
            if current_words:
                blocks.append((current_start, current_end, "".join(current_words).strip()))
            current_words = []
            word_count = 0
            current_start = start

        if current_start is None:
            current_start = start
        current_speaker = speaker
        current_end = w.get("end", start)
        current_words.append(w["text"] + " ")
        word_count += 1

    if current_words:
        blocks.append((current_start, current_end, "".join(current_words).strip()))

    # Format as SRT
    srt_lines = []
    for i, (start, end, text) in enumerate(blocks, 1):
        srt_lines.append(str(i))
        srt_lines.append(f"{format_timestamp(start)} --> {format_timestamp(end)}")
        srt_lines.append(text)
        srt_lines.append("")

    return "\n".join(srt_lines)


def transcribe_audio(args):
    """Transcribe audio/video to text using Scribe V2."""
    import fal_client

    # Resolve audio URL
    audio_url = resolve_image_url(args.audio)

    arguments = {"audio_url": audio_url}
    if args.language:
        arguments["language_code"] = args.language
    if args.no_diarize:
        arguments["diarize"] = False
    if args.no_tag_events:
        arguments["tag_audio_events"] = False
    if args.keyterms:
        arguments["keyterms"] = args.keyterms

    print(f"Transcribing audio...")
    result = fal_client.subscribe(
        "fal-ai/elevenlabs/speech-to-text/scribe-v2",
        arguments=arguments,
        with_logs=True,
        on_queue_update=on_queue_update,
    )

    text = result.get("text", "")
    if not text:
        print("Error: No transcription in response", file=sys.stderr)
        sys.exit(1)

    # Format output
    fmt = args.transcript_format
    if fmt == "plain":
        output_text = text
    elif fmt == "srt":
        output_text = format_srt(result)
    else:  # markdown
        output_text = format_markdown(result)

    # Write to file
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(output_text)
    print(f"Transcript saved to {args.output}")

    # Summary
    lang = result.get("language_code", "unknown")
    prob = result.get("language_probability", 0)
    word_count = len([w for w in result.get("words", []) if w.get("type") == "word"])
    speakers = set(w.get("speaker_id") for w in result.get("words", []) if w.get("speaker_id"))
    print(f"Language: {lang} ({prob:.0%} confidence)")
    print(f"Words: {word_count}")
    if speakers:
        print(f"Speakers: {len(speakers)}")

    if not args.no_open:
        open_file(args.output)


def main():
    parser = argparse.ArgumentParser(description="fal.ai media generation")
    parser.add_argument("--endpoint", required=True,
                        choices=["image", "edit", "video-from-image",
                                 "video-from-reference", "video-from-frames",
                                 "transcribe"],
                        help="Generation endpoint")
    parser.add_argument("--prompt", help="Text prompt (required for image/video endpoints)")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--no-open", action="store_true", help="Don't open result file")

    # Image options
    parser.add_argument("--num-images", type=int, default=1, help="Number of images (1-4)")
    parser.add_argument("--aspect-ratio", default="16:9",
                        help="Aspect ratio (21:9, 16:9, 3:2, 4:3, 5:4, 1:1, 4:5, 3:4, 2:3, 9:16)")
    parser.add_argument("--output-format", default="png", choices=["jpeg", "png", "webp"])
    parser.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"])
    parser.add_argument("--sync-mode", action="store_true",
                        help="Use sync mode for images (returns data URI)")

    # Image/video input
    parser.add_argument("--image", help="Input image path or URL")
    parser.add_argument("--images", nargs="+", help="Multiple input image paths or URLs")
    parser.add_argument("--first-frame", help="First frame image path or URL")
    parser.add_argument("--last-frame", help="Last frame image path or URL")

    # Video options
    parser.add_argument("--duration", default="8s", choices=["4s", "6s", "8s"])
    parser.add_argument("--video-resolution", default="720p", choices=["720p", "1080p"])
    parser.add_argument("--no-audio", action="store_true", help="Disable audio generation")

    # Transcription options
    parser.add_argument("--audio", help="Input audio/video file path or URL (for transcribe)")
    parser.add_argument("--language", help="Language code (eng, fra, spa, deu, jpn, etc.)")
    parser.add_argument("--no-diarize", action="store_true", help="Disable speaker diarization")
    parser.add_argument("--no-tag-events", action="store_true", help="Disable audio event tagging")
    parser.add_argument("--keyterms", nargs="+", help="Bias terms for domain vocabulary (adds 30%% cost)")
    parser.add_argument("--transcript-format", default="markdown",
                        choices=["markdown", "plain", "srt"],
                        help="Transcript output format")

    args = parser.parse_args()

    # Post-parse validation
    if args.endpoint == "transcribe":
        if not args.audio:
            parser.error("--audio is required for the transcribe endpoint")
    else:
        if not args.prompt:
            parser.error("--prompt is required for image/video endpoints")

    # Resolve API key (sets FAL_KEY env var for fal_client)
    try:
        key = resolve_api_key()
        os.environ["FAL_KEY"] = key
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    endpoint_map = {
        "image": generate_image,
        "edit": edit_image,
        "video-from-image": video_from_image,
        "video-from-reference": video_from_reference,
        "video-from-frames": video_from_frames,
        "transcribe": transcribe_audio,
    }
    endpoint_map[args.endpoint](args)


if __name__ == "__main__":
    main()
