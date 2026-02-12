#!/usr/bin/env python3
"""Python HTTP client for the web-factory admin API.

Stdlib-only — works in Claude.ai sandbox without pip packages.

Usage:
  python3 site_api.py publish  <build-dir> <brand> <site-name> [--title "..."] [--brand-kit <path>]
  python3 site_api.py update   <build-dir> <brand> <site-name> [--title "..."] [--brand-kit <path>]
  python3 site_api.py download <brand> <site-name> [output-dir]
  python3 site_api.py list     [<brand>]
  python3 site_api.py info     <brand> <site-name>
  python3 site_api.py delete   <brand> <site-name>
  python3 site_api.py rotate-password <brand> <site-name>

Environment / credentials.json:
  gateway_domain  or  WEB_FACTORY_DOMAIN      (default: bluewaves-athena.app)
  admin_token     or  WEB_FACTORY_ADMIN_TOKEN
"""
import argparse
import base64
import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def resolve_credentials() -> tuple:
    """Resolve gateway domain and admin token.

    Checks:
    1. credentials.json in the script's directory
    2. Environment variables
    Returns (domain, token) or raises RuntimeError.
    """
    creds_path = Path(__file__).parent / "credentials.json"
    domain = None
    token = None

    if creds_path.exists():
        try:
            with open(creds_path) as f:
                creds = json.load(f)
            d = creds.get("gateway_domain", "")
            t = creds.get("admin_token", "")
            if d and d != "YOUR_GATEWAY_DOMAIN_HERE":
                domain = d
            if t and t != "YOUR_ADMIN_TOKEN_HERE":
                token = t
        except (json.JSONDecodeError, KeyError):
            pass

    if not domain:
        domain = os.environ.get("WEB_FACTORY_DOMAIN", "bluewaves-athena.app")
    if not token:
        token = os.environ.get("WEB_FACTORY_ADMIN_TOKEN")

    if not token:
        raise RuntimeError(
            "Admin token not found. Set it via:\n"
            "  Place credentials.json with {\"admin_token\": \"...\"} in the scripts/ directory\n"
            "  Or: export WEB_FACTORY_ADMIN_TOKEN='your-token'"
        )

    return domain, token


def api_request(method: str, path: str, domain: str, token: str,
                body: dict = None) -> dict:
    """Make an authenticated HTTP request to the admin API."""
    url = f"https://{domain}/_api{path}"
    data = json.dumps(body).encode() if body else None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        error_body = e.read().decode()
        try:
            err = json.loads(error_body)
        except json.JSONDecodeError:
            err = {"error": error_body}
        print(f"API error ({e.code}): {err.get('error', error_body)}", file=sys.stderr)
        sys.exit(1)


def read_build_dir(build_dir: str) -> dict:
    """Read all files in a build directory, base64-encode them."""
    build_path = Path(build_dir)
    if not build_path.is_dir():
        print(f"Error: {build_dir} is not a directory", file=sys.stderr)
        sys.exit(1)
    if not (build_path / "index.html").exists():
        print(f"Error: {build_dir}/index.html not found", file=sys.stderr)
        sys.exit(1)

    files = {}
    for filepath in build_path.rglob("*"):
        if filepath.is_file():
            rel = str(filepath.relative_to(build_path))
            with open(filepath, "rb") as f:
                files[rel] = base64.b64encode(f.read()).decode()
    return files


def read_brand_tokens(manifest_path: str) -> dict:
    """Extract color tokens from a brand kit manifest.json for login page styling."""
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        return manifest.get("tokens", {}).get("colors", {})
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        print(f"Warning: Could not read brand kit: {e}", file=sys.stderr)
        return {}


def cmd_publish(args):
    domain, token = resolve_credentials()
    files = read_build_dir(args.build_dir)
    body = {"title": args.title or args.site_name, "files": files}
    if args.brand_kit:
        body["brand_tokens"] = read_brand_tokens(args.brand_kit)

    result = api_request("POST", f"/sites/{args.brand}/{args.site_name}",
                         domain, token, body)
    print(f"Published: {result['url']}")
    print(f"Password:  {result['password']}")
    print(f"Files:     {result.get('files', len(files))}")


def cmd_update(args):
    domain, token = resolve_credentials()
    files = read_build_dir(args.build_dir)
    body = {"files": files}
    if args.title:
        body["title"] = args.title
    if args.brand_kit:
        body["brand_tokens"] = read_brand_tokens(args.brand_kit)

    result = api_request("PUT", f"/sites/{args.brand}/{args.site_name}",
                         domain, token, body)
    print(f"Updated: {result.get('updated')}")
    print(f"Files:   {result.get('files', len(files))}")


def cmd_list(args):
    domain, token = resolve_credentials()
    path = "/sites"
    if args.brand:
        path += f"?brand={args.brand}"

    result = api_request("GET", path, domain, token)
    sites = result.get("sites", [])
    if not sites:
        print("No sites found.")
        return

    print(f"{'Brand':<16} {'Name':<24} {'Title':<32} {'Created'}")
    print("-" * 90)
    for s in sites:
        print(f"{s['brand']:<16} {s['name']:<24} {s['title']:<32} {s['created'][:10]}")
    print(f"\n{result.get('count', len(sites))} site(s)")


def cmd_info(args):
    domain, token = resolve_credentials()
    result = api_request("GET", f"/sites/{args.brand}/{args.site_name}",
                         domain, token)
    print(json.dumps(result, indent=2))


def cmd_delete(args):
    domain, token = resolve_credentials()
    result = api_request("DELETE", f"/sites/{args.brand}/{args.site_name}",
                         domain, token)
    print(f"Deleted: {result.get('deleted')}")


def cmd_download(args):
    domain, token = resolve_credentials()
    result = api_request("GET", f"/sites/{args.brand}/{args.site_name}/files",
                         domain, token)
    files = result.get("files", {})
    if not files:
        print("No files found.", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    total_bytes = 0
    for rel_path, b64_content in files.items():
        file_path = out_dir / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        data = base64.b64decode(b64_content)
        with open(file_path, "wb") as f:
            f.write(data)
        total_bytes += len(data)

    print(f"Downloaded {len(files)} file(s) to {out_dir}/ ({total_bytes:,} bytes)")
    metadata = result.get("metadata", {})
    if metadata.get("title"):
        print(f"Title: {metadata['title']}")


def cmd_rotate(args):
    domain, token = resolve_credentials()
    result = api_request("POST", f"/sites/{args.brand}/{args.site_name}/password",
                         domain, token)
    print(f"New password: {result['password']}")
    print(f"URL:          {result['url']}")


def main():
    parser = argparse.ArgumentParser(description="web-factory admin API client")
    sub = parser.add_subparsers(dest="command", required=True)

    # publish
    p = sub.add_parser("publish", help="Publish a new site")
    p.add_argument("build_dir", help="Path to build directory with index.html")
    p.add_argument("brand", help="Brand subdomain (e.g. bluewaves)")
    p.add_argument("site_name", help="Site path segment (e.g. q1-proposal)")
    p.add_argument("--title", help="Site title")
    p.add_argument("--brand-kit", help="Path to brand kit manifest.json")
    p.set_defaults(func=cmd_publish)

    # update
    p = sub.add_parser("update", help="Update an existing site")
    p.add_argument("build_dir", help="Path to build directory with index.html")
    p.add_argument("brand", help="Brand subdomain")
    p.add_argument("site_name", help="Site path segment")
    p.add_argument("--title", help="New title")
    p.add_argument("--brand-kit", help="Path to brand kit manifest.json")
    p.set_defaults(func=cmd_update)

    # list
    p = sub.add_parser("list", help="List all sites")
    p.add_argument("brand", nargs="?", help="Filter by brand")
    p.set_defaults(func=cmd_list)

    # info
    p = sub.add_parser("info", help="Get site metadata")
    p.add_argument("brand", help="Brand subdomain")
    p.add_argument("site_name", help="Site path segment")
    p.set_defaults(func=cmd_info)

    # download
    p = sub.add_parser("download", help="Download all site files")
    p.add_argument("brand", help="Brand subdomain")
    p.add_argument("site_name", help="Site path segment")
    p.add_argument("output_dir", nargs="?", default="./build",
                   help="Output directory (default: ./build)")
    p.set_defaults(func=cmd_download)

    # delete
    p = sub.add_parser("delete", help="Delete a site")
    p.add_argument("brand", help="Brand subdomain")
    p.add_argument("site_name", help="Site path segment")
    p.set_defaults(func=cmd_delete)

    # rotate-password
    p = sub.add_parser("rotate-password", help="Rotate site password")
    p.add_argument("brand", help="Brand subdomain")
    p.add_argument("site_name", help="Site path segment")
    p.set_defaults(func=cmd_rotate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
