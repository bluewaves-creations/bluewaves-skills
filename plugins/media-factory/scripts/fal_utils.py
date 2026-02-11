#!/usr/bin/env python3
"""Shared utilities for media-factory fal.ai integration.

Provides API key resolution, file download, data URI decoding,
local file upload, and platform-aware file opening.

Usage:
    python fal_utils.py --check-key
"""
import base64
import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request


def resolve_api_key() -> str:
    """Resolve fal.ai API key from credentials file or environment.

    Checks in order:
    1. credentials.json in the skill's scripts/ directory (Claude.ai standalone ZIPs)
    2. $FAL_KEY environment variable (Claude Code)
    3. Raises RuntimeError with instructions
    """
    # 1. Credentials file (for Claude.ai standalone ZIPs)
    creds_path = Path(__file__).parent / "credentials.json"
    if creds_path.exists():
        try:
            with open(creds_path) as f:
                creds = json.load(f)
            key = creds.get("api_key", "")
            if key and key != "USER_KEY_HERE":
                return key
        except (json.JSONDecodeError, KeyError):
            pass

    # 2. Environment variable
    key = os.environ.get("FAL_KEY")
    if key:
        return key

    raise RuntimeError(
        "FAL_KEY not found. Set it via:\n"
        "  Place credentials.json with {\"api_key\": \"...\"} in the scripts/ directory\n"
        "  Or: export FAL_KEY='your-api-key'  (add to ~/.zshrc)"
    )


def download_result(url: str, output_dir: str = ".", prefix: str = "generated") -> str:
    """Download a file from URL with a timestamped filename.

    Returns the local file path.
    """
    # Determine extension from URL or content type
    ext = ".png"
    if ".mp4" in url:
        ext = ".mp4"
    elif ".webp" in url:
        ext = ".webp"
    elif ".jpg" in url or ".jpeg" in url:
        ext = ".jpg"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}{ext}"
    filepath = os.path.join(output_dir, filename)

    req = Request(url)
    with urlopen(req) as response, open(filepath, "wb") as out:
        out.write(response.read())

    return filepath


def decode_data_uri(data_uri: str, output_path: str) -> str:
    """Decode a base64 data URI and save to file.

    Handles format: data:image/png;base64,<base64data>
    Returns the output path.
    """
    if "," in data_uri:
        data_uri = data_uri.split(",", 1)[1]
    data = base64.b64decode(data_uri)
    with open(output_path, "wb") as f:
        f.write(data)
    return output_path


def upload_local_file(path: str) -> str:
    """Upload a local file to fal.ai CDN for use as input.

    Returns the uploaded file URL.
    """
    import fal_client
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    return fal_client.upload_file(path)


def open_file(path: str):
    """Open a file with the platform-appropriate viewer."""
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["open", path], check=True)
        elif system == "Linux":
            subprocess.run(["xdg-open", path], check=True)
        elif system == "Windows":
            os.startfile(path)
    except Exception as e:
        print(f"Could not open file: {e}", file=sys.stderr)


def main():
    """CLI entry point for key checking."""
    import argparse
    parser = argparse.ArgumentParser(description="fal.ai utility functions")
    parser.add_argument("--check-key", action="store_true", help="Check API key resolution")
    args = parser.parse_args()

    if args.check_key:
        try:
            key = resolve_api_key()
            print(f"API key resolved ({len(key)} characters)")
            creds_path = Path(__file__).parent / "credentials.json"
            if creds_path.exists():
                try:
                    with open(creds_path) as f:
                        creds = json.load(f)
                    cred_key = creds.get("api_key", "")
                    if cred_key and cred_key != "USER_KEY_HERE":
                        print("Source: credentials.json")
                    else:
                        print("Source: $FAL_KEY env var")
                except (json.JSONDecodeError, KeyError):
                    print("Source: $FAL_KEY env var")
            else:
                print("Source: $FAL_KEY env var")
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
