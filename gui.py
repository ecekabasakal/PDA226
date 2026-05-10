"""
gui.py - Main GUI module for Album Cover Studio
Implements AlbumApp: a two-panel Tkinter window.

Left panel  — user inputs (journal text, genre, era, track count, generate button)
Right panel — generated output (cover art, album metadata, scrollable tracklist)

Public API (called by teammates):
    app.get_journal_text()            -> str
    app.get_genre()                   -> str
    app.get_era()                     -> str
    app.get_track_count()             -> int
    app.set_status(message)           -> None
    app.display_album(metadata,       -> None
                      tracks, image)
    app.bind_generate(callback)       -> None   (connect Generate button)
"""

import tkinter as tk
from tkinter import ttk
import webbrowser

import styles


# ---------------------------------------------------------------------------
# AlbumApp
# ---------------------------------------------------------------------------

class AlbumApp:
    """Root application window for Album Cover Studio."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Album Cover Studio")
        self.root.configure(bg=styles.BG_DARK)
        self.root.geometry("1150x720")
        self.root.minsize(900, 600)

        self._current_image = None   # Holds PhotoImage ref to prevent GC
        self._track_widgets  = []    # Track row widget references

        self._setup_style()
        self._build_ui()

    # ------------------------------------------------------------------
    # Theme / style setup
    # ------------------------------------------------------------------

    def _setup_style(self):
        """Apply a dark 'clam' ttk theme using the color constants in styles.py."""
        s = ttk.Style(self.root)
        s.theme_use("clam")

        # Global defaults
        s.configure(".",
                    background=styles.BG_DARK,
                    foreground=styles.FG_PRIMARY,
                    fieldbackground=styles.BG_CARD,
                    bordercolor=styles.BORDER_COLOR,
                    troughcolor=styles.BG_PANEL,
                    selectbackground=styles.ACCENT_GREEN,
                    selectforeground=styles.BG_DARK,
                    font=styles.FONT_BODY)

        # Frames
        s.configure("TFrame",        background=styles.BG_DARK)
        s.configure("Panel.TFrame",  background=styles.BG_PANEL)
        s.configure("Card.TFrame",   background=styles.BG_CARD)

        # Labels
        s.configure("TLabel",        background=styles.BG_DARK,  foreground=styles.FG_PRIMARY,   font=styles.FONT_BODY)
        s.configure("Panel.TLabel",  background=styles.BG_PANEL, foreground=styles.FG_PRIMARY,   font=styles.FONT_BODY)
        s.configure("Title.TLabel",  background=styles.BG_PANEL, foreground=styles.FG_PRIMARY,   font=styles.FONT_TITLE)
        s.configure("Heading.TLabel",background=styles.BG_PANEL, foreground=styles.FG_PRIMARY,   font=styles.FONT_HEADING)
        s.configure("Meta.TLabel",   background=styles.BG_CARD,  foreground=styles.FG_SECONDARY, font=styles.FONT_BODY)
        s.configure("Status.TLabel", background=styles.BG_PANEL, foreground=styles.FG_SECONDARY, font=styles.FONT_SMALL)

        # Accent button (Generate)
        s.configure("Accent.TButton",
                    background=styles.ACCENT_GREEN,
                    foreground=styles.BG_DARK,
                    font=styles.FONT_LABEL,
                    borderwidth=0,
                    padding=(10, 8))
        s.map("Accent.TButton",
              background=[("active", styles.ACCENT_GREEN_HOVER), ("pressed", styles.ACCENT_GREEN)],
              foreground=[("active", styles.BG_DARK)])

        # Listen button (small, outlined feel)
        s.configure("Listen.TButton",
                    background=styles.BG_PANEL,
                    foreground=styles.ACCENT_GREEN,
                    font=styles.FONT_SMALL,
                    borderwidth=1,
                    padding=(4, 2))
        s.map("Listen.TButton",
              background=[("active", styles.BG_CARD)],
              foreground=[("active", styles.ACCENT_GREEN_HOVER)])

        # Combobox
        s.configure("TCombobox",
                    fieldbackground=styles.BG_CARD,
                    background=styles.BG_CARD,
                    foreground=styles.FG_PRIMARY,
                    arrowcolor=styles.FG_SECONDARY,
                    bordercolor=styles.BORDER_COLOR,
                    lightcolor=styles.BG_CARD,
                    darkcolor=styles.BG_CARD)
        s.map("TCombobox",
              fieldbackground=[("readonly", styles.BG_CARD)],
              foreground=[("readonly", styles.FG_PRIMARY)],
              background=[("readonly", styles.BG_CARD)])

        # Spinbox
        s.configure("TSpinbox",
                    fieldbackground=styles.BG_CARD,
                    background=styles.BG_CARD,
                    foreground=styles.FG_PRIMARY,
                    arrowcolor=styles.FG_SECONDARY,
                    bordercolor=styles.BORDER_COLOR)

        # Scrollbar
        s.configure("TScrollbar",
                    background=styles.BG_PANEL,
                    troughcolor=styles.BG_DARK,
                    arrowcolor=styles.FG_SECONDARY,
                    bordercolor=styles.BG_PANEL)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        """Assemble the title bar and the two-panel content area."""
        # Title bar
        title_bar = ttk.Frame(self.root, style="Panel.TFrame", padding=(20, 14))
        title_bar.pack(fill="x")
        ttk.Label(title_bar, text="Album Cover Studio", style="Title.TLabel").pack(side="left")

        # Thin horizontal rule beneath title
        tk.Frame(self.root, bg=styles.BORDER_COLOR, height=1).pack(fill="x")

        # Content row
        content = ttk.Frame(self.root, style="TFrame")
        content.pack(fill="both", expand=True)

        # Left panel — fixed width
        left = ttk.Frame(content, style="Panel.TFrame", padding=(20, 20), width=300)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        # Vertical rule
        tk.Frame(content, bg=styles.BORDER_COLOR, width=1).pack(side="left", fill="y")

        # Right panel — expands
        right = ttk.Frame(content, style="Panel.TFrame", padding=(24, 20))
        right.pack(side="left", fill="both", expand=True)

        self._build_left_panel(left)
        self._build_right_panel(right)

    # --- Left panel ---

    def _build_left_panel(self, parent):
        """Journal input, genre/era/track-count controls, generate button, status."""

        # Journal entry
        ttk.Label(parent, text="Journal Entry / Mood", style="Heading.TLabel").pack(anchor="w", pady=(0, 6))

        self._journal_text = tk.Text(
            parent,
            height=9,
            wrap="word",
            bg=styles.BG_CARD,
            fg=styles.FG_SECONDARY,        # starts at placeholder colour
            insertbackground=styles.FG_PRIMARY,
            relief="flat",
            font=styles.FONT_BODY,
            padx=8, pady=8,
            selectbackground=styles.ACCENT_GREEN,
            selectforeground=styles.BG_DARK,
            borderwidth=0,
        )
        self._journal_text.pack(fill="x")
        self._install_placeholder(self._journal_text, "Describe your mood, day, or feelings…")

        # Genre
        ttk.Label(parent, text="Genre", style="Heading.TLabel").pack(anchor="w", pady=(16, 4))
        genres = ["Pop", "Rock", "Hip-Hop/Rap", "Electronic", "Indie",
                  "R&B/Soul", "Jazz", "Metal", "Türk Pop", "Klasik"]
        self._genre_var = tk.StringVar(value=genres[0])
        ttk.Combobox(parent, textvariable=self._genre_var, values=genres,
                     state="readonly").pack(fill="x")

        # Era
        ttk.Label(parent, text="Era", style="Heading.TLabel").pack(anchor="w", pady=(12, 4))
        eras = ["1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]
        self._era_var = tk.StringVar(value="2000s")
        ttk.Combobox(parent, textvariable=self._era_var, values=eras,
                     state="readonly").pack(fill="x")

        # Track count
        ttk.Label(parent, text="Track Count", style="Heading.TLabel").pack(anchor="w", pady=(12, 4))
        self._track_count_var = tk.IntVar(value=10)
        ttk.Spinbox(parent, from_=6, to=14, textvariable=self._track_count_var,
                    state="readonly", width=6).pack(anchor="w")

        # Spacer
        ttk.Label(parent, text="", style="Panel.TLabel").pack()

        # Generate button
        self._generate_btn = ttk.Button(parent, text="Generate Album", style="Accent.TButton")
        self._generate_btn.pack(fill="x", pady=(12, 0))

        # Status label
        self._status_var = tk.StringVar(value="Ready.")
        ttk.Label(parent, textvariable=self._status_var,
                  style="Status.TLabel", wraplength=260).pack(anchor="w", pady=(8, 0))

    # --- Right panel ---

    def _build_right_panel(self, parent):
        """Cover image + metadata row, followed by the scrollable tracklist."""

        # ── Top row: cover image  +  metadata ──────────────────────────
        top_row = ttk.Frame(parent, style="Panel.TFrame")
        top_row.pack(fill="x", pady=(0, 18))

        # Cover image placeholder
        img_outer = tk.Frame(top_row, bg=styles.BG_CARD, padx=2, pady=2)
        img_outer.pack(side="left", padx=(0, 20))

        self._cover_label = tk.Label(
            img_outer,
            text="Cover Art\nWill Appear Here",
            bg=styles.BG_CARD,
            fg=styles.FG_SECONDARY,
            font=styles.FONT_BODY,
            width=22,
            height=11,
            relief="flat",
        )
        self._cover_label.pack()

        # Metadata card
        meta_card = ttk.Frame(top_row, style="Card.TFrame", padding=(16, 14))
        meta_card.pack(side="left", fill="both", expand=True)

        # Album name (large)
        self._album_name_var = tk.StringVar(value="—")
        tk.Label(meta_card, textvariable=self._album_name_var,
                 bg=styles.BG_CARD, fg=styles.FG_PRIMARY,
                 font=styles.FONT_TITLE, wraplength=380, anchor="w",
                 justify="left").pack(anchor="w")

        tk.Frame(meta_card, bg=styles.BG_CARD, height=10).pack()  # spacer

        # Metadata rows (artist / year / label / mood / tags)
        self._meta_vars = {}
        for display, key in [("Artist", "artist"), ("Year", "year"),
                              ("Label", "label"),  ("Mood", "mood"), ("Tags", "tags")]:
            row = tk.Frame(meta_card, bg=styles.BG_CARD)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"{display}:", bg=styles.BG_CARD,
                     fg=styles.FG_SECONDARY, font=styles.FONT_SMALL,
                     width=7, anchor="e").pack(side="left")
            var = tk.StringVar(value="—")
            self._meta_vars[key] = var
            tk.Label(row, textvariable=var, bg=styles.BG_CARD,
                     fg=styles.FG_PRIMARY, font=styles.FONT_BODY,
                     anchor="w", wraplength=340, justify="left").pack(side="left", padx=(6, 0))

        # ── Tracklist ───────────────────────────────────────────────────
        ttk.Label(parent, text="Tracklist", style="Heading.TLabel").pack(anchor="w", pady=(0, 6))

        # Scrollable container
        track_outer = ttk.Frame(parent, style="Card.TFrame")
        track_outer.pack(fill="both", expand=True)

        self._track_canvas = tk.Canvas(
            track_outer,
            bg=styles.BG_CARD,
            highlightthickness=0,
            bd=0,
        )
        scrollbar = ttk.Scrollbar(track_outer, orient="vertical",
                                  command=self._track_canvas.yview)
        self._track_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self._track_canvas.pack(side="left", fill="both", expand=True)

        # Inner frame inside canvas
        self._track_inner = tk.Frame(self._track_canvas, bg=styles.BG_CARD)
        self._track_window = self._track_canvas.create_window(
            (0, 0), window=self._track_inner, anchor="nw"
        )

        # Resize hooks
        self._track_inner.bind("<Configure>", self._on_inner_configure)
        self._track_canvas.bind("<Configure>", self._on_canvas_configure)

        # Mousewheel scrolling (bound only while cursor is inside)
        self._track_canvas.bind("<Enter>", self._bind_mousewheel)
        self._track_canvas.bind("<Leave>", self._unbind_mousewheel)

        # Initial placeholder
        tk.Label(self._track_inner,
                 text="Generate an album to see the tracklist.",
                 bg=styles.BG_CARD, fg=styles.FG_SECONDARY,
                 font=styles.FONT_BODY, padx=12, pady=20).pack(anchor="w")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _install_placeholder(self, text_widget: tk.Text, placeholder: str):
        """Show grey hint text that vanishes when the user starts typing."""
        text_widget.insert("1.0", placeholder)
        text_widget._placeholder = placeholder

        def on_focus_in(_event):
            if text_widget.get("1.0", "end-1c") == text_widget._placeholder:
                text_widget.delete("1.0", "end")
                text_widget.config(fg=styles.FG_PRIMARY)

        def on_focus_out(_event):
            if not text_widget.get("1.0", "end-1c").strip():
                text_widget.insert("1.0", text_widget._placeholder)
                text_widget.config(fg=styles.FG_SECONDARY)

        text_widget.bind("<FocusIn>",  on_focus_in)
        text_widget.bind("<FocusOut>", on_focus_out)

    def _on_inner_configure(self, _event=None):
        """Update canvas scroll region when track rows are added/removed."""
        self._track_canvas.configure(scrollregion=self._track_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Stretch the inner frame to fill the canvas width."""
        self._track_canvas.itemconfig(self._track_window, width=event.width)

    def _bind_mousewheel(self, _event):
        self._track_canvas.bind_all("<MouseWheel>",       self._on_mousewheel)
        self._track_canvas.bind_all("<Button-4>",         self._on_mousewheel)  # Linux scroll up
        self._track_canvas.bind_all("<Button-5>",         self._on_mousewheel)  # Linux scroll down

    def _unbind_mousewheel(self, _event):
        self._track_canvas.unbind_all("<MouseWheel>")
        self._track_canvas.unbind_all("<Button-4>")
        self._track_canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        """Cross-platform mousewheel scrolling for the tracklist."""
        if event.num == 4:      # Linux scroll up
            self._track_canvas.yview_scroll(-1, "units")
        elif event.num == 5:    # Linux scroll down
            self._track_canvas.yview_scroll(1, "units")
        else:                   # macOS / Windows
            self._track_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _clear_tracklist(self):
        """Destroy all existing track rows."""
        for widget in self._track_inner.winfo_children():
            widget.destroy()
        self._track_widgets.clear()

    def _add_track_row(self, index: int, title: str, artist: str, on_listen=None):
        """Append one track row to the scrollable list."""
        # Alternate row shading for readability
        bg = styles.BG_CARD if index % 2 == 0 else styles.BG_PANEL

        row = tk.Frame(self._track_inner, bg=bg, pady=5, padx=10)
        row.pack(fill="x")

        # Track number
        tk.Label(row, text=f"{index:02d}.", bg=bg,
                 fg=styles.FG_SECONDARY, font=styles.FONT_SMALL,
                 width=3, anchor="e").pack(side="left")

        # Song title + artist (stacked vertically)
        info = tk.Frame(row, bg=bg)
        info.pack(side="left", fill="x", expand=True, padx=(10, 0))
        tk.Label(info, text=title,  bg=bg, fg=styles.FG_PRIMARY,
                 font=styles.FONT_BODY,  anchor="w").pack(anchor="w")
        tk.Label(info, text=artist, bg=bg, fg=styles.FG_SECONDARY,
                 font=styles.FONT_SMALL, anchor="w").pack(anchor="w")

        # Listen button
        listen_cmd = on_listen if on_listen else lambda: None
        ttk.Button(row, text="▶  Listen", style="Listen.TButton",
                   command=listen_cmd).pack(side="right")

        self._track_widgets.append(row)

    # ------------------------------------------------------------------
    # Teammate connection point
    # ------------------------------------------------------------------

    def bind_generate(self, callback):
        """Connect the Generate button to a handler defined in main.py."""
        self._generate_btn.configure(command=callback)

    # ------------------------------------------------------------------
    # Public API — called by teammates
    # ------------------------------------------------------------------

    def get_journal_text(self) -> str:
        """Return the user's journal entry, or '' if only the placeholder is shown."""
        text = self._journal_text.get("1.0", "end-1c").strip()
        placeholder = getattr(self._journal_text, "_placeholder", "")
        return "" if text == placeholder else text

    def get_genre(self) -> str:
        """Return the currently selected genre string."""
        return self._genre_var.get()

    def get_era(self) -> str:
        """Return the currently selected era string (e.g. '2000s')."""
        return self._era_var.get()

    def get_track_count(self) -> int:
        """Return the selected number of tracks as an integer."""
        return int(self._track_count_var.get())

    def set_status(self, message: str):
        """Update the status label below the Generate button."""
        self._status_var.set(message)
        self.root.update_idletasks()

    def display_album(self, metadata: dict, tracks: list, image=None):
        """
        Populate the right panel with generated album data.

        Args:
            metadata: dict — expected keys: name, artist, year, label, mood, tags
            tracks:   list of dicts — expected keys: title, artist, url (optional)
            image:    PIL.Image.Image object, or None to keep the placeholder
        """
        # Album name
        self._album_name_var.set(metadata.get("name", "Unknown Album"))

        # Metadata fields
        for key, var in self._meta_vars.items():
            value = metadata.get(key, "")
            var.set(str(value) if value else "—")

        # Cover image
        if image is not None:
            try:
                from PIL import ImageTk
                photo = ImageTk.PhotoImage(image)
                self._cover_label.configure(image=photo, text="", width=0, height=0)
                self._current_image = photo   # Keep reference — prevents garbage collection
            except Exception:
                self._cover_label.configure(text="[Image unavailable]")

        # Rebuild tracklist
        self._clear_tracklist()
        for i, track in enumerate(tracks, start=1):
            title  = track.get("title", "Unknown Title")
            artist = track.get("artist", "")
            url    = track.get("url", None)
            # Build a closure so each button captures its own URL
            on_listen = (lambda u: lambda: webbrowser.open(u))(url) if url else None
            self._add_track_row(i, title, artist, on_listen)

        if not tracks:
            tk.Label(self._track_inner,
                     text="No tracks found for this combination.",
                     bg=styles.BG_CARD, fg=styles.FG_SECONDARY,
                     font=styles.FONT_BODY, padx=12, pady=20).pack(anchor="w")
