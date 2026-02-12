#!/usr/bin/env python3
"""Shared utilities for web-factory Cloudflare integration.

Provides credential resolution for both admin API (gateway) and
wrangler-based operations (Cloudflare API token + account ID).

Usage:
    python3 cf_utils.py --check-key
"""
import json
import os
import sys
from pathlib import Path


def resolve_gateway_credentials() -> tuple:
    """Resolve gateway domain and admin token.

    Checks in order:
    1. credentials.json in the script's directory (Claude.ai standalone ZIPs)
    2. Environment variables (Claude Code)
    Returns (domain, token) or raises RuntimeError.
    """
    creds_path = Path(__file__).parent / "credentials.json"
    domain = None
    token = None

    # 1. Credentials file (for Claude.ai standalone ZIPs)
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

    # 2. Environment variables
    if not domain:
        domain = os.environ.get("WEB_FACTORY_DOMAIN", "api.bluewaves-athena.app")
    if not token:
        token = os.environ.get("WEB_FACTORY_ADMIN_TOKEN")

    if not token:
        raise RuntimeError(
            "Admin token not found. Set it via:\n"
            "  Place credentials.json with {\"admin_token\": \"...\"} in the scripts/ directory\n"
            "  Or: export WEB_FACTORY_ADMIN_TOKEN='your-token'  (add to ~/.zshrc)"
        )

    return domain, token


def resolve_cloudflare_credentials() -> tuple:
    """Resolve Cloudflare API token and account ID for wrangler operations.

    Checks in order:
    1. credentials.json in the script's directory
    2. Environment variables
    Returns (api_token, account_id) or raises RuntimeError.
    """
    creds_path = Path(__file__).parent / "credentials.json"
    api_token = None
    account_id = None

    if creds_path.exists():
        try:
            with open(creds_path) as f:
                creds = json.load(f)
            t = creds.get("api_token", "")
            a = creds.get("account_id", "")
            if t and t != "YOUR_CLOUDFLARE_API_TOKEN_HERE":
                api_token = t
            if a and a != "YOUR_CLOUDFLARE_ACCOUNT_ID_HERE":
                account_id = a
        except (json.JSONDecodeError, KeyError):
            pass

    if not api_token:
        api_token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not account_id:
        account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")

    if not api_token:
        raise RuntimeError(
            "Cloudflare API token not found. Set it via:\n"
            "  Place credentials.json with {\"api_token\": \"...\"} in the scripts/ directory\n"
            "  Or: export CLOUDFLARE_API_TOKEN='your-token'  (add to ~/.zshrc)"
        )
    if not account_id:
        raise RuntimeError(
            "Cloudflare account ID not found. Set it via:\n"
            "  Place credentials.json with {\"account_id\": \"...\"} in the scripts/ directory\n"
            "  Or: export CLOUDFLARE_ACCOUNT_ID='your-id'  (add to ~/.zshrc)"
        )

    return api_token, account_id


def main():
    """CLI entry point for credential checking."""
    import argparse
    parser = argparse.ArgumentParser(description="web-factory credential utilities")
    parser.add_argument("--check-key", action="store_true",
                        help="Check credential resolution")
    args = parser.parse_args()

    if args.check_key:
        print("=== Gateway credentials ===")
        try:
            domain, token = resolve_gateway_credentials()
            print(f"  Domain: {domain}")
            print(f"  Token:  resolved ({len(token)} characters)")
        except RuntimeError as e:
            print(f"  Error: {e}", file=sys.stderr)

        print("\n=== Cloudflare credentials ===")
        try:
            api_token, account_id = resolve_cloudflare_credentials()
            print(f"  API token:  resolved ({len(api_token)} characters)")
            print(f"  Account ID: {account_id}")
        except RuntimeError as e:
            print(f"  Error: {e}", file=sys.stderr)

        # Report source
        creds_path = Path(__file__).parent / "credentials.json"
        if creds_path.exists():
            print(f"\nSource: credentials.json ({creds_path})")
        else:
            print("\nSource: environment variables")


if __name__ == "__main__":
    main()
