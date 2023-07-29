import utime
from micropython import const


class PT2258:
    def __init__(self, address: int, port=None) -> None:
        """
        Initialize the PT2258 audio IC driver.

        :param address: The I2C address of the PT2258 IC (7-bit address).
        :param port: The I2C bus port to use (an instance of machine.I2C).
        """
        if port is None:
            raise ValueError('I2C object is required')
        self.__I2C = port
        valid_addresses = [0x8C, 0x88, 0x84, 0x80]
        if address not in valid_addresses:
            raise ValueError('The I2C device address is not valid')
        # Convert 7-bit address to 8-bit for I2C communication
        self.__PT2258_ADDR = const(address >> 1)
        # Initializing the PT2258
        self.__initialize_pt2258()

    def __write_pt2258(self, volume_10db: int, volume_1db: int) -> None:
        """
        Write the volume values to the PT2258 audio IC.

        :param volume_10db: The 10dB step volume value.
        :param volume_1db: The 1dB step volume value.
        """
        write_data = bytearray([volume_10db, volume_1db])
        try:
            self.__I2C.writeto(self.__PT2258_ADDR, const(write_data))  # Write the values to the PT2258
        except OSError as e:
            if e.args[0] == 5:  # I2C bus error (Device not found)
                raise RuntimeError("Device not found on the I2C bus.")
            else:
                raise RuntimeError(f"I2C communication error occurred: {e}")

    def __initialize_pt2258(self) -> None:
        """
        Initialize the PT2258 audio IC after power-up.

        This function waits for a short time to ensure stability
        and then sends an I2C write operation to clear register 0xC0 of the PT2258 IC.
        """
        # Functions registers
        clear_register = const(0xC0)
        # Wait for stabilization
        utime.sleep_ms(200)
        # Clear the register to ensure a clean start
        self.__write_pt2258(0, clear_register)

    @staticmethod
    def __volume_map(value: int, in_main: int, in_max: int, out_main: int, out_max: int) -> int:
        """
        Map the given value from the input range to the output range.
        The value is flipped so that 0 dB represents maximum volume and -79 dB represents minimum volume.

        :param value: The input value to be mapped to the output range.
        :param in_main: The minimum value of the input range.
        :param in_max: The maximum value of the input range.
        :param out_main: The minimum value of the output range.
        :param out_max: The maximum value of the output range.
        :return: The mapped value in the output range as an integer.
        """
        value = max(in_main, min(value, in_max))
        flipped_value = 100 - value
        map_value = (flipped_value - in_main) * (out_max - out_main) // (in_max - in_main) + out_main
        return int(map_value)

    def master_volume(self, volume: int) -> None:
        """
        Set the master volume of the PT2258 audio IC.

        :param volume: The master volume value (0 to 100).
        """
        # Master volume registers
        master_1db = const(0xE0)
        master_10db = const(0xD0)
        if not 0 <= volume <= 100:
            raise ValueError("Master volume should be in the range 0 to 100.")
        # Map the value to PT2258 range (0 to 79)
        mapped_volume = self.__volume_map(value=volume, in_main=0, in_max=100, out_main=0, out_max=79)
        a, b = divmod(mapped_volume, 10)
        # Send master volume data: 10dB followed by 1dB
        self.__write_pt2258(master_10db | a, master_1db | b)

    def channel_volume(self, channel: int, volume: int) -> None:
        """
        Set the volume of a specific channel on the PT2258 audio IC.

        :param channel: The channel number (0 to 5).
        :param volume: The volume value (0 to 100).
        """
        if not 0 <= volume <= 100:
            raise ValueError("Channel volume should be in the range 0 to 100.")
        if not 0 <= channel <= 5:
            raise ValueError("Channel should be in the range 0 to 5.")
        # Channel volume registers: 10dB step, 1dB step
        channel_registers = [
            (0x80, 0x90),  # channel 1 (10dB, 1dB)
            (0x40, 0x50),  # channel 2 (10dB, 1dB)
            (0x00, 0x10),  # channel 3 (10dB, 1dB)
            (0x20, 0x30),  # channel 4 (10dB, 1dB)
            (0x60, 0x70),  # channel 5 (10dB, 1dB)
            (0xA0, 0xB0),  # channel 6 (10dB, 1dB)
        ]
        # Map the value to PT2258 range (0 to 79)
        mapped_volume = self.__volume_map(value=volume, in_main=0, in_max=100, out_main=0, out_max=79)
        a, b = divmod(mapped_volume, 10)
        channel_10db, channel_1db = channel_registers[channel]
        # Send channel volume data: 10dB followed by 1dB
        self.__write_pt2258(channel_10db | a, channel_1db | b)

    def toggle_mute(self, mute: bool) -> None:
        """
        Toggle mute on/off for the PT2258 audio IC.

        :param mute: If True, mute is turned on. If False, mute is turned off.
        """
        # Mute registers
        mute_on = const(0xF9)
        mute_off = const(0xF8)
        # Choose the appropriate mute setting
        toggled_mute = mute_on if mute else mute_off
        # Send the mute data
        self.__write_pt2258(0, toggled_mute)
        """
        The write_pt2258 function take 2 parameter, but we don't need 2 so make 1 mummy passing 0
        is done to minimize I2C overhead and improve efficiency.
        """

# The code ends here
