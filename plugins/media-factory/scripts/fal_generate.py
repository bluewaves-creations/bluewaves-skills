#!/usr/bin/env python3
"""Unified fal.ai generation script for media-factory.

Handles image generation, image editing, and video generation via
fal_client.subscribe() with queue management, progress logging,
and automatic result download.

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


def main():
    parser = argparse.ArgumentParser(description="fal.ai media generation")
    parser.add_argument("--endpoint", required=True,
                        choices=["image", "edit", "video-from-image",
                                 "video-from-reference", "video-from-frames"],
                        help="Generation endpoint")
    parser.add_argument("--prompt", required=True, help="Text prompt")
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

    args = parser.parse_args()

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
    }
    endpoint_map[args.endpoint](args)


if __name__ == "__main__":
    main()
