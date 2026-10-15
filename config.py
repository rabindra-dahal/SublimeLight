"""Application-wide configuration parameters and styles."""

# Default Window Configuration
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

# Sublime Atom UI Hex Colors Scheme
COLOR_BG = "#21252B"          # Main document workspace area tint
COLOR_SIDEBAR = "#1E2227"     # Sidebar navigation frame color
COLOR_TEXT = "#ABB2BF"        # Modern off-white monospace foreground
COLOR_STATUS_BAR = "#282C34"  # Base dashboard status footer metrics tracking color

# Fonts Configurations
FONT_EDITOR = ("Consolas", 14)
FONT_UI = ("Arial", 12)

# --- Syntax Highlighting Palette (Sublime Style) ---
COLOR_KEYWORD = "#F92672"   # Bright Pink (def, class, while, if, return)
COLOR_STRING  = "#E6DB74"   # Soft Yellow ("strings", 'strings')
COLOR_COMMENT = "#75715E"   # Muted Olive Gray (# comments)
COLOR_NUMBER  = "#AE81FF"   # Soft Purple (1, 2, 3, True, False)

# Collection of target language keywords to highlight
PYTHON_KEYWORDS = {
    'def', 'class', 'return', 'if', 'elif', 'else', 'while', 'for', 
    'in', 'break', 'continue', 'import', 'from', 'as', 'pass', 'try', 
    'except', 'lambda', 'with', 'assert', 'global', 'nonlocal'
}

PYTHON_NUMBERS = {'True', 'False', 'None'}

