"""
Generates exactly 5 non-overlapping difference regions on a copy of the
original image. Each region is a randomly chosen alteration type at a
randomly chosen position.

Demonstrates:
    Encapsulation     
    Class interaction 
"""

from __future__ import annotations
from typing import List, Tuple, Optional
import random
import numpy as np

from alterations import ALL_ALTERATIONS, Alteration


class DifferenceRegion:
    """
    Plain data class describing a single difference region.
    Holds the rectangle, the alteration that was applied, and whether
    the player has already located it.
    """

    def __init__(self, x: int, y: int, w: int, h: int, alteration: Alteration):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._alteration = alteration
        self._found = False

    # Encapsulation: read-only access 
    @property
    def x(self) -> int: return self._x
    @property
    def y(self) -> int: return self._y
    @property
    def w(self) -> int: return self._w
    @property
    def h(self) -> int: return self._h
    @property
    def alteration(self) -> Alteration: return self._alteration
    @property
    def found(self) -> bool: return self._found

    # Centre of region (used for circles) 
    @property
    def center(self) -> Tuple[int, int]:
        return self._x + self._w // 2, self._y + self._h // 2

    # Bounding-circle radius (used for click tolerance) 
    @property
    def radius(self) -> int:
        return max(self._w, self._h) // 2 + 4

    def mark_found(self) -> None:
        self._found = True

    def contains_point(self, px: int, py: int, tolerance: int = 18) -> bool:
        """
        Return True if the point (px, py) lies within `tolerance` pixels
        of this region (using the bounding rectangle expanded by
        tolerance).
        """
        return (self._x - tolerance <= px <= self._x + self._w + tolerance and
                self._y - tolerance <= py <= self._y + self._h + tolerance)

    def overlaps(self, other: "DifferenceRegion", padding: int = 6) -> bool:
        """Axis-aligned rectangle overlap test with extra padding."""
        return not (self._x + self._w + padding <= other._x or
                    other._x + other._w + padding <= self._x or
                    self._y + self._h + padding <= other._y or
                    other._y + other._h + padding <= self._y)


class DifferenceGenerator:
    """
    Builds the modified image and the list of 5 difference regions.

    Usage:
        gen = DifferenceGenerator(original_bgr)
        modified_bgr, regions = gen.generate()
    """

    NUM_DIFFERENCES = 5
    MIN_REGION = 30          # minimum side length of a region (pixels)
    MAX_REGION = 70          # maximum side length of a region
    BORDER_MARGIN = 10       # keep regions away from image edges
    MAX_PLACEMENT_TRIES = 400

    def __init__(self, original: np.ndarray):
        if original is None or original.size == 0:
            raise ValueError("Original image is empty.")
        self._original = original
        self._height, self._width = original.shape[:2]

    def _pick_alteration_classes(self) -> list:
        """
        Choose NUM_DIFFERENCES alteration classes such that at least
        three DISTINCT alteration types appear in every puzzle.
        """
        # Start with a random sample of distinct types (up to what we have)
        n_distinct = min(len(ALL_ALTERATIONS), self.NUM_DIFFERENCES)
        distinct = random.sample(ALL_ALTERATIONS, n_distinct)

        # Fill remaining slots (if NUM_DIFFERENCES > number of types)
        # with random picks from the full pool
        chosen = list(distinct)
        while len(chosen) < self.NUM_DIFFERENCES:
            chosen.append(random.choice(ALL_ALTERATIONS))

        random.shuffle(chosen)
        return chosen

    def generate(self) -> Tuple[np.ndarray, List[DifferenceRegion]]:
        """
        Returns a (modified_image, regions) tuple.
        Guarantees exactly NUM_DIFFERENCES non-overlapping regions and
        at least 3 distinct alteration types per puzzle.
        """
        modified = self._original.copy()
        regions: List[DifferenceRegion] = []

        # Pre-pick the alteration classes so we control the variety
        alteration_queue = self._pick_alteration_classes()

        attempts = 0
        # Adaptive sizing: shrink max-region for very small images
        max_side = min(self.MAX_REGION,
                       max(self.MIN_REGION + 5,
                           min(self._width, self._height) // 6))
        min_side = min(self.MIN_REGION, max_side - 5)

        while len(regions) < self.NUM_DIFFERENCES:
            attempts += 1
            if attempts > self.MAX_PLACEMENT_TRIES:
                # Image too small / too crowded; relax constraints slightly
                max_side = max(min_side + 4, max_side - 2)
                attempts = 0
                if max_side <= min_side:
                    raise RuntimeError(
                        "Image too small to fit 5 non-overlapping regions."
                    )

            w = random.randint(min_side, max_side)
            h = random.randint(min_side, max_side)
            x = random.randint(self.BORDER_MARGIN,
                               self._width - w - self.BORDER_MARGIN)
            y = random.randint(self.BORDER_MARGIN,
                               self._height - h - self.BORDER_MARGIN)

            # Use the next pre-chosen alteration class so we guarantee
            # at least 3 distinct types per puzzle.
            alteration_cls = alteration_queue[len(regions)]
            alteration = alteration_cls()

            candidate = DifferenceRegion(x, y, w, h, alteration)

            if any(candidate.overlaps(r) for r in regions):
                continue

            # Apply the alteration to a temporary copy first; if the
            # change is imperceptible (e.g. blur on a near-uniform
            # region) try a different position rather than producing
            # an "invisible" difference.
            preview = modified.copy()
            alteration.apply(preview, x, y, w, h)
            diff = np.abs(
                preview[y:y + h, x:x + w].astype(np.int16)
                - modified[y:y + h, x:x + w].astype(np.int16)
            ).mean()
            if diff < 4.0:
                continue  # too subtle to see; pick another spot

            modified = preview
            regions.append(candidate)

        return modified, regions
