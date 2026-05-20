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
    app.bind_generate(callback)       -> None
"""

import tkinter as tk
from tkinter import ttk
import webbrowser

import styles


# ---------------------------------------------------------------------------
# RoundedButton — Canvas-based button with rounded corners
# ---------------------------------------------------------------------------

class RoundedButton(tk.Canvas):
    """A fully custom button with rounded corners drawn on a Canvas."""

    def __init__(self, parent, text, command=None,
                 bg=None, fg=None, hover_bg=None,
                 font=None, radius=18, padx=20, pady=8,
                 master_bg=None, **kwargs):
        self._bg       = bg       or styles.ACCENT_GREEN
        self._fg       = fg       or styles.BG_DARK
        self._hover_bg = hover_bg or styles.ACCENT_GREEN_HOVER
        self._font     = font     or styles.FONT_LABEL
        self._radius   = radius
        self._padx     = padx
        self._pady     = pady
        self._command  = command
        self._text     = text

        # Measure text size using tkinter font module
        import tkinter.font as tkfont
        f = tkfont.Font(family=self._font[0], size=self._font[1],
                        weight=self._font[2] if len(self._font) > 2 else "normal")
        self._btn_w = int(f.measure(text)) + padx * 2
        self._btn_h = int(f.metrics("linespace")) + pady * 2

        super().__init__(parent,
                         width=self._btn_w, height=self._btn_h,
                         highlightthickness=0, bd=0,
                         bg=master_bg or styles.BG_PANEL,
                         **kwargs)

        self._draw(self._bg)

        self.bind("<Enter>",           self._on_enter)
        self.bind("<Leave>",           self._on_leave)
        self.bind("<ButtonPress-1>",   self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        self.create_arc(x1,       y1,       x1+2*r,   y1+2*r,   start=90,  extent=90,  **kw)
        self.create_arc(x2-2*r,   y1,       x2,       y1+2*r,   start=0,   extent=90,  **kw)
        self.create_arc(x1,       y2-2*r,   x1+2*r,   y2,       start=180, extent=90,  **kw)
        self.create_arc(x2-2*r,   y2-2*r,   x2,       y2,       start=270, extent=90,  **kw)
        self.create_rectangle(x1+r, y1,   x2-r, y2,   **kw)
        self.create_rectangle(x1,   y1+r, x2,   y2-r, **kw)

    def _draw(self, bg_color):
        self.delete("all")
        self._round_rect(0, 0, self._btn_w, self._btn_h, self._radius,
                         fill=bg_color, outline=bg_color)
        self.create_text(self._btn_w // 2, self._btn_h // 2,
                         text=self._text, fill=self._fg, font=self._font)

    def _on_enter(self, _e):   self._draw(self._hover_bg)
    def _on_leave(self, _e):   self._draw(self._bg)
    def _on_press(self, _e):   self._draw(self._hover_bg)
    def _on_release(self, _e):
        self._draw(self._bg)
        if self._command:
            self._command()

    def configure(self, **kwargs):
        if "command" in kwargs:
            self._command = kwargs.pop("command")
        super().configure(**kwargs)


class AlbumApp:
    """Root application window for Album Cover Studio."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Album Cover Studio")
        self.root.configure(bg=styles.BG_DARK)
        self.root.geometry("1150x720")
        self.root.minsize(900, 600)

        self._current_image = None
        self._track_widgets  = []

        self._setup_style()
        self._build_ui()

    # ------------------------------------------------------------------
    # Theme / style setup
    # ------------------------------------------------------------------

    def _setup_style(self):
        s = ttk.Style(self.root)
        s.theme_use("clam")

        s.configure(".",
                    background=styles.BG_DARK,
                    foreground=styles.FG_PRIMARY,
                    fieldbackground=styles.BG_CARD,
                    bordercolor=styles.BORDER_COLOR,
                    troughcolor=styles.BG_PANEL,
                    selectbackground=styles.ACCENT_GREEN,
                    selectforeground=styles.BG_DARK,
                    font=styles.FONT_BODY)

        s.configure("TFrame",        background=styles.BG_DARK)
        s.configure("Panel.TFrame",  background=styles.BG_PANEL)
        s.configure("Card.TFrame",   background=styles.BG_CARD)

        s.configure("TLabel",        background=styles.BG_DARK,  foreground=styles.FG_PRIMARY,   font=styles.FONT_BODY)
        s.configure("Panel.TLabel",  background=styles.BG_PANEL, foreground=styles.FG_PRIMARY,   font=styles.FONT_BODY)
        s.configure("Title.TLabel",  background=styles.BG_PANEL, foreground=styles.FG_PRIMARY,   font=styles.FONT_TITLE)
        s.configure("Heading.TLabel",background=styles.BG_PANEL, foreground=styles.ACCENT_GREEN, font=styles.FONT_HEADING)
        s.configure("Meta.TLabel",   background=styles.BG_CARD,  foreground=styles.FG_SECONDARY, font=styles.FONT_BODY)
        s.configure("Status.TLabel", background=styles.BG_PANEL, foreground=styles.FG_SECONDARY, font=styles.FONT_SMALL)

        # Accent button (Generate)
        s.configure("Accent.TButton",
                    background=styles.ACCENT_GREEN,
                    foreground=styles.BG_DARK,
                    font=styles.FONT_LABEL,
                    borderwidth=0,
                    relief="flat",
                    padding=(14, 10))
        s.map("Accent.TButton",
              background=[("active", styles.ACCENT_GREEN_HOVER), ("pressed", styles.ACCENT_GREEN)],
              foreground=[("active", styles.FG_PRIMARY)])

        # Listen button
        s.configure("Listen.TButton",
                    background=styles.ACCENT_GREEN_HOVER,
                    foreground=styles.ACCENT_GREEN,
                    font=styles.FONT_BODY,
                    borderwidth=0,
                    relief="flat",
                    padding=(10, 5))
        s.map("Listen.TButton",
              background=[("active", styles.BG_CARD)],
              foreground=[("active", styles.ACCENT_GREEN)])

        # Combobox
        s.configure("TCombobox",
                    fieldbackground=styles.BG_CARD,
                    background=styles.BG_CARD,
                    foreground=styles.FG_PRIMARY,
                    arrowcolor=styles.ACCENT_GREEN,
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
                    arrowcolor=styles.ACCENT_GREEN,
                    bordercolor=styles.BORDER_COLOR)

        # Scrollbar
        s.configure("TScrollbar",
                    background=styles.BG_CARD,
                    troughcolor=styles.BG_PANEL,
                    arrowcolor=styles.BG_PANEL,
                    bordercolor=styles.BG_PANEL,
                    relief="flat")

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        # Title bar
        title_bar = ttk.Frame(self.root, style="Panel.TFrame", padding=(20, 14))
        title_bar.pack(fill="x")

        # Green accent line left of title
        title_inner = tk.Frame(title_bar, bg=styles.BG_PANEL)
        title_inner.pack(side="left")
        tk.Frame(title_inner, bg=styles.ACCENT_GREEN, width=3, height=24).pack(side="left", padx=(0, 10))
        tk.Label(title_inner, text="Album Cover Studio",
                 bg=styles.BG_PANEL, fg=styles.FG_PRIMARY,
                 font=styles.FONT_TITLE).pack(side="left")

        tk.Frame(self.root, bg=styles.BORDER_COLOR, height=1).pack(fill="x")

        content = ttk.Frame(self.root, style="TFrame")
        content.pack(fill="both", expand=True)

        left = ttk.Frame(content, style="Panel.TFrame", padding=(20, 20), width=300)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Frame(content, bg=styles.BORDER_COLOR, width=1).pack(side="left", fill="y")

        right = ttk.Frame(content, style="TFrame", padding=(24, 20))
        right.pack(side="left", fill="both", expand=True)

        self._build_left_panel(left)
        self._build_right_panel(right)

    # --- Left panel ---

    def _build_left_panel(self, parent):
        ttk.Label(parent, text="JOURNAL ENTRY / MOOD", style="Heading.TLabel").pack(anchor="w", pady=(0, 6))

        _j_box, _j_inner = self._make_rounded_box(parent, radius=10, pad=4)
        _j_box.pack(fill="x")
        self._journal_text = tk.Text(
            _j_inner,
            height=9,
            wrap="word",
            bg=styles.BG_CARD,
            fg=styles.FG_SECONDARY,
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

        ttk.Label(parent, text="GENRE", style="Heading.TLabel").pack(anchor="w", pady=(16, 4))
        genres = ["Pop", "Rock", "Hip-Hop/Rap", "Electronic", "Indie",
                  "R&B/Soul", "Jazz", "Metal", "Türk Pop", "Klasik"]
        self._genre_var = tk.StringVar(value=genres[0])
        _g_box, _g_inner = self._make_rounded_box(parent, radius=10, pad=4)
        _g_box.pack(fill="x")
        ttk.Combobox(_g_inner, textvariable=self._genre_var, values=genres,
                     state="readonly").pack(fill="x")

        ttk.Label(parent, text="ERA", style="Heading.TLabel").pack(anchor="w", pady=(12, 4))
        eras = ["1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]
        self._era_var = tk.StringVar(value="2000s")
        _e_box, _e_inner = self._make_rounded_box(parent, radius=10, pad=4)
        _e_box.pack(fill="x")
        ttk.Combobox(_e_inner, textvariable=self._era_var, values=eras,
                     state="readonly").pack(fill="x")

        ttk.Label(parent, text="TRACK COUNT", style="Heading.TLabel").pack(anchor="w", pady=(12, 4))
        self._track_count_var = tk.IntVar(value=10)
        _t_box, _t_inner = self._make_rounded_box(parent, radius=10, pad=4)
        _t_box.pack(anchor="w")
        ttk.Spinbox(_t_inner, from_=6, to=14, textvariable=self._track_count_var,
                    state="readonly", width=6).pack(anchor="w")

        ttk.Label(parent, text="", style="Panel.TLabel").pack()

        self._generate_btn = RoundedButton(
            parent, text="Generate Album",
            bg=styles.ACCENT_GREEN,
            fg=styles.BG_DARK,
            hover_bg="#0d9e6e",
            font=styles.FONT_LABEL,
            radius=18, padx=30, pady=10,
            master_bg=styles.BG_PANEL,
        )
        self._generate_btn.pack(fill="x", pady=(12, 0))

        self._status_var = tk.StringVar(value="✓ Ready.")
        ttk.Label(parent, textvariable=self._status_var,
                  style="Status.TLabel", wraplength=260).pack(anchor="w", pady=(8, 0))

    # --- Right panel ---

    def _build_right_panel(self, parent):
        # ── Top row: cover image + metadata ──
        top_row = tk.Frame(parent, bg=styles.BG_DARK)
        top_row.pack(fill="x", pady=(0, 18))

        # Cover image — larger square with rounded canvas border
        _cover_canvas = tk.Canvas(top_row, bg=styles.BG_DARK, highlightthickness=0, bd=0,
                                   width=172, height=172)
        _cover_canvas.pack(side="left", padx=(0, 20))
        AlbumApp._draw_rr(_cover_canvas, 0, 0, 172, 172, 12,
                           fill=styles.BG_PANEL, outline=styles.BG_PANEL)
        self._cover_label = tk.Label(
            _cover_canvas,
            text="Cover Art\nWill Appear Here",
            bg=styles.BG_PANEL,
            fg=styles.FG_SECONDARY,
            font=styles.FONT_BODY,
            relief="flat",
        )
        _cover_canvas.create_window(6, 6, anchor="nw", window=self._cover_label,
                                     width=160, height=160)

        # Metadata block
        meta = tk.Frame(top_row, bg=styles.BG_DARK)
        meta.pack(side="left", fill="both", expand=True)

        # "AI CURATED PLAYLIST" label
        tk.Label(meta, text="AI CURATED PLAYLIST",
                 bg=styles.BG_DARK, fg=styles.ACCENT_GREEN,
                 font=styles.FONT_SMALL).pack(anchor="w")

        # Album name
        self._album_name_var = tk.StringVar(value="—")
        tk.Label(meta, textvariable=self._album_name_var,
                 bg=styles.BG_DARK, fg=styles.FG_PRIMARY,
                 font=styles.FONT_TITLE, wraplength=400,
                 anchor="w", justify="left").pack(anchor="w", pady=(2, 0))

        # Mood description (italic)
        self._mood_var = tk.StringVar(value="")
        tk.Label(meta, textvariable=self._mood_var,
                 bg=styles.BG_DARK, fg=styles.FG_SECONDARY,
                 font=(styles.FONT_BODY[0], styles.FONT_BODY[1], "italic"),
                 wraplength=400, anchor="w", justify="left").pack(anchor="w", pady=(4, 6))

        # Metadata rows
        self._meta_vars = {}
        for display, key in [("Artist", "artist"), ("Year", "year"), ("Label", "label")]:
            row = tk.Frame(meta, bg=styles.BG_DARK)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"{display}:", bg=styles.BG_DARK,
                     fg=styles.FG_SECONDARY, font=styles.FONT_SMALL,
                     width=7, anchor="e").pack(side="left")
            var = tk.StringVar(value="—")
            self._meta_vars[key] = var
            tk.Label(row, textvariable=var, bg=styles.BG_DARK,
                     fg=styles.FG_PRIMARY, font=styles.FONT_BODY,
                     anchor="w").pack(side="left", padx=(6, 0))

        # Tags frame (badges)
        self._tags_frame = tk.Frame(meta, bg=styles.BG_DARK)
        self._tags_frame.pack(anchor="w", pady=(8, 0))

        # ── Tracklist ──
        tracklist_header = tk.Frame(parent, bg=styles.BG_DARK)
        tracklist_header.pack(fill="x", pady=(0, 6))
        tk.Frame(tracklist_header, bg=styles.ACCENT_GREEN, width=3, height=16).pack(side="left")
        tk.Label(tracklist_header, text="  Tracklist",
                 bg=styles.BG_DARK, fg=styles.FG_PRIMARY,
                 font=styles.FONT_HEADING).pack(side="left")

        _track_container = tk.Canvas(parent, bg=styles.BG_DARK, highlightthickness=0, bd=0)

        # save album button at the bottom
        self._export_btn = RoundedButton(
            parent, text="Save Album (JSON + PNG)",
            bg=styles.ACCENT_GREEN,
            fg=styles.BG_DARK,
            hover_bg="#0d9e6e",
            font=styles.FONT_LABEL,
            radius=18, padx=20, pady=10,
            master_bg=styles.BG_DARK,
        )
        self._export_btn.pack(side="bottom", fill="x", pady=(12, 0))

        _track_container.pack(fill="both", expand=True)
        track_outer = tk.Frame(_track_container, bg=styles.BG_PANEL)
        _tc_win = _track_container.create_window(6, 6, anchor="nw", window=track_outer)

        def _draw_track_border(event=None):
            cw = _track_container.winfo_width()
            ch = _track_container.winfo_height()
            if cw < 2 or ch < 2:
                return
            _track_container.delete("rr")
            AlbumApp._draw_rr(_track_container, 0, 0, cw, ch, 12,
                               fill=styles.BG_PANEL, outline=styles.BG_PANEL, tags="rr")
            _track_container.tag_lower("rr")
            _track_container.itemconfig(_tc_win, width=cw - 12, height=ch - 12)

        _track_container.bind("<Configure>", _draw_track_border)

        self._track_canvas = tk.Canvas(
            track_outer, bg=styles.BG_PANEL,
            highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(track_outer, orient="vertical",
                                  command=self._track_canvas.yview)
        self._track_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self._track_canvas.pack(side="left", fill="both", expand=True)

        self._track_inner = tk.Frame(self._track_canvas, bg=styles.BG_PANEL)
        self._track_window = self._track_canvas.create_window(
            (0, 0), window=self._track_inner, anchor="nw")

        self._track_inner.bind("<Configure>", self._on_inner_configure)
        self._track_canvas.bind("<Configure>", self._on_canvas_configure)
        self._track_canvas.bind("<Enter>", self._bind_mousewheel)
        self._track_canvas.bind("<Leave>", self._unbind_mousewheel)

        tk.Label(self._track_inner,
                 text="Generate an album to see the tracklist.",
                 bg=styles.BG_PANEL, fg=styles.FG_SECONDARY,
                 font=styles.FONT_BODY, padx=12, pady=20).pack(anchor="w")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _install_placeholder(self, text_widget, placeholder):
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

    @staticmethod
    def _draw_rr(canvas, x1, y1, x2, y2, r, **kw):
        canvas.create_arc(x1,       y1,       x1+2*r, y1+2*r, start=90,  extent=90,  **kw)
        canvas.create_arc(x2-2*r,   y1,       x2,     y1+2*r, start=0,   extent=90,  **kw)
        canvas.create_arc(x1,       y2-2*r,   x1+2*r, y2,     start=180, extent=90,  **kw)
        canvas.create_arc(x2-2*r,   y2-2*r,   x2,     y2,     start=270, extent=90,  **kw)
        canvas.create_rectangle(x1+r, y1,   x2-r, y2,   **kw)
        canvas.create_rectangle(x1,   y1+r, x2,   y2-r, **kw)

    def _make_rounded_box(self, parent, radius=10, pad=4, fill_color=None, canvas_bg=None):
        fill_color = fill_color or styles.BG_CARD
        canvas_bg  = canvas_bg  or styles.BG_PANEL
        canvas = tk.Canvas(parent, bg=canvas_bg, highlightthickness=0, bd=0)
        inner  = tk.Frame(canvas, bg=fill_color)
        win    = canvas.create_window(pad, pad, anchor="nw", window=inner)

        def _redraw():
            cw, ch = canvas.winfo_width(), canvas.winfo_height()
            if cw < 2 or ch < 2:
                return
            canvas.delete("rr")
            AlbumApp._draw_rr(canvas, 0, 0, cw, ch, radius,
                               fill=fill_color, outline=fill_color, tags="rr")
            canvas.tag_lower("rr")

        def _on_canvas_resize(event):
            canvas.itemconfig(win, width=event.width - pad * 2)
            _redraw()

        def _on_inner_resize(event):
            canvas.config(height=inner.winfo_reqheight() + pad * 2)
            _redraw()

        canvas.bind("<Configure>", _on_canvas_resize)
        inner.bind("<Configure>", _on_inner_resize)
        return canvas, inner

    def _on_inner_configure(self, _event=None):
        self._track_canvas.configure(scrollregion=self._track_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self._track_canvas.itemconfig(self._track_window, width=event.width)

    def _bind_mousewheel(self, _event):
        self._track_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self._track_canvas.bind_all("<Button-4>",   self._on_mousewheel)
        self._track_canvas.bind_all("<Button-5>",   self._on_mousewheel)

    def _unbind_mousewheel(self, _event):
        self._track_canvas.unbind_all("<MouseWheel>")
        self._track_canvas.unbind_all("<Button-4>")
        self._track_canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 4:
            self._track_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._track_canvas.yview_scroll(1, "units")
        else:
            self._track_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _clear_tracklist(self):
        for widget in self._track_inner.winfo_children():
            widget.destroy()
        self._track_widgets.clear()

    def _add_track_row(self, index, title, artist, on_listen=None):
        bg = styles.BG_PANEL if index % 2 == 0 else styles.BG_DARK

        row = tk.Frame(self._track_inner, bg=bg, pady=6, padx=12)
        row.pack(fill="x")

        tk.Label(row, text=f"{index:02d}.", bg=bg,
                 fg=styles.FG_SECONDARY, font=styles.FONT_SMALL,
                 width=3, anchor="e").pack(side="left")

        info = tk.Frame(row, bg=bg)
        info.pack(side="left", fill="x", expand=True, padx=(10, 0))
        tk.Label(info, text=title,  bg=bg, fg=styles.FG_PRIMARY,
                 font=styles.FONT_BODY, anchor="w").pack(anchor="w")
        tk.Label(info, text=artist, bg=bg, fg=styles.FG_SECONDARY,
                 font=styles.FONT_SMALL, anchor="w").pack(anchor="w")

        listen_cmd = (lambda u: lambda: webbrowser.open(u))(on_listen) if on_listen else lambda: None
        RoundedButton(row, text="▶  Listen",
                      bg=styles.ACCENT_GREEN_HOVER,
                      fg=styles.ACCENT_GREEN,
                      hover_bg=styles.BG_CARD,
                      font=styles.FONT_SMALL,
                      radius=12, padx=12, pady=4,
                      master_bg=bg,
                      command=listen_cmd).pack(side="right")

        self._track_widgets.append(row)

    def _update_tags(self, tags):
        """Render tag badges in the tags frame."""
        for widget in self._tags_frame.winfo_children():
            widget.destroy()
        if isinstance(tags, list):
            tag_list = tags
        else:
            tag_list = [t.strip() for t in str(tags).split(",") if t.strip()]
        for tag in tag_list:
            tk.Label(self._tags_frame,
                     text=f"#{tag}",
                     bg=styles.ACCENT_GREEN_HOVER,
                     fg=styles.ACCENT_GREEN,
                     font=styles.FONT_SMALL,
                     padx=8, pady=2,
                     relief="flat").pack(side="left", padx=(0, 4))

    # ------------------------------------------------------------------
    # Teammate connection point
    # ------------------------------------------------------------------

    def bind_generate(self, callback):
        self._generate_btn.configure(command=callback)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_journal_text(self) -> str:
        text = self._journal_text.get("1.0", "end-1c").strip()
        placeholder = getattr(self._journal_text, "_placeholder", "")
        return "" if text == placeholder else text

    def get_genre(self) -> str:
        return self._genre_var.get()

    def get_era(self) -> str:
        return self._era_var.get()

    def get_track_count(self) -> int:
        return int(self._track_count_var.get())

    def set_status(self, message: str):
        self._status_var.set(message)
        self.root.update_idletasks()

    def display_album(self, metadata: dict, tracks: list, image=None):
        # Album name
        self._album_name_var.set(metadata.get("name", "Unknown Album"))

        # Mood (italic description)
        mood = metadata.get("mood", "")
        self._mood_var.set(f'"{mood}"' if mood else "")

        # Metadata fields
        for key, var in self._meta_vars.items():
            value = metadata.get(key, "")
            if key == "year":
                count = len(tracks)
                var.set(f"{value} • {count} songs" if value else f"{count} songs")
            else:
                var.set(str(value) if value else "—")

        # Tags as badges
        self._update_tags(metadata.get("tags", []))

        # Cover image
        if image is not None:
            try:
                from PIL import ImageTk
                import image_service
                img_resized = image_service.resize_for_display(image, (160, 160))
                photo = ImageTk.PhotoImage(img_resized)
                self._cover_label.configure(image=photo, text="", width=0, height=0)
                self._current_image = photo
            except Exception:
                self._cover_label.configure(text="[Image unavailable]")

        # Tracklist
        self._clear_tracklist()
        for i, track in enumerate(tracks, start=1):
            title  = track.get("title", "Unknown Title")
            artist = track.get("artist", "")
            url    = track.get("url", None)
            self._add_track_row(i, title, artist, url)

        if not tracks:
            tk.Label(self._track_inner,
                     text="No tracks found for this combination.",
                     bg=styles.BG_PANEL, fg=styles.FG_SECONDARY,
                     font=styles.FONT_BODY, padx=12, pady=20).pack(anchor="w")