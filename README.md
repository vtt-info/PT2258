# PT2258 Class for MicroPython

This is a Python class implementation for controlling the PT2258 audio volume control IC using MicroPython.

## Usage

The PT2258 is a 6-channel audio volume control IC that can adjust the volume in -1dB steps and provides a total
attenuation of -79dB This
class simplifies the process of controlling the PT2258 chip and allows you to set the master volume and individual
channel volumes. and ON or OFF the Mute

The code is more efficient, simpler, and easier to use!
Feel free to use this code as a starting point for your PT2258 audio control project and customize it according to your
needs.

1. Copy the `AUDIO_PY.py` file to your MicroPython device.
2. Import the necessary modules. and redy to use.

## Example code

```python
import utime
from machine import Pin, I2C

from AUDIO_PY import PT2258

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)

pt2258 = PT2258(address=0x88, port=i2c)


def main() -> None:
    # set all channel in to o
    for channel in range(6):
        pt2258.channel_volume(channel, 0)
    pt2258.master_volume(0)
    while True:
        for volume in range(100):
            print('Volume is at maximum' if volume == 0 else f'Master volume: {volume}dB')
            pt2258.master_volume(volume)
            utime.sleep(0.5)  # Every off half second the master volume raise up


if __name__ == '__main__':
    main()


```

## Example code for multiple PT2258

```python
from machine import Pin, I2C

from AUDIO_PY import PT2258

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)

# Initialize the PT2258
pt2258_1 = PT2258(address=0x80, port=i2c)  # IC 1
pt2258_2 = PT2258(address=0x84, port=i2c)  # IC 2
pt2258_3 = PT2258(address=0x88, port=i2c)  # IC 3
pt2258_4 = PT2258(address=0x8C, port=i2c)  # IC 4

# set master volume range: 0 to 100
pt2258_1.master_volume(volume)  # IC 1
pt2258_2.master_volume(volume)  # IC 2
pt2258_3.master_volume(volume)  # IC 3
pt2258_4.master_volume(volume)  # IC 4

# the volume value cum from anything you want rotary encoder or variable resistor
# set channel volume range: 0 to 100, channel range index: 0 to 5
pt2258_1.channel_volume(channel, volume)  # IC 1
pt2258_2.channel_volume(channel, volume)  # IC 2
pt2258_3.channel_volume(channel, volume)  # IC 3
pt2258_4.channel_volume(channel, volume)  # IC 4

# toggle the mute use bool if it's True mute is on, if it's False mute is off
pt2258_1.toggle_mute(True)  # IC 1 mute is on
pt2258_2.toggle_mute(False)  # IC 2 mute is off
pt2258_3.toggle_mute(True)  # IC 3 mute is on
pt2258_4.toggle_mute(False)  # IC 4 mute is off

```

Make sure the address are valid otherwise the program raise error

Thanks to MicroPython. it's make the job simple.

