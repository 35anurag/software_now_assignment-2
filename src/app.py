
"""
The main Tkinter application: ties together GameState,
DifferenceGenerator, and two ImageCanvas widgets.

Demonstrates:
    Inheritance      
    Encapsulation    
    Class interaction 
"""

from __future__ import annotations
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional

import cv2
import numpy as np

from difference_generator import DifferenceGenerator, DifferenceRegion
from game_state import GameState
from image_canvas import ImageCanvas


class SpotTheDifferenceApp(tk.Tk):
    """
    Top-level Tkinter application window.

    Inherits from `tk.Tk` (inheritance) and demonstrates polymorphism by
    overriding default behaviour (e.g., custom title bar text, custom
    layout). Composes a GameState and two ImageCanvas widgets.
    """

    CANVAS_W = 480
    CANVAS_H = 480

    SUPPORTED_EXTS = [
        ("Image files", "*.jpg *.jpeg *.png *.bmp"),
        ("JPEG", "*.jpg *.jpeg"),
        ("PNG", "*.png"),
        ("Bitmap", "*.bmp"),
        ("All files", "*.*"),
    ]

    def __init__(self):
        super().__init__()
        self.title("HIT137 - Spot the Difference")
        self.configure(bg="#2b2b2b")
        self.resizable(False, False)

        # --- Encapsulated state ---
        self._game = GameState()
        self._original: Optional[np.ndarray] = None
        self._modified: Optional[np.ndarray] = None
        self._current_path: Optional[str] = None

        self._build_ui()
        self._refresh_status()

    
    # UI construction

    def _build_ui(self) -> None:
        # Style for ttk widgets
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TButton", padding=6, font=("Helvetica", 10, "bold"))
        style.configure("Info.TLabel", background="#2b2b2b",
                        foreground="#f5f5f5", font=("Helvetica", 11, "bold"))
        style.configure("Header.TLabel", background="#2b2b2b",
                        foreground="#fafafa", font=("Helvetica", 14, "bold"))

        # Top bar with controls
        top = tk.Frame(self, bg="#2b2b2b")
        top.pack(fill="x", padx=10, pady=(10, 4))

        ttk.Button(top, text="Load Image",
                   command=self._on_load).pack(side="left", padx=(0, 6))
        self._reveal_btn = ttk.Button(top, text="Reveal Differences",
                                      command=self._on_reveal,
                                      state="disabled")
        self._reveal_btn.pack(side="left", padx=6)
        ttk.Button(top, text="Quit",
                   command=self.destroy).pack(side="right")

        # Status row
        status = tk.Frame(self, bg="#2b2b2b")
        status.pack(fill="x", padx=10, pady=4)

        self._remaining_var = tk.StringVar(value="Remaining: -")
        self._mistakes_var = tk.StringVar(value="Mistakes: 0 / 3")
        self._score_var = tk.StringVar(value="Total Found: 0")
        self._file_var = tk.StringVar(value="No image loaded")

        ttk.Label(status, textvariable=self._remaining_var,
                  style="Info.TLabel").pack(side="left", padx=(0, 18))
        ttk.Label(status, textvariable=self._mistakes_var,
                  style="Info.TLabel").pack(side="left", padx=18)
        ttk.Label(status, textvariable=self._score_var,
                  style="Info.TLabel").pack(side="left", padx=18)
        ttk.Label(status, textvariable=self._file_var,
                  style="Info.TLabel").pack(side="right")

        # Headers
        headers = tk.Frame(self, bg="#2b2b2b")
        headers.pack(fill="x", padx=10)
        ttk.Label(headers, text="Original (reference)",
                  style="Header.TLabel").pack(side="left",
                                               expand=True)
        ttk.Label(headers, text="Modified (click to find)",
                  style="Header.TLabel").pack(side="left",
                                               expand=True)

        # Canvases
        canvas_frame = tk.Frame(self, bg="#2b2b2b")
        canvas_frame.pack(padx=10, pady=8)

        self._left_canvas = ImageCanvas(
            canvas_frame, width=self.CANVAS_W, height=self.CANVAS_H,
            clickable=False)
        self._left_canvas.pack(side="left", padx=(0, 6))

        self._right_canvas = ImageCanvas(
            canvas_frame, width=self.CANVAS_W, height=self.CANVAS_H,
            clickable=True, on_click=self._on_image_click)
        self._right_canvas.pack(side="left", padx=(6, 0))

        # Bottom hint
        self._hint_var = tk.StringVar(
            value="Load an image (JPG / PNG / BMP) to begin.")
        ttk.Label(self, textvariable=self._hint_var,
                  style="Info.TLabel").pack(pady=(0, 10))


    # Event handlers
    def _on_load(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose an image",
            filetypes=self.SUPPORTED_EXTS,
        )
        if not path:
            return

        # cv2.imread fails silently on bad paths / unsupported formats
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is None:
            messagebox.showerror(
                "Could not load image",
                f"Failed to read:\n{path}\n\n"
                "Make sure the file is a valid JPG / PNG / BMP.")
            return

        # Reasonable lower bound so 5 regions fit
        h, w = img.shape[:2]
        if min(h, w) < 220:
            messagebox.showwarning(
                "Image too small",
                "Please choose an image at least 220 pixels on the "
                "shorter side so the differences fit comfortably.")
            return

        try:
            generator = DifferenceGenerator(img)
            modified, regions = generator.generate()
        except RuntimeError as exc:
            messagebox.showerror("Could not generate puzzle", str(exc))
            return

        # New round - reset everything
        self._original = img
        self._modified = modified
        self._current_path = path
        self._game.start_new_round(regions)

        self._left_canvas.set_image(self._original)
        self._right_canvas.set_image(self._modified)
        self._reveal_btn.configure(state="normal")
        self._file_var.set(f"File: {os.path.basename(path)}")
        self._hint_var.set(
            "Click on the right-hand image to find the 5 differences.")
        self._refresh_status()

    def _on_image_click(self, image_x: int, image_y: int) -> None:
        if not self._game.can_click:
            return

        hit = self._game.register_click(image_x, image_y)

        if hit is not None:
            cx, cy = hit.center
            r = hit.radius
            # Draw red circle on BOTH images
            self._left_canvas.draw_circle(cx, cy, r, colour="#ff3030", width=3)
            self._right_canvas.draw_circle(cx, cy, r, colour="#ff3030", width=3)
            self._refresh_status()

            if self._game.is_complete:
                self._hint_var.set(
                    "All 5 differences found - well done! "
                    "Load another image to keep playing.")
                messagebox.showinfo(
                    "All differences found!",
                    "You found all 5 differences in this image. "
                    "Load another image to continue playing.")
        else:
            self._refresh_status()
            if self._game.is_locked_out:
                self._handle_lockout()

    def _on_reveal(self) -> None:
        if not self._game.regions:
            return
        unfound = self._game.reveal_all()
        for region in unfound:
            cx, cy = region.center
            r = region.radius
            # Blue circles on BOTH images
            self._left_canvas.draw_circle(cx, cy, r,
                                          colour="#3aa6ff", width=3)
            self._right_canvas.draw_circle(cx, cy, r,
                                           colour="#3aa6ff", width=3)
        self._refresh_status()
        self._hint_var.set("Differences revealed. Load a new image to "
                           "restart.")

    # Helpers
    def _handle_lockout(self) -> None:
        found = self._game.found_count
        total = len(self._game.regions)
        msg = (f"Too many incorrect guesses!\n\n"
               f"You found {found} of {total} differences.\n"
               f"Load a new image to restart.")
        self._right_canvas.draw_message(
            "Locked out - 3 mistakes reached", colour="#ff8080")
        self._hint_var.set(
            f"Locked out: found {found}/{total}. Load a new image.")
        messagebox.showwarning("Out of guesses", msg)

    def _refresh_status(self) -> None:
        if self._game.regions:
            self._remaining_var.set(
                f"Remaining: {self._game.remaining_count}")
        else:
            self._remaining_var.set("Remaining: -")
        self._mistakes_var.set(
            f"Mistakes: {self._game.mistakes} / "
            f"{self._game.MAX_MISTAKES}")
        self._score_var.set(f"Total Found: {self._game.cumulative_score}")
