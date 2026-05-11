"""
A custom Tkinter canvas that displays a (possibly scaled) image and
draws coloured circles around difference regions.

Demonstrates:
    * Inheritance   - subclasses tkinter.Canvas
    * Encapsulation - hides scaling / rendering details
    * Polymorphism  - overrides Canvas behaviour by adding draw_circle
"""

from __future__ import annotations
import tkinter as tk
from typing import Callable, Optional
from PIL import Image, ImageTk
import cv2
import numpy as np

class ImageCanvas(tk.Canvas):
    """
    A Tk Canvas that knows how to:
    * display an OpenCV (BGR) image scaled to fit while preserving aspect ratio,
    * draw red / blue circles in image coordinates,
    * report click positions in image coordinates (via callback).
    """
    def __init__(self, parent, width: int, height: int, 
                 clickable: bool = False, 
                 on_click: Optional[Callable[[int, int], None]] = None, 
                 **kwargs):
        # Initialize the parent tk.Canvas
        super().__init__(parent, width=width, height=height, **kwargs)
        self.width = width
        self.height = height
        self.clickable = clickable
        self.on_click = on_click
        self.img_tk = None
        self.scale = 1.0

        # Bind the left-click event if clickable is True
        if self.clickable:
            self.bind("<Button-1>", self._handle_click)

    def set_image(self, cv_img):
        """Processes and displays an OpenCV image on the canvas."""
        # Convert OpenCV BGR format to RGB format for PIL
        cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, _ = cv_img_rgb.shape

        # Calculate scaling to fit the canvas while maintaining aspect ratio
        self.scale = min(self.width / w, self.height / h)
        new_w, new_h = int(w * self.scale), int(h * self.scale)
        
        # Resize image and convert to a format Tkinter understands
        pil_img = Image.fromarray(cv_img_rgb).resize((new_w, new_h))
        self.img_tk = ImageTk.PhotoImage(image=pil_img)
        
        # Clear canvas and draw the new image
        self.delete("all")
        self.create_image(0, 0, anchor=tk.NW, image=self.img_tk)

    def draw_circle(self, x: int, y: int, radius: int = 5, color: str = "red"):
        """Draws a circle based on original image coordinates."""
        # Convert original image coordinates to the current canvas scale
        cx, cy = x * self.scale, y * self.scale
        self.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, 
                         outline=color, width=2)

    def _handle_click(self, event):
        """Translates a canvas click back into original image coordinates."""
        if self.on_click:
            # Convert canvas click (event.x) back to original image coordinate
            img_x, img_y = int(event.x / self.scale), int(event.y / self.scale)
            self.on_click(img_x, img_y)

# --- APPLICATION ENTRY POINT ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("HIT137 - Image Analysis Tool")

    # 1. Create a sample image using NumPy (a dark gray background)
    # 400 pixels high, 600 pixels wide
    sample_img = np.full((400, 600, 3), 40, dtype=np.uint8)
    
    # 2. Draw a simple shape on the image using OpenCV to show it works
    cv2.putText(sample_img, "Click to draw circles!", (50, 200), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # 3. Define what happens when we click
    def click_event_handler(x, y):
        print(f"Image Coordinate Clicked: x={x}, y={y}")
        # Draw a blue circle at the click location
        canvas.draw_circle(x, y, radius=8, color="blue")

    # 4. Create the custom canvas
    canvas = ImageCanvas(root, width=800, height=500, clickable=True, on_click=click_event_handler)
    canvas.pack(padx=20, pady=20)

    # 5. Load the image into the canvas
    canvas.set_image(sample_img)

    root.mainloop()