"""
SublimeLight - Editor Syntax Highlighting Engine
Encapsulates regex matching loops to apply high-contrast Monokai theme 
tokens onto the active editing canvas without cluttering the view modules.
"""

import re

class SyntaxHighlighter:
    def __init__(self, text_area):
        self.text_area = text_area

        # Configure Monokai color tags on the provided text area widget
        self.text_area.tag_config("keyword", foreground="#F92672")  # Pink
        self.text_area.tag_config("builtin", foreground="#66D9EF")  # Cyan
        self.text_area.tag_config("string", foreground="#E6DB74")   # Yellow
        self.text_area.tag_config("comment", foreground="#75715E")  # Grey
        self.text_area.tag_config("number", foreground="#AE81FF")   # Purple
        self.text_area.tag_config("search_match", background="#FFB200", foreground="black")

    def highlight(self, is_elements_visible):
        """Scans the buffer canvas text data and applies Monokai token tags."""
        if not is_elements_visible:
            return

        # Clear existing color layers to re-parse clean blocks
        for tag in ["keyword", "builtin", "string", "comment", "number"]:
            self.text_area.tag_remove(tag, "1.0", "end")

        code_text = self.text_area.get("1.0", "end-1c")

        # Master Python regex matching matrix rules
        keywords = r'\b(def|class|return|while|for|in|if|elif|else|break|continue|import|from|as|global|assert|pass|try|except|finally|print)\b'
        builtins = r'\b(str|int|float|list|dict|set|tuple|len|range|enumerate|print|input|open|append|strip|split)\b'
        strings = r'(\".*?\"|\'.*?\')'
        comments = r'(#.*)'
        numbers = r'\b(\d+)\b'

        def apply_tag(pattern, tag_name):
            for match in re.finditer(pattern, code_text):
                start_idx = self.text_area.index(f"1.0 + {match.start()} chars")
                end_idx = self.text_area.index(f"1.0 + {match.end()} chars")
                self.text_area.tag_add(tag_name, start_idx, end_idx)

        # Cascade rendering passes
        apply_tag(numbers, "number")
        apply_tag(keywords, "keyword")
        apply_tag(builtins, "builtin")
        apply_tag(strings, "string")
        apply_tag(comments, "comment")
