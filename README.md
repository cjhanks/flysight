# flysight

Visual display tool for observing heatmaps, peak detections, and frames
from video.

![Example](.readme/sc1.png)

## TLDR

Run `make`.

## Environment

This code was tested on ubuntu 20.04.  It required these apt packages.

```
apt-get install -y  \
  python3           \
  python3-venv      \
  build-essential
```

## Build

The recommended way to run this program is through use of the top-level
`Makefile` which internally uses VirtualEnv.

These three commands will configure a virtualenv, install dependencies,
and run the app.

```bash
make virtualenv
make dep
make run
```

*Alternatively*, you can install the package.

```bash
python3 -m venv venv
. venv/bin/activate
python setup.py install
```

Then the command will be available as `flysight`.

## Running

Configuring your environment.

```bash
make virtualenv
make dep
```

Any subsequently run:

```bash
make run
```

## Data

To fetch the two video examples:

```
cd data
./get.sh
```

## Configuration

In `flysight/config.yml` there is a set of default configuration
options.  Options are documented in this file.  If you wish to change
them, you can pass them into the program by either running;

```
make run ARGS="--config ./path/to/config.yml"
```

OR (if installed...)

```
flysight --config ./path/to/config.yml
```

### Command

`Open` opens a new video file.

`Save` will save the currently rendered image to disk as a PNG.

`Quit` you can guess.

### Display

`Show Image` requests the renderer to display the raw image from the
provided video stream.

`Show Peaks` requests the renderer to display arrows pointing at the
pixel selected from nonmax-suppression.

`Show Heatmap` requests the renderer to display the heatmap.  If the
image is also shown, it will set an alpha channel such that you can
see the heatmap overlaid on the image.

## Debugging

If you are receiving complaints from `protobuf`, you may need to
generate the protofiles for your system.  This will require you
installing `protoc`.  On ubuntu, `apt-get install protobuf-compiler`.

Then run, `make proto`.

## Improvements

There are several improvements which could occur for this application.

- The display widget should be zoomable and navigable.
- The zoom widget should not be zooming into the window render buffer,
  that loses precision.  Rather, it should be rendering from the data
  independent of the diplay.
- Some of the default sizings are wonky.
- The nonmax suppression isn't perfect or tuned.

