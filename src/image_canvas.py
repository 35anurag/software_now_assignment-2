"""
A custom Tkinter canvas that displays a (possibly scaled) image and
draws coloured circles around difference regions.

Demonstrates:
    * Inheritance  - subclasses tkinter.Canvas
    * Encapsulation - hides scaling / rendering details
    * Polymorphism - overrides Canvas behaviour by adding draw_circle
"""

from __future__ import annotations
import tkinter as tk
from typing import Callable, Optional, Tuple
from PIL import Image, ImageTk
import cv2
import numpy as np


class ImageCanvas(tk.Canvas):
    """
    A Tk Canvas that knows how to:
      * display an OpenCV (BGR) image scaled to fit while preserving
        aspect ratio,
      * draw red / blue circles in image coordinates,
      * report click positions in image coordinates (via callback).
    """

    def __init__(self, parent, width: int, height: int,
                 clickable: bool = False,
                 on_click: Optional[Callable[[int, int], None]] = None,
                 **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg="#1e1e1e", highlightthickness=1,
                         highlightbackground="#444", **kwargs)

        self._target_w = width
        self._target_h = height

        self._cv_image: Optional[np.ndarray] = None    # original BGR
        self._tk_image: Optional[ImageTk.PhotoImage] = None
        self._scale: float = 1.0      # display / image
        self._offset_x: int = 0       # image top-left in canvas coords
        self._offset_y: int = 0
        self._displayed_w: int = 0
        self._displayed_h: int = 0

        self._clickable = clickable
        self._on_click = on_click

        if clickable:
            self.bind("<Button-1>", self._handle_click)

    # ---------- Public API ----------
    def set_image(self, cv_image: np.ndarray) -> None:
        """Replace the displayed image (BGR numpy array)."""
        self._cv_image = cv_image
        self._render()

    def clear_overlays(self) -> None:
        """Remove all circles / text but keep the base image."""
        self.delete("overlay")

    def draw_circle(self, image_x: int, image_y: int, image_radius: int,
                    colour: str = "red", width: int = 3) -> None:
        """Draw a circle in image coordinates."""
        if self._cv_image is None:
            return
        cx = self._offset_x + int(image_x * self._scale)
        cy = self._offset_y + int(image_y * self._scale)
        r = max(6, int(image_radius * self._scale))
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         outline=colour, width=width, tags="overlay")

    def draw_message(self, text: str, colour: str = "white") -> None:
        """Draw a centred message overlay (used for lockout)."""
        cx = self._target_w // 2
        cy = self._target_h - 30
        self.create_rectangle(0, cy - 22, self._target_w, cy + 22,
                              fill="#000000", outline="",
                              stipple="gray50", tags="overlay")
        self.create_text(cx, cy, text=text, fill=colour,
                         font=("Helvetica", 12, "bold"), tags="overlay")

    # ---------- Internal helpers ----------
    def _render(self) -> None:
        """Compute scale + offsets, blit image onto the canvas."""
        self.delete("all")
        if self._cv_image is None:
            return

        h, w = self._cv_image.shape[:2]
        scale = min(self._target_w / w, self._target_h / h)
        new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))

        # Convert BGR -> RGB and resize using OpenCV (high quality)
        resized = cv2.resize(self._cv_image, (new_w, new_h),
                             interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        self._tk_image = ImageTk.PhotoImage(pil_img)

        self._scale = scale
        self._displayed_w = new_w
        self._displayed_h = new_h
        self._offset_x = (self._target_w - new_w) // 2
        self._offset_y = (self._target_h - new_h) // 2

        self.create_image(self._offset_x, self._offset_y,
                          image=self._tk_image, anchor="nw")

    def _handle_click(self, event) -> None:
        if self._cv_image is None or self._on_click is None:
            return

        # Translate canvas coordinates back to image coordinates
        ix = (event.x - self._offset_x) / self._scale
        iy = (event.y - self._offset_y) / self._scale

        h, w = self._cv_image.shape[:2]
        if 0 <= ix < w and 0 <= iy < h:
            self._on_click(int(ix), int(iy))
