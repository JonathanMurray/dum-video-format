# DUM - a dumb video format

This is an implementation of a dumb made-up video format, along with a Pygame application that can
play DUM files.

Disclaimer: this project exists only for educational purposes.

## The DUM format

A DUM video file is structured in the following way:

### Header
The file must begin with a header that contains the values listed below.
```
- magic_string (3 bytes) = 0x64756d ("dum")
- frame_rate (4 bytes)
- width (4 bytes)
- height (4 bytes)
- hor_scale (4 bytes)
- ver_scale (4 bytes)
```

### Frames
After the header comes the frame data. Each frame is simply a sequence of rows, where each row is a
sequence of pixels. Each pixel must contain RGB values as listed below
```
- red (1 byte)
- green (1 byte)
- blue (1 byte) 
```

## Try it out

```bash
# Create a DUM video file
./create_example_file.py hello_world.dum
 
# Play it
./play.py hello_world.dum
```