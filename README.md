## Looky: a simple fixation target program

### Installation instructions

These instructions assume that you are using the [Anaconda](https://www.anaconda.com/) or [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main) Python distributions. Apart from Python's base libraries, looky requires [pygame](https://www.pygame.org/wiki/GettingStarted) and [watchdog](https://pypi.org/project/watchdog/). Python >=3.14 breaks some pygame functionality, so please strict the Python version to <=3.13.

#### To install:

1. Create a virtual environment called **looky**: `conda create -n looky python=3.13`
2. Activate the **looky** environment: `conda activate looky`
3. Install **pygame** using pip: `pip install pygame`
4. Install **watchdog** using pip (`pip install watchdog`) or conda (`conda install watchdog`)
5. Clone this repo into your a folder that's in your PYTHONPATH. In CHOIR labs, this will typically be `/home/user/code` or `c:\code`. Move into the desired folder and issue `git clone https://github.com/rjonnal/looky`
6. Edit `config.py` as necessary. In particular, set the value of `data_monitoring_folder` to a real folder in your filesystem where the acquired images will be written.
7. If setting `user_window = True` in `config.py`, please install `matplotlib` with `conda install matplotlib`.

#### To run:

1. Activate the **looky** environment: `conda activate looky`
2. Run: `python looky.py`

### Keyboard shortcuts

<kbd>Up</kbd>: Move target up.

<kbd>Down</kbd>: Move target down.

<kbd>Left</kbd>: Move target left.

<kbd>Right</kbd>: Move target right.

<kbd>Shift</kbd>+<kbd>Up</kbd>: Move target up (small step).

<kbd>Shift</kbd>+<kbd>Down</kbd>: Move target down (small step).

<kbd>Shift</kbd>+<kbd>Left</kbd>: Move target left (small step).

<kbd>Shift</kbd>+<kbd>Right</kbd>: Move target right (small step).

<kbd>Alt</kbd>+<kbd>Up</kbd>: Move origin up.

<kbd>Alt</kbd>+<kbd>Down</kbd>: Move origin down.

<kbd>Alt</kbd>+<kbd>Left</kbd>: Move origin left.

<kbd>Alt</kbd>+<kbd>Right</kbd>: Move origin right.

<kbd>Alt</kbd>+<kbd>Shift</kbd>+<kbd>Up</kbd>: Move origin up (small step).

<kbd>Alt</kbd>+<kbd>Shift</kbd>+<kbd>Down</kbd>: Move origin down (small step).

<kbd>Alt</kbd>+<kbd>Shift</kbd>+<kbd>Left</kbd>: Move origin left (small step).

<kbd>Alt</kbd>+<kbd>Shift</kbd>+<kbd>Right</kbd>: Move origin right (small step).

<kbd>Shift</kbd>+<kbd>f</kbd>: Brighten the target.

<kbd>f</kbd>: Darken the target.

<kbd>Shift</kbd>+<kbd>b</kbd>: Brighten the background.

<kbd>b</kbd>: Darken the background.

<kbd>i</kbd>: Toggle inset image/video, e.g. dead leaves animation.

<kbd>Ctrl</kbd>+<kbd>i</kbd>: Cycle through inset options.

<kbd>Ctrl</kbd>+<kbd>t</kbd>: Cycle through target options.

<kbd>PageDown</kbd>: Next location in location script.

<kbd>PageUp</kbd>: Previous location in location script.

<kbd>o</kbd>: Run the Python script located at `config.external_script_o`.

<kbd>p</kbd>: Run the Python script located at `config.external_script_p`.

<kbd>Escape</kbd> or <kbd>q</kbd>: Quit.

<kbd>w</kbd>: Write a test file to `data_monitoring_folder` to see if data monitoring and auto-advancing are functioning correctly.

### Location scripts

If the folder containing `looky.py` contains another Python file called `location_script.py`, then looky will try to import `location_script` from `location_script` (i.e., `location_script.py` should express a variable called `location_script`). That variable should define a list of `(x,y)` tuples, where each value of `x` and `y` is a retinal eccentricity in degrees. In looky, the script can be navigated using the <kbd>PageUp</kbd> and <kbd>PageDown</kbd> keys.

### Config file `config.py` settings

#### Data monitorning and auto-advance

Some parameters to set up data monitoring and auto-advance:

```
data_monitoring = True
data_monitoring_folder = '/home/rjonnal/code/looky/testing'
data_monitoring_extensions = ['.unp']
auto_advance = True # automatically advance the script index when new data is detected
```

If `data_monitoring` is `True`, **looky** will monitor the folder `data_monitoring_folder` recursively to see if any files are written there. If a file is written there, its extension is compared to the items in the list `data_monitoring_extensions`, and if it matches one of those, **looky** writes the current location (retinal eccentricity) to a file accompanying the newly written data file.

If `auto_advance` is `True`, then **looky** will automatically go to the next location in the location script whenever new data is written to the `data_monitoring_folder` matching one of the extensions in `data_monitoring_extensions`.

#### External scripts

The variables `config.external_script_o` and `config.external_script_p` can be set to Python scripts that are to be run from the **looky** interface, using the <kbd>o</kbd> and <kbd>p</kbd> keys, respectively.

#### User window

If `user_window = True`, **looky** will generate a small version of the fixation target in a separate window, showing the origin, target location, and eccentricity message. This requires installation of `matplotlib`.

#### Beeps

To configure **looky** to beep when the target moves, set `config.beep` to the location of a wav audio file. Two are included in `/data/wavs`. Set `config.beep = None` to silence looky.

#### Dead leaves configuration

Some basic parameters for setting up the inset screen:

```
inset_background_color = (127, 127, 127)
inset_width_deg = 18.0
inset_height_deg = 6.0
inset_x_deg = 0.0
inset_y_deg = 3.0
```

The average ellipse radius, major or minor axis:
```
deadleaves_rad_mean_deg = 0.25
```

The standard deviation of ellipse radius:
```
deadleaves_rad_std_deg = 0.2
```

The number of ellipses; this is effectively calculated from the inset size and the average size of the leaves:
```
deadleaves_n_ellipses = int(inset_width_deg*inset_height_deg/deadleaves_rad_mean_deg**2)
```

The full range of contrast for the dead leaves. 255 means that the maximum inversion amplitude will be 255 gray levels, i.e. oscillating between 0 and 255:
```
deadleaves_gray_range = 255
```

The mean gray level for the leaves:
```
deadleaves_gray_mean = 127
```

The flip frequency for the contrast inversions. This is twice the full-cycle frequency, but the full-cycle frequency isn't as important as the flip frequency. The flip frequency is the carrier frequency for downstream analysis.
```
deadleaves_frequency = 6
```

A random seed for the deadleaves images.
```
deadleaves_seed = 1234
```

#### Drifting grating configuration

The update rate in frames per second for the drifting grating visualization:
```
grating_frequency = 30
```

The spatial period of the grating in degrees:
```
grating_period_deg = 1
```

The drift speed in cycles per second:
```
grating_cycles_per_second = 5
```

The orientation of the grating:
```
grating_orientation = 'vertical'
```

#### Counterphase checkerboard (pERG) configuration

The counterphase update rate, i.e. the 'flicker' rate:
```
checkerboard_frequency = 5
```

The numbers of columns and rows, defined in terms of the width of the inset image:
```
checkerboard_n_cols = inset_width_deg
checkerboard_n_rows = inset_height_deg
```

The colors of the bright and dark squares:
```
checkerboard_bright = (255,255,255)
checkerboard_dark = (0,0,0)
```

