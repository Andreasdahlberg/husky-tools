#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""Interface for the HuskyLens object recognition module."""

import math
import logging
import serial

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Block:
    """Class representing a block"""

    def __init__(self, x, y, width, height, id) -> None:
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._id = id

    @property
    def x(self) -> int:
        """Get the x coordinate of the center of the block."""
        return self._x

    @property
    def y(self) -> int:
        """Get the y coordinate of the center of the block."""
        return self._y

    @property
    def width(self) -> int:
        """Get the width of the block in pixels."""
        return self._width

    @property
    def height(self) -> int:
        """Get the height of the block in pixels."""
        return self._height

    @property
    def id(self) -> int:
        """Get the ID of the block."""
        return self._id

    @property
    def learned(self) -> bool:
        """Check if the block is learned."""
        return self.id > 0


class Arrow:
    """Class representing an arrow"""

    def __init__(self, x_tail, y_tail, x_head, y_head, id) -> None:
        self._x_tail = x_tail
        self._y_tail = y_tail
        self._x_head = x_head
        self._y_head = y_head
        self._id = id

    @property
    def x_tail(self) -> int:
        """Get the x coordinate of the tail of the arrow."""
        return self._x_tail

    @property
    def y_tail(self) -> int:
        """Get the y coordinate of the tail of the arrow."""
        return self._y_tail

    @property
    def x_head(self) -> int:
        """Get the x coordinate of the head of the arrow."""
        return self._x_head

    @property
    def y_head(self) -> int:
        """Get the y coordinate of the head of the arrow."""
        return self._y_head

    @property
    def id(self) -> int:
        """Get the ID of the arrow."""
        return self._id

    @property
    def learned(self) -> bool:
        """Check if the arrow is learned."""
        return self.id > 0

    def get_angle(self) -> float:
        """Get the angle of the arrow in degrees"""
        return math.degrees(math.atan2(self.y_head - self.y_tail, self.x_head - self.x_tail))

    def get_length(self) -> float:
        """Get the length of the arrow in pixels"""
        return math.sqrt((self.x_head - self.x_tail) ** 2 + (self.y_head - self.y_tail) ** 2)


COMMAND_REQUEST_KNOCK = 0x2C
COMMAND_REQUEST_ALGORITHM = 0x2D
COMMAND_REQUEST_BLOCKS = 0x21
COMMAND_REQUEST_BLOCKS_LEARNED = 0x24
COMMAND_REQUEST_BY_ID = 0x26
COMMAND_REQUEST_LEARN = 0x36
COMMAND_REQUEST_FORGET = 0x37

COMMAND_RETURN_INFO = 0x29
COMMAND_RETURN_OK = 0x2E


class HuskyLens:
    """Class for the HuskyLens object recognition module."""
    _COMMAND_HEADER_ADDRESS = [0x55, 0xAA, 0x11]

    def __init__(self, port, baudrate=9600, timeout=0.5) -> None:
        self._serial = serial.Serial(port, baudrate=baudrate, timeout=timeout)

    def knock(self) -> bool:
        """Check if the HuskyLens is connected."""
        logger.info('COMMAND_REQUEST_KNOCK')
        self._write_command(COMMAND_REQUEST_KNOCK)
        response = self._read_response()
        return response[-2] == COMMAND_RETURN_OK

    def set_algorithm(self, algorithm: int) -> None:
        """Set the algorithm used by the HuskyLens."""
        logger.info('COMMAND_REQUEST_ALGORITHM %d', algorithm)
        self._write_command(COMMAND_REQUEST_ALGORITHM, algorithm.to_bytes(2, byteorder='little'))
        response = self._read_response()
        return response[-2] == COMMAND_RETURN_OK

    def learn(self, object_id) -> None:
        """Learn the current recognized object with the given ID."""
        logger.info('COMMAND_REQUEST_LEARN %d', object_id)
        self._write_command(COMMAND_REQUEST_LEARN, object_id.to_bytes(2, byteorder='little'))
        response = self._read_response()
        return response[-2] == COMMAND_RETURN_OK

    def forget(self) -> None:
        """Forget learned objects for the current algorithm."""
        logger.info('COMMAND_REQUEST_FORGET')
        self._write_command(COMMAND_REQUEST_FORGET)
        response = self._read_response()
        return response[-2] == COMMAND_RETURN_OK

    def get_blocks(self) -> list:
        """Get a list of blocks from the HuskyLens."""
        logger.info('COMMAND_REQUEST_BLOCKS')
        self._write_command(COMMAND_REQUEST_BLOCKS)
        return self.handle_block_response()

    def get_blocks_learned(self) -> list:
        """Get a list of learned blocks from the HuskyLens."""
        logger.info('COMMAND_REQUEST_BLOCKS_LEARNED')
        self._write_command(COMMAND_REQUEST_BLOCKS_LEARNED)
        return self.handle_block_response()

    def get_blocks_by_id(self, id) -> list:
        """Get a list of blocks with a specific ID from the HuskyLens."""
        logger.info('COMMAND_REQUEST_BY_ID %d', id)
        # TODO: This is a hack, the HuskyLens should support this natively
        blocks = self.get_blocks()
        return [block for block in blocks if block.id == id]

    def _write_command(self, cmd: int, data=[]) -> None:
        """Write a command to the HuskyLens."""
        command = self._COMMAND_HEADER_ADDRESS.copy()

        command.append(len(data))
        command.append(cmd)
        command.extend(data)
        # Add checksum
        command.append(sum(command) & 0xFF)

        logger.debug('write: %s', ' '.join(hex(x) for x in command))

        self._serial.flush()
        self._serial.flushInput()
        self._serial.write(bytes(command))

    def _read_response(self):
        """Read a response from the HuskyLens."""
        response = self._serial.read(5)
        length = int(response[-2])
        response += (self._serial.read(length + 1))

        logger.debug('read: %s', ' '.join(hex(x) for x in response))

        expected_checksum = sum(response[:-1]) & 0xFF
        checksum = response[-1]
        if expected_checksum != checksum:
            raise ValueError('Checksum mismatch {} != {}'.format(
                expected_checksum, checksum))
        return response

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._serial.close()

    def handle_block_response(self):
        """Handle a block response from the HuskyLens."""
        info_response = self._read_response()
        number_of_blocks = int.from_bytes(info_response[5:6], byteorder='little', signed=False)

        blocks = []
        for i in range(0, number_of_blocks):
            response = self._read_response()

            x = int.from_bytes(response[5:6], byteorder='little', signed=False)
            y = int.from_bytes(response[7:8], byteorder='little', signed=False)
            width = int.from_bytes(response[9:10], byteorder='little', signed=False)
            height = int.from_bytes(response[11:12], byteorder='little', signed=False)
            id = int.from_bytes(response[13:14], byteorder='little', signed=False)
            blocks.append(Block(x, y, width, height, id))

        return blocks


if __name__ == "__main__":
    with HuskyLens("/dev/ttyUSB0") as lens:
        print("Connected:", lens.knock())
