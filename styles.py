"""
styles.py - Visual constants for Album Cover Studio
Dark navy theme with emerald accent.
Import this module wherever colors or fonts are needed — never hard-code values.
"""

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

# Backgrounds
BG_DARK   = "#0F172A"   # Window / root background (lacivert-siyah)
BG_PANEL  = "#1E293B"   # Side panels and section containers (soft navy)
BG_CARD   = "#334155"   # Cards, input fields, track rows (hafif açık navy)

# Foregrounds
FG_PRIMARY   = "#E2E8F0"   # Main readable text (soft beyaz)
FG_SECONDARY = "#94A3B8"   # Subdued labels, placeholders (gri)

# Accent
ACCENT_GREEN       = "#10B981"   # Orta emerald — buttons, highlights
ACCENT_GREEN_HOVER = "#063A2C"   # Derin emerald — hover/active, badges

# Structural
BORDER_COLOR = "#334155"   # Subtle dividers between sections

# ---------------------------------------------------------------------------
# Fonts  (family, size, weight)
# ---------------------------------------------------------------------------

_FAMILY = "Helvetica"   # System-safe sans-serif on macOS/Linux/Windows

FONT_TITLE   = (_FAMILY, 18, "bold")   # Album name, window heading
FONT_HEADING = (_FAMILY, 12, "bold")   # Section headings
FONT_LABEL   = (_FAMILY, 10, "bold")   # Bold inline labels
FONT_BODY    = (_FAMILY, 10)           # General readable text
FONT_SMALL   = (_FAMILY,  9)           # Secondary / subdued info