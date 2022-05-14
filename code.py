# SPDX-FileCopyrightText: 2020 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# This example implements a simple two line scroller using
# Adafruit_CircuitPython_Display_Text. Each line has its own color
# and it is possible to modify the example to use other fonts and non-standard
# characters.

import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
import time
import adafruit_imageload
from digitalio import DigitalInOut, Direction, Pull
from rainbowio import colorwheel
from adafruit_display_text import bitmap_label as label
import gc


gc.enable()
MATRIX_SIZE = 64

displayio.release_displays()

# Configure matrix
matrix = rgbmatrix.RGBMatrix(
    width=MATRIX_SIZE, height=MATRIX_SIZE, bit_depth=6,
    rgb_pins=[board.MTX_R1, board.MTX_G1, board.MTX_B1, board.MTX_R2, board.MTX_G2, board.MTX_B2],
    addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD, board.MTX_ADDRE],
    clock_pin=board.MTX_CLK, latch_pin=board.MTX_LAT, output_enable_pin=board.MTX_OE)

# Configure Button UP
button_up = DigitalInOut(board.BUTTON_UP)
button_up.direction = Direction.INPUT
button_up.pull = Pull.UP

# Configure Button DOWN
button_down = DigitalInOut(board.BUTTON_DOWN)
button_down.direction = Direction.INPUT
button_down.pull = Pull.UP

# Associate the RGB matrix with a Display so that we can use displayio features
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

class AnimationBmp():
    def __init__(self, bmp_file, bmp_size, fps=30, frame_count=10, x=0, y=0, scale=1, animations=[]):
        self.t = 0
        self.i = 0
        self.fps = fps
        self.frame_count = frame_count
        self.bmp_file = bmp_file
        self.bmp_size = bmp_size
        self.MATRIX_SIZE = 64
        self.animations = animations
        self.x = x
        self.y = y
        self.scale = scale

    def load(self, group):
        for a in self.animations:
            a.load(group)

        bitmap = displayio.OnDiskBitmap(self.bmp_file)
        self.grid = displayio.TileGrid(bitmap,
                                  pixel_shader=bitmap.pixel_shader,
                                  width=1,
                                  height=1,
                                  tile_height=self.bmp_size,
                                  tile_width=self.bmp_size,
                                  default_tile=0,
                                  x=self.x,
                                  y=self.y)

        subgroup = displayio.Group(scale=self.scale) #int(self.MATRIX_SIZE/self.bmp_size))
        subgroup.append(self.grid)

        group.append(subgroup)

    def update(self):
        for a in self.animations:
            a.update()

        if (time.monotonic() > self.t + 1/self.fps):
            self.i += 1
            if (self.i >= self.frame_count):
                self.i = 0
            self.grid[0] = self.i
            self.t = time.monotonic()

class AnimationBmpText(AnimationBmp):
    def __init__(self, bmp_file, bmp_size, fps=30, frame_count=10, x=0, y=0, scale=1, animations=[]):
        super().__init__(bmp_file, bmp_size, fps=fps, frame_count=frame_count, x=x, y=y, scale=scale, animations=animations)

    def load(self, group):
        super().load(group)

        # text = label.Label(terminalio.FONT,
        #              color=0xFF0000,
        #              background_color=None,
        #              background_tight=True,
        #              text="@jjasmine47")
        text = label.Label(terminalio.FONT,
                     color=0x00FFFF,
                     background_color=0x000000,
                     background_tight=True,
                     text="congrats!")
        text.x = 10
        text.y = 10

        group.append(text)

        text_2022 = label.Label(terminalio.FONT,
                         color=0xFF00FF,
                         background_color=0x000000,
                         background_tight=True,
                         text="2022")

        text_2022.x = 21
        text_2022.y = 50
        group.append(text_2022)

animations = [
    #AnimationBmp("starry_night_gamma.bmp", 64, frame_count=1),
     #AnimationBmp("tear-processed.bmp", 64, frame_count=1, fps=1),
    #AnimationBmpText("self-processed.bmp", 64, frame_count=1, fps=1)
    #AnimationBmp("fire.bmp", 64, frame_count=20, fps=5)
    AnimationBmpText("fireworks.bmp", 64, frame_count=10),
     #AnimationBmp("brown.bmp", 64, frame_count=2, fps=5),
    #AnimationBmp("parrot.bmp", 32, frame_count=10, fps=3, animations=[
    #        AnimationBmp("parrot.bmp", 32, frame_count=10, x=32, fps=6),
    #        AnimationBmp("parrot.bmp", 32, frame_count=10, y=32, fps=9),
    #        AnimationBmp("parrot.bmp", 32, frame_count=10, x=32, y=32, fps=12)
    #    ]
    #),
]

current_ani_idx = 0
animation = animations[current_ani_idx]
animation_time = 10 # seconds to display each animation

def load_animation(idx):
    global animation
    global current_ani_idx

    print("Loading animation index", idx)
    if (idx >= 0 and idx < len(animations)):
        current_ani_idx = idx
        animation = animations[idx]

        group = displayio.Group(scale=1)
        animation.load(group)
        display.show(group)

    gc.collect()
    #print("Free bytes:", gc.mem_free())

load_animation(0)

button_up_prev = button_up.value
button_down_prev = button_down.value

main_time = time.monotonic()

while True:
    # Update matrix display
    animation.update()
    display.refresh(minimum_frames_per_second=0)

    # Update button press
    # On button release
    if not button_up_prev and button_up.value:
        print("button_up")
        grid = load_animation((current_ani_idx + 1) % len(animations))
        main_time = time.monotonic()


    # On button release
    if not button_down_prev and button_down.value:
        print("button_down")
        grid = load_animation((current_ani_idx - 1) % len(animations))
        main_time = time.monotonic()

    button_up_prev = button_up.value
    button_down_prev = button_down.value

    if (animation_time) and (time.monotonic() > main_time + animation_time):
        print("timer for animation")
        grid = load_animation((current_ani_idx + 1) % len(animations))
        main_time = time.monotonic()



