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

        self.__PT2258_ADDR = const(address >> 1)  # 7-bit address is accepted by I2C

        # Functions registers
        self.__CLEAR_REGISTER = const(0xC0)
        # Mute registers
        self.__MUTE_ON = const(0xF9)
        self.__MUTE_OFF = const(0xF8)
        # master volume registers
        self.__MASTER_1dB = const(0xE0)
        self.__MASTER_10dB = const(0xD0)

        # Channel volume registers: 10dB step, 1dB step
        self.__CHANNEL_REGISTERS = [
            (0x80, 0x90),  # channel 1 (10dB, 1dB)
            (0x40, 0x50),  # channel 2 (10dB, 1dB)
            (0x00, 0x10),  # channel 3 (10dB, 1dB)
            (0x20, 0x30),  # channel 4 (10dB, 1dB)
            (0x60, 0x70),  # channel 5 (10dB, 1dB)
            (0xA0, 0xB0),  # channel 6 (10dB, 1dB)
        ]
        self.__init_pt2258()  # Initializing the PT2258

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
                raise RuntimeError(f"I2C communication error acquired in: {e}")

    def __init_pt2258(self) -> None:
        """
        Initialize the PT2258 audio IC after power-up.

        This function waits for a short time to ensure stability
        and then sends an I2C write operation to clear register 0xC0 of the PT2258 IC.
        """
        utime.sleep_ms(200)
        self.__write_pt2258(0, self.__CLEAR_REGISTER)

    @staticmethod
    def __volume_map(value: int, in_main: int, in_max: int, out_main: int, out_max: int) -> int:
        """
        Map the given value from the input range to the output range.

        :param value: The input value to be mapped to the output range.
        :param in_main: The minimum value of the input range.
        :param in_max: The maximum value of the input range.
        :param out_main: The minimum value of the output range.
        :param out_max: The maximum value of the output range.
        :return: The mapped value in the output range as an integer.
        """
        value = max(in_main, min(value, in_max))
        flip_value = 100 - value
        """
        flip_value: we flip the value 0 to 100 into 100 to 0
        the logic is -79dB is valve dead close no more flow, -0db is valve full open
        if we send 0 to 100 without the flip the control work reverse which is not ethical so we flip the value 
        """
        map_value = (flip_value - in_main) * (out_max - out_main) // (in_max - in_main) + out_main
        return int(map_value)

    def master_volume(self, volume: int) -> None:
        """
        Set the master volume of the PT2258 audio IC.

        :param volume: The master volume value (0 to 100).
        """
        if not 0 <= volume <= 100:
            raise ValueError("Master volume should be in the range 0 to 100.")
        mapped_volume = self.__volume_map(volume, 0, 100, 0, 79)  # Map the value to PT2258 range (0 to 79)
        a, b = divmod(mapped_volume, 10)
        self.__write_pt2258(self.__MASTER_10dB | a, self.__MASTER_1dB | b)  # We need to send 10dB byte followed by 1dB

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
        mapped_volume = self.__volume_map(volume, 0, 100, 0, 79)  # Map the value to PT2258 range (0 to 79)
        a, b = divmod(mapped_volume, 10)
        channel_10db, channel_1db = self.__CHANNEL_REGISTERS[channel]
        self.__write_pt2258(channel_10db | a, channel_1db | b)  # We need to send 10dB byte followed by 1dB

    def toggle_mute(self, mute: bool) -> None:
        """
        Toggle mute on/off for the PT2258 audio IC.

        :param mute: If True, mute is turned on. If False, mute is turned off.
        """
        if mute:
            self.__write_pt2258(0, self.__MUTE_ON)
        else:
            self.__write_pt2258(0, self.__MUTE_OFF)

# The code ends here
