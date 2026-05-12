import tkinter as tk
from PIL import Image, ImageTk
import cv2


class ImageCanvas(tk.Canvas):
    def __init__(self, parent, width=480, height=480, clickable=False, on_click=None):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg="black",
            highlightthickness=0
        )

        self.width = width
        self.height = height
        self.clickable = clickable
        self.on_click = on_click
        self.tk_image = None

        if clickable:
            self.bind("<Button-1>", self.handle_click)

    def set_image(self, cv_img):
        # Convert OpenCV BGR → RGB
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

        image = Image.fromarray(rgb)
        image = image.resize((self.width, self.height))

        self.tk_image = ImageTk.PhotoImage(image)

        self.delete("all")
        self.create_image(
            self.width // 2,
            self.height // 2,
            image=self.tk_image
        )

    def handle_click(self, event):
        if self.on_click:
            self.on_click(event.x, event.y)

    def draw_circle(self, x, y, r, colour="red", width=3):
        self.create_oval(
            x-r, y-r,
            x+r, y+r,
            outline=colour,
            width=width
        )

    def draw_message(self, text, colour="white"):
        self.create_text(
            self.width // 2,
            self.height // 2,
            text=text,
            fill=colour,
            font=("Arial", 18, "bold")
        )
