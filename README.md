# DUM - a dumb video format

This is an implementation of a dumb made-up video format, along with a Pygame application that can
play DUM files.

Disclaimer: this project exists only for educational purposes.

## Try it out

```bash
# Create a DUM video file
./create_example_file.py hello_world.dum
 
# Play it
./play.py hello_world.dum
```

## The DUM format

The internal structure of a DUM video file is described below. When contents are listed, the number
in parenthesis denotes how many bytes that part consists of.

### Header
The file must begin with a header that contains the values listed below.
```
- magic_string (4) = 0x64756d76 (ascii for "dumv")
- frame_rate (1)
- width (2)
- height (2)
- hor_scale (1)
- ver_scale (1)
- num_frames (4)
```

### Frames
After the header comes the frame data. 

Frame header:
```
- frame_type (1) = 1 (raw), 2 (color-mapped), 3 (quantized 16bit), or 4 (quantized 8bit)
- frame_size (4)
```

#### Raw frame
A raw frame is simply a sequence of rows, where each row is a sequence of pixels. Each pixel is
made up of 3 bytes (RGB).

#### Color-mapped frame
A list of RGB values is defined that is then referenced with indices by the pixels.
A compressed frame contains the following data:
```
- num_colors (1)
- color_map (num_colors * 3)
- pixels (num_rows * num_cols)
```

#### Quantized frame
Colors are quantized in a way such that an RGB-triple (which in its raw form takes up 3 bytes) fits
in either 2 or 1 byte (depending on the quantization mode).
A quantized frame contains the following data:
```
- pixels (num_rows * num_cols * n) 
```
where n is either 1 or 2 bytes depending on the quantization mode.
