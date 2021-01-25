# DUM - a dumb video format

This is an implementation of a dumb made-up video format, along with a Pygame application that can
play DUM files.

Disclaimer: this project exists only for educational purposes.

## The DUM format

A DUM video file is structured in the following way:

### Header
The file must begin with a header that contains the values listed below.
```
- magic_string (4 bytes) = 0x64756d76 ("dumv")
- frame_rate (1 byte)
- width (1 byte)
- height (1 byte)
- hor_scale (1 byte)
- ver_scale (1 byte)
- num_frames (4 bytes)
```

### Frames
After the header comes the frame data. 

Frame header:
```
- type (1 byte) = 1 (raw) or 2 (compressed)
```

#### Raw frame
A raw frame is simply a sequence of rows, where each row is a sequence of pixels. Each pixel is
made up of 3 bytes (RGB).

#### Compressed frame
A compressed frame contains the following data:
```
- num_colors (1 byte)
- colors (num_colors * 3 bytes)
- pixels (num_rows * num_cols bytes)
```

A list of RGB values is defined that is then referenced with indices by the pixels.

## Try it out

```bash
# Create a DUM video file
./create_example_file.py hello_world.dum
 
# Play it
./play.py hello_world.dum
```