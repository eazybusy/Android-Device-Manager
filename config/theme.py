# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  Android Device Manager — Design System v2                                  ║
# ║  Steel-Blue Dark palette · professional · slightly lighter than v1           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ── Surfaces (dark → light) ────────────────────────────────────────────────────
BG_DARK   = "#0E1F2F"   # Window root  — deepest layer
BG_PANEL  = "#132C42"   # Topbar / sidebar panels
BG_CARD   = "#1A3452"   # Card surfaces
BG_INPUT  = "#0C1B2A"   # Entry / dropdown fields
BG_HOVER  = "#1E3E5E"   # Interactive hover state

# ── Accent blue ────────────────────────────────────────────────────────────────
ACCENT       = "#2B85E4"   # Primary interactive blue
ACCENT_DARK  = "#1A6DC4"   # Pressed / hover on accent
ACCENT_SOFT  = "#16344E"   # Subtle tint background

# ── Text ───────────────────────────────────────────────────────────────────────
TEXT        = "#D4E6F7"   # Primary  — cool blue-white
TEXT_LABEL  = "#8AAFC8"   # Form labels / secondary
TEXT_MUTED  = "#506A82"   # Hints, placeholders, disabled

# ── Borders ────────────────────────────────────────────────────────────────────
BORDER      = "#1D3F5C"   # Default / resting
BORDER_ACT  = "#2B85E4"   # Focus / active  (= ACCENT)

# ── Semantic ───────────────────────────────────────────────────────────────────
GREEN   = "#29A87A"   # Connected / success
RED     = "#D95454"   # Error / disconnected
YELLOW  = "#D49020"   # Warning / caution

# ── Typography scale ───────────────────────────────────────────────────────────
FONT_TITLE  = 20
FONT_HEAD   = 14
FONT_BODY   = 13
FONT_SMALL  = 11
FONT_MICRO  = 10

# ── Shape tokens ───────────────────────────────────────────────────────────────
R_CARD  = 12
R_BTN   = 8
R_INPUT = 8

# ── Legacy aliases (keep third-party code happy) ───────────────────────────────
MUTED    = TEXT_MUTED
BG_PANEL_DARK = BG_INPUT