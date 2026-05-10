# HIT137 Group Assignment 3 — Spot the Difference

A desktop application built with **Python**, **Tkinter** and **OpenCV** that
generates "spot the difference" puzzles from any image the user supplies.

When the user loads an image, the program creates an exact clone, then
introduces **exactly 5** randomly placed, **non-overlapping** differences using
one of several OpenCV-based alteration techniques. The two images are shown
side by side and the player tries to find the differences by clicking on the
modified image on the right.

---

## How to run

1. Install the dependencies (Python 3.9 or newer recommended):

   ```bash
   pip install -r requirements.txt
   ```

2. Run the application from the `src/` directory:

   ```bash
   cd src
   python main.py
   ```

3. Click **Load Image**, choose any JPG / PNG / BMP file (a 220 px minimum on
   the shorter side is recommended), then click on the right-hand image to
   start finding differences.

---

## Project structure

```
spot_the_difference/
├── README.md
├── requirements.txt
├── github_link.txt
└── src/
    ├── main.py                    # Entry point
    ├── app.py                     # SpotTheDifferenceApp (extends tk.Tk)
    ├── image_canvas.py            # ImageCanvas (extends tk.Canvas)
    ├── alterations.py             # Alteration ABC + 5 concrete subclasses
    ├── difference_generator.py    # DifferenceGenerator + DifferenceRegion
    └── game_state.py              # GameState (scores / mistakes / lockout)
```

---

## OOP design overview

The codebase is organised into **6 classes across 5 modules**, comfortably
exceeding the rubric's "at least three classes" requirement.

| Class | Module | Responsibility | OOP features demonstrated |
|---|---|---|---|
| `Alteration` (abstract) | `alterations.py` | Defines the polymorphic interface for image alterations | Abstract base class, encapsulation, abstract method |
| `BlurAlteration`, `ColorShiftAlteration`, `BrightnessAlteration`, `ShapeAlteration`, `PixelateAlteration` | `alterations.py` | Five concrete alteration types | **Inheritance** (from `Alteration`), **polymorphism** (override `apply()`), constructor chaining via `super().__init__()` |
| `DifferenceRegion` | `difference_generator.py` | Plain data class for a single difference | Encapsulation (private attrs + read-only properties) |
| `DifferenceGenerator` | `difference_generator.py` | Builds the modified image with 5 non-overlapping regions | **Class interaction** with `Alteration` subclasses (polymorphic `apply()`), encapsulation |
| `GameState` | `game_state.py` | Per-round and cumulative score/mistake tracking | Encapsulation (private state, read-only props), constructor, methods |
| `ImageCanvas` | `image_canvas.py` | Custom canvas widget that displays scaled images and circles | **Inheritance** from `tk.Canvas`, encapsulation of scaling logic |
| `SpotTheDifferenceApp` | `app.py` | Main GUI window | **Inheritance** from `tk.Tk`, composes all other classes |

### Inheritance & polymorphism in practice

- All five alteration classes inherit from the abstract `Alteration` base
  class. Each overrides the `apply(image, x, y, w, h)` method differently,
  but the `DifferenceGenerator` calls them through the same base-class
  interface — that's polymorphism.
- `ImageCanvas` extends `tk.Canvas` and adds image-scaling and circle-drawing
  methods while still behaving as a regular Tk canvas.
- `SpotTheDifferenceApp` extends `tk.Tk` and customises the top-level window.

### Encapsulation in practice

Internal state in every class is stored in attributes prefixed with `_` and
exposed only through read-only `@property` accessors (e.g.
`GameState.remaining_count`, `DifferenceRegion.center`). Mutations go through
explicit methods such as `start_new_round`, `register_click`, or
`mark_found`, which keeps the rest of the program from accidentally
corrupting state.

---

## Image processing details (OpenCV)

When an image is loaded:

1. The image is read with `cv2.imread` (supports JPG, PNG, BMP).
2. An **exact clone** is created with `numpy.copy`.
3. `DifferenceGenerator` selects 5 alteration *classes* such that **at
   least three distinct types** appear in every puzzle (in fact all 5 of
   our types appear by default since we have exactly 5).
4. For each alteration, a random rectangle (size 30–70 px, kept clear of
   image borders) is placed on the clone.
5. **Non-overlap is guaranteed** — every candidate rectangle is checked for
   overlap (with a small padding) against all previously placed regions
   and rejected if it collides.
6. **Visibility check** — after applying, the mean per-pixel difference is
   measured; regions whose change is too subtle to see (e.g. a blur on a
   completely flat colour patch) are rejected and a new spot is tried.
7. All 5 differences are generated **before** the player sees the modified
   image, and both **type** and **position** are randomised on every load.

### Alteration types

| Type | What it does |
|---|---|
| **Blur** | Gaussian blur (`cv2.GaussianBlur`) with kernel scaled to region size |
| **Colour Shift** | Hue + saturation shift in HSV space (`cv2.cvtColor`) |
| **Brightness** | Adds/subtracts a delta from each channel (clipped to 0–255) |
| **Shape** | Stamps a filled circle or rectangle in a slightly-shifted colour |
| **Pixelate** | Down-scale + nearest-neighbour up-scale |

All manipulation is performed using OpenCV / NumPy operations as required.

---

## GUI features (Tkinter)

- **Load Image** button opens a file dialog filtered to JPG / PNG / BMP.
- Original and modified images are shown **side by side**, both scaled to
  fit a 480 × 480 canvas while **preserving aspect ratio**.
- Loading a new image **resets** the per-round state (mistakes, locks,
  reveal flag) but keeps the cumulative `Total Found` score.
- Clicks are processed only on the right-hand canvas (encoded by the
  `clickable` flag on `ImageCanvas`); coordinates are translated back to
  image space before being checked against difference regions.
- A **tolerance of 18 pixels** is applied to clicks so the player doesn't
  have to pixel-hunt.
- On a hit, a **red circle** is drawn on **both** images at the difference
  location, and the `Remaining` counter and `Total Found` score update
  immediately.
- On a miss, the `Mistakes` counter increments. When mistakes reach **3**,
  clicks are disabled, an on-canvas red overlay is shown, and a popup
  informs the player how many they found.
- When **all 5 differences are found**, a popup notifies the player and
  the on-screen hint suggests loading another image.
- A **Reveal Differences** button draws **blue circles** on both images
  for every still-unfound difference and updates `Remaining` to 0.
- The bottom hint label gives clear, contextual instructions at every
  stage.

---

## Group contributions

This section should be filled in by the group when submitting. Use the
GitHub commit history as the canonical record of contributions per the
assignment instructions.

- *Member 1*: …
- *Member 2*: …
- *Member 3*: JACK MALONEY
- *Member 4*: …
