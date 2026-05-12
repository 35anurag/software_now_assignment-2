from abc import ABC, abstractmethod
import cv2
import numpy as np
import random

class Alteration(ABC):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def apply(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self._name!r}>"

class BlurAlteration(Alteration):
    def __init__(self):
        super().__init__("Blur")

    def apply(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> None:
        region = image[y:y + h, x:x + w]
        k = max(7, (min(w, h) // 3) | 1)
        blurred = cv2.GaussianBlur(region, (k, k), sigmaX=0)
        image[y:y + h, x:x + w] = blurred

class ColorShiftAlteration(Alteration):
    def __init__(self):
        super().__init__("Colour Shift")

    def apply(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> None:
        region = image[y:y + h, x:x + w]
        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV).astype(np.int16)
        hue_shift = random.choice([-40, -30, 30, 40, 50])
        sat_scale = random.uniform(1.2, 1.6)
        hsv[..., 0] = (hsv[..., 0] + hue_shift) % 180
        hsv[..., 1] = np.clip(hsv[..., 1] * sat_scale, 0, 255)
        shifted = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        image[y:y + h, x:x + w] = shifted

class BrightnessAlteration(Alteration):
    def __init__(self):
        super().__init__("Brightness")

    def apply(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> None:
        region = image[y:y + h, x:x + w].astype(np.int16)
        delta = random.choice([-60, -50, 50, 60, 70])
        region = np.clip(region + delta, 0, 255).astype(np.uint8)
        image[y:y + h, x:x + w] = region

class ShapeAlteration(Alteration):
    def __init__(self):
        super().__init__("Shape")

    def apply(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> None:
        region = image[y:y + h, x:x + w]
        avg = region.reshape(-1, 3).mean(axis=0)
        shift = np.array([random.randint(-70, 70) for _ in range(3)])
        colour = tuple(int(c) for c in np.clip(avg + shift, 0, 255))
        cx, cy = w // 2, h // 2
        radius = max(4, min(w, h) // 3)
        if random.random() < 0.5:
            cv2.circle(region, (cx, cy), radius, colour, thickness=-1)
        else:
            r = max(3, radius - 1)
            cv2.rectangle(region, (cx - r, cy - r), (cx + r, cy + r), colour, thickness=-1)
        image[y:y + h, x:x + w] = region

class PixelateAlteration(Alteration):
    def __init__(self):
        super().__init__("Pixelate")

    def apply(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> None:
        region = image[y:y + h, x:x + w]
        scale = max(4, min(w, h) // 6)
        small = cv2.resize(region, (max(1, w // scale), max(1, h // scale)),
                           interpolation=cv2.INTER_LINEAR)
        pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        image[y:y + h, x:x + w] = pixelated

ALL_ALTERATIONS = [
    BlurAlteration,
    ColorShiftAlteration,
    BrightnessAlteration,
    ShapeAlteration,
    PixelateAlteration,
]
