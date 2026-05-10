"""
styles.py - Visual constants for Album Cover Studio
Dark Spotify-inspired theme: deep backgrounds with a #1DB954 green accent.
Import this module wherever colors or fonts are needed — never hard-code values.
"""

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

# Backgrounds (darkest → lightest)
BG_DARK   = "#121212"   # Window / root background
BG_PANEL  = "#1E1E1E"   # Side panels and section containers
BG_CARD   = "#282828"   # Cards, input fields, track rows

# Foregrounds
FG_PRIMARY   = "#FFFFFF"   # Main readable text
FG_SECONDARY = "#B3B3B3"   # Subdued labels, placeholders, timestamps

# Accent
ACCENT_GREEN       = "#1DB954"   # Spotify-brand green — buttons, highlights
ACCENT_GREEN_HOVER = "#1ED760"   # Slightly brighter on hover/active

# Structural
BORDER_COLOR = "#333333"   # Subtle dividers between sections

# ---------------------------------------------------------------------------
# Fonts  (family, size, weight)
# ---------------------------------------------------------------------------

_FAMILY = "Helvetica"   # System-safe sans-serif on macOS/Linux/Windows

FONT_TITLE   = (_FAMILY, 18, "bold")   # Album name, window heading
FONT_HEADING = (_FAMILY, 12, "bold")   # Section headings
FONT_LABEL   = (_FAMILY, 10, "bold")   # Bold inline labels (e.g. "Artist:")
FONT_BODY    = (_FAMILY, 10)           # General readable text
FONT_SMALL   = (_FAMILY,  9)           # Secondary / subdued info
