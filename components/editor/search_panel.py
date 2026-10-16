"""
SublimeLight - Editor Search Component Panel
Encapsulates the Find and Replace user interface row layout cleanly
without leaking styling geometry parameters into the main typing canvas.
"""

import customtkinter as ctk
import config

class SearchPanelComponent(ctk.CTkFrame):
    def __init__(self, parent, text_area, update_line_count_callback, highlight_doc_callback, context):
        super().__init__(parent, height=45, fg_color="#1a1a1a", corner_radius=0)
        self.text_area = text_area
        self.update_line_count = update_line_count_callback
        self.highlight_full_document = highlight_doc_callback
        self.context = context
        
        self.grid_propagate(False)

        # 1. Structural Inputs Sub-Layout
        self.find_entry = ctk.CTkEntry(
            self, width=160, placeholder_text="Find text...",
            font=(config.FONT_UI, 11), fg_color="#2c313c", border_width=0, text_color="white"
        )
        self.find_entry.pack(side="left", padx=(15, 5), pady=8)
        self.find_entry.bind("<KeyRelease>", self.execute_live_text_search)

        self.replace_entry = ctk.CTkEntry(
            self, width=160, placeholder_text="Replace with...",
            font=(config.FONT_UI, 11), fg_color="#2c313c", border_width=0, text_color="white"
        )
        self.replace_entry.pack(side="left", padx=5, pady=8)

        # 2. Command Execution Actions
        self.replace_btn = ctk.CTkButton(
            self, width=80, text="Replace", font=(config.FONT_UI, 11),
            fg_color="#A9FFB2", text_color="black", hover_color="#86DF90", 
            command=self.execute_text_replacement
        )
        self.replace_btn.pack(side="left", padx=5, pady=8)

        # 3. Dedicated Close Handle Button
        self.close_panel_btn = ctk.CTkButton(
            self, width=30, text="×", font=(config.FONT_UI, 14, "bold"),
            fg_color="transparent", text_color="#75715E", hover_color="#2c313c", 
            command=parent.toggle_find_panel
        )
        self.close_panel_btn.pack(side="right", padx=15, pady=8)

    def execute_live_text_search(self, event=None):
        """Scans the master text buffer using clean index pointers and highlights matches."""
        self.text_area.tag_remove("search_match", "1.0", "end")
        search_query = self.find_entry.get()
        
        if not search_query:
            return

        start_pos = "1.0"
        while True:
            match_index = self.text_area.search(search_query, start_pos, stopindex="end")
            if not match_index:
                break
                
            end_index = f"{match_index} + {len(search_query)} chars"
            self.text_area.tag_add("search_match", match_index, end_index)
            start_pos = end_index

    def execute_text_replacement(self):
        """Performs global text replacement substitution strings safely across the buffer canvas."""
        search_query = self.find_entry.get()
        replacement_text = self.replace_entry.get()
        
        if not search_query:
            return

        # Safely capture old plain text sequence lengths
        full_content = self.text_area.get("1.0", "end-1c")
        updated_content = full_content.replace(search_query, replacement_text)
        
        current_cursor = self.text_area.index("insert")
        
        # Rewrite the viewport string parameters
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", updated_content)
        
        # Reset state configurations smoothly
        self.text_area.mark_set("insert", current_cursor)
        self.update_line_count()
        self.highlight_full_document()
        self.execute_live_text_search()
        
        if self.context:
            self.context.save_current_buffer_to_cache()
