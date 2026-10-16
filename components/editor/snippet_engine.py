"""
SublimeLight - Editor Snippet Engine
Encapsulates keyword text mapping interceptions and handles structural 
multi-line boilerplate expansion strings when triggering Tab events.
"""

import re
from .snippets import SNIPPET_LIBRARY

class SnippetEngine:
    def __init__(self, text_area, update_line_count_callback, highlight_doc_callback, context):
        self.text_area = text_area
        self.update_line_count = update_line_count_callback
        self.highlight_full_document = highlight_doc_callback
        self.context = context

    def process_tab_event(self, event):
        """Intercepts the cursor tracking index line and auto-expands matching macro inputs."""
        try:
            current_cursor = self.text_area.index("insert")
            row, col = map(int, current_cursor.split("."))
            current_line_text = self.text_area.get(f"{row}.0", current_cursor)
            
            # Extract the last typed word token before the cursor caret
            word_match = re.search(r'(\b\w+)$', current_line_text)
            if not word_match:
                return None  # Fall back gracefully to standard spacer tab indents
                
            typed_keyword = word_match.group(1)
            
            if typed_keyword in SNIPPET_LIBRARY:
                # 1. Compute exact word span positions to wipe abbreviation
                word_start_col = col - len(typed_keyword)
                start_index_str = f"{row}.{word_start_col}"
                self.text_area.delete(start_index_str, current_cursor)
                
                # 2. Extract leading indentation spaces to align the macro lines perfectly
                leading_spaces_match = re.match(r'^([ \t]*)', current_line_text)
                base_indentation = leading_spaces_match.group(1) if leading_spaces_match else ""
                
                raw_template = SNIPPET_LIBRARY[typed_keyword]
                indented_lines = []
                for idx, line in enumerate(raw_template.split("\n")):
                    if idx == 0:
                        indented_lines.append(line)
                    else:
                        indented_lines.append(base_indentation + line)
                
                # 3. Inject full boilerplates into editing surface tracks
                self.text_area.insert(start_index_str, "\n".join(indented_lines))
                
                self.update_line_count()
                self.highlight_full_document(True)
                if self.context:
                    self.context.save_current_buffer_to_cache()
                    
                return "break"  # Blocks Tkinter from writing raw spacer characters
        except:
            pass
        return None
