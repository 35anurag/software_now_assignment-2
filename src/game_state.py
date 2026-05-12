"""
Encapsulates the round state:
    -the list of difference regions for the current image
    -how many the player has found
    -how many mistakes they have made
    -whether the player is locked out (3 mistakes reached)
    -cumulative score across multiple images

Demonstrates:
    -Encapsulation - private fields with read-only properties
    -Constructor / methods / class interaction with DifferenceRegion
"""

from __future__ import annotations
from typing import List, Optional

from difference_generator import DifferenceRegion


class GameState:
    """Tracks the state of the current round and cumulative score."""

    MAX_MISTAKES = 3
    DIFFERENCES_PER_IMAGE = 5

    def __init__(self):
        self._regions: List[DifferenceRegion] = []
        self._mistakes: int = 0
        self._cumulative_found: int = 0   # across all images this session
        self._revealed: bool = False

    # -------- Public read-only properties --------
    @property
    def regions(self) -> List[DifferenceRegion]:
        return list(self._regions)

    @property
    def mistakes(self) -> int:
        return self._mistakes

    @property
    def found_count(self) -> int:
        return sum(1 for r in self._regions if r.found)

    @property
    def remaining_count(self) -> int:
        return len(self._regions) - self.found_count

    @property
    def cumulative_score(self) -> int:
        return self._cumulative_found

    @property
    def is_locked_out(self) -> bool:
        return self._mistakes >= self.MAX_MISTAKES

    @property
    def is_complete(self) -> bool:
        return (len(self._regions) > 0 and
                self.remaining_count == 0)

    @property
    def is_revealed(self) -> bool:
        return self._revealed

    @property
    def can_click(self) -> bool:
        """Whether clicks should be processed at the moment."""
        return (len(self._regions) > 0 and
                not self.is_locked_out and
                not self.is_complete and
                not self._revealed)

    # -------- State mutations --------
    def start_new_round(self, regions: List[DifferenceRegion]) -> None:
        """Reset per-round state and install a new set of regions."""
        self._regions = regions
        self._mistakes = 0
        self._revealed = False

    def register_click(self, x: int, y: int) -> Optional[DifferenceRegion]:
        """
        Returns the region that was hit, or None for a miss.
        Caller is responsible for checking `can_click` first.
        Updates mistakes / found counters.
        """
        for region in self._regions:
            if not region.found and region.contains_point(x, y):
                region.mark_found()
                self._cumulative_found += 1
                return region

        # Miss
        self._mistakes += 1
        return None

    def reveal_all(self) -> List[DifferenceRegion]:
        """Mark the round as revealed and return the still-unfound regions."""
        unfound = [r for r in self._regions if not r.found]
        self._revealed = True
        return unfound
