# HIT137 Assignment 3 - Spot the Difference

This is our group assignment for HIT137. We made a desktop app where two
images are shown side by side and the player has to find 5 differences
between them by clicking on the modified image.

The app uses Python with Tkinter for the GUI and OpenCV for image
processing.

# How to run it

You need Python 3.9 or above.
First install the libraries:

```
pip install -r requirements.txt
```
Then run the program from the src folder:
```
cd src
python main.py
```

Click "Load Image" and choose a JPG, PNG or BMP file. Then click on the
right image to find the differences.

# Files in this project

```
spot_the_difference/
├── README.md
├── requirements.txt
├── github_link.txt
├── sample_images/
│   ├── sample_gradient.png
│   └── sample_landscape.jpg
└── src/
    ├── main.py                  - starts the program
    ├── app.py                   - main window class
    ├── image_canvas.py          - canvas for showing images
    ├── alterations.py           - the 5 alteration types
    ├── difference_generator.py  - creates the modified image
    └── game_state.py            - tracks score and mistakes
```

## OOP part

We made the program using OOP with these classes:

- `Alteration` - abstract base class for image alterations
- `BlurAlteration`, `ColorShiftAlteration`, `BrightnessAlteration`,
  `ShapeAlteration`, `PixelateAlteration` - the 5 alteration types,
  all inherit from Alteration
- `DifferenceRegion` - holds info about one difference
- `DifferenceGenerator` - makes the modified image with 5 differences
- `GameState` - tracks how many found, how many mistakes
- `ImageCanvas` - extends tk.Canvas to show images and draw circles
- `SpotTheDifferenceApp` - extends tk.Tk, the main window

We used:
- Inheritance - the alteration classes inherit from `Alteration`,
  `ImageCanvas` inherits from `tk.Canvas`, and `SpotTheDifferenceApp`
  inherits from `tk.Tk`
- Polymorphism - every alteration class has its own `apply()`
  method that does something different, but they all get called the
  same way
- Encapsulation - private variables start with `_` and we use
  `@property` to give read-only access
- Constructors - every class has an `__init__` method
- Class interaction - `DifferenceGenerator` uses `Alteration`
  objects, `GameState` uses `DifferenceRegion` objects, and the app
  class uses all of them together

## Image processing part

When an image is loaded, we use OpenCV to:

1. Read the image with `cv2.imread`
2. Make a copy of it using numpy
3. Pick 5 random rectangles that don't overlap
4. Apply a random alteration to each rectangle on the copy

The 5 alteration types are:
- Blur - uses `cv2.GaussianBlur`
- Colour Shift - changes hue and saturation in HSV colour space
- Brightness - adds or subtracts from each pixel
- Shape - draws a small filled circle or rectangle
- Pixelate - shrinks and grows the region with nearest neighbour

Every time you load an image you get different positions and
different alteration types because we use `random.randint` and
`random.sample`.

We make sure the regions don't overlap by checking each new region
against all the existing ones before adding it. We also check that
the alteration actually made a visible change (in case the region
falls on a flat colour area).

## GUI part

The GUI has:
- A "Load Image" button that opens a file dialog
- The original image on the left and the modified image on the right
- A status bar showing remaining differences, mistakes (out of 3),
  and total found across all images
- Click detection on the right image - clicks within 18 pixels of a
  difference count as a hit
- Red circles drawn on both images when you find a difference
- A popup message when you find all 5 differences
- Lockout after 3 mistakes with a red message and popup
- A "Reveal Differences" button that draws blue circles on both
  images for any unfound differences
- Loading a new image resets everything for that round

## Group members

- Member 1: Anurag Regmi
- Member 2: Bibek Pantha
- Member 3: Bibek Khakural
- Member 4: Jack Maloney
