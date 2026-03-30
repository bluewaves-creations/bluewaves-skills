#!/usr/bin/env python3
"""Bluewaves brand design tokens for skill-eval HTML output.

Single source of truth for color tokens used by generate_review.py
and generate_report.py. Matches the Bluewaves brand kit at
plugins/docs-factory/skills/brand-bluewaves/references/tokens.md.
"""

# --- Brand colors ---
PRIMARY = "#B78A66"       # Brown Sand
PRIMARY_DARK = "#A07550"  # Hover state
ACCENT_TEAL = "#00D2E0"   # Ocean teal
ACCENT_RED = "#FF375F"    # Sun red

# --- Neutrals ---
NEUTRAL_900 = "#2C2C2C"   # Body text (never pure black)
NEUTRAL_700 = "#4A4A4A"
NEUTRAL_500 = "#7A7A7A"   # Muted text
NEUTRAL_300 = "#B0B0B0"   # Borders
NEUTRAL_100 = "#F5F5F7"   # Alt backgrounds
WHITE = "#FFFFFF"          # Page backgrounds

# --- Derived ---
BORDER_LIGHT = "#E5E5E5"
CODE_TEXT = "#0891B2"      # Dark teal for code on white bg

# --- Semantic (functional, not brand) ---
PASS = "#30D158"
FAIL = "#FF4245"
PENDING = "#D97706"

# Light-background badge variants
PASS_BG = "#E8F8EC"
FAIL_BG = "#FEE2E2"
PENDING_BG = "#FEF3C7"

# Badge text (dark for light backgrounds)
PASS_TEXT = "#166534"
FAIL_TEXT = "#991B1B"
PENDING_TEXT = "#92400E"

# --- Score badges (for reports) ---
SCORE_GOOD_BG = PASS_BG
SCORE_GOOD_FG = PASS_TEXT
SCORE_OK_BG = PENDING_BG
SCORE_OK_FG = PENDING
SCORE_BAD_BG = FAIL_BG
SCORE_BAD_FG = FAIL_TEXT

# --- Typography ---
FONT_BODY = "'Merriweather', Georgia, serif"
FONT_MONO = "'Fira Code', 'SF Mono', monospace"
FONT_IMPORT = "@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=Fira+Code&display=swap');"

# --- Light theme dict (for generate_report.py) ---
LIGHT_THEME = {
    "bg": WHITE,
    "fg": NEUTRAL_900,
    "card_bg": NEUTRAL_100,
    "border": NEUTRAL_300,
    "th_bg": PRIMARY,
    "th_fg": WHITE,
    "test_th_bg": ACCENT_TEAL,
    "test_cell_bg": "#F0FBFC",
    "hover_bg": NEUTRAL_100,
    "best_bg": PASS_BG,
    "pass_color": PASS,
    "fail_color": FAIL,
    "muted": NEUTRAL_500,
    "score_good_bg": SCORE_GOOD_BG,
    "score_good_fg": SCORE_GOOD_FG,
    "score_ok_bg": SCORE_OK_BG,
    "score_ok_fg": SCORE_OK_FG,
    "score_bad_bg": SCORE_BAD_BG,
    "score_bad_fg": SCORE_BAD_FG,
    "desc_bg": NEUTRAL_100,
}

# --- Dark theme dict (kept for --dark flag) ---
DARK_THEME = {
    "bg": "#0a0a0a",
    "fg": "#e0e0e0",
    "card_bg": "#1a1a1a",
    "border": "#333",
    "th_bg": "#222",
    "th_fg": "#e0e0e0",
    "test_th_bg": "#1a3a5c",
    "test_cell_bg": "#0d1a2a",
    "hover_bg": "#1e1e1e",
    "best_bg": "#1a2e1a",
    "pass_color": "#22c55e",
    "fail_color": "#ef4444",
    "muted": "#888",
    "score_good_bg": "#052e16",
    "score_good_fg": "#22c55e",
    "score_ok_bg": "#422006",
    "score_ok_fg": "#f59e0b",
    "score_bad_bg": "#450a0a",
    "score_bad_fg": "#ef4444",
    "desc_bg": "#111",
}
