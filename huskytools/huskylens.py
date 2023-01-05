#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""Interface for the HuskyLens object recognition module."""

import math
import logging
import serial

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class RecognitionAlgorithm:
    """Class representing the algorithms available on the HuskyLens."""
    FACE_RECOGNITION = 0x00
    OBJECT_TRACKING = 0x01
    OBJECT_RECOGNITION = 0x02
    LINE_TRACKING = 0x03
    COLOR_RECOGNITION = 0x04
    TAG_RECOGNITION = 0x05
    OBJECT_CLASSIFICATION = 0x06


class Block:
    """Class representing a block"""

    def __init__(self, x: int, y: int, width: int, height: int, id: int) -> None:
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

    def __init__(self, x_tail: int, y_tail: int, x_head: int, y_head: int, id: int) -> None:
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


class ChecksumMismatch(Exception):
    pass


class ResponseLengthError(Exception):
    pass


class Interface:
    """Class for the HuskyLens object recognition module."""
    _COMMAND_HEADER_ADDRESS = [0x55, 0xAA, 0x11]
    _COMMAND_REQUEST_KNOCK = 0x2C
    _COMMAND_REQUEST_ALGORITHM = 0x2D
    _COMMAND_REQUEST_BLOCKS = 0x21
    _COMMAND_REQUEST_ARROWS = 0x22
    _COMMAND_REQUEST_BLOCKS_LEARNED = 0x24
    _COMMAND_REQUEST_ARROWS_LEARNED = 0x25
    _COMMAND_REQUEST_BY_ID = 0x26
    _COMMAND_REQUEST_BLOCKS_BY_ID = 0x27
    _COMMAND_REQUEST_ARROWS_BY_ID = 0x28
    _COMMAND_REQUEST_CUSTOM_NAMES = 0x2F
    _COMMAND_REQUEST_PHOTO = 0x30
    _COMMAND_REQUEST_SEND_KNOWLEDGES = 0x32
    _COMMAND_REQUEST_RECEIVE_KNOWLEDGES = 0x33
    _COMMAND_REQUEST_CUSTOM_TEXT = 0x34
    _COMMAND_REQUEST_CLEAR_TEXT = 0x35
    _COMMAND_REQUEST_LEARN = 0x36
    _COMMAND_REQUEST_FORGET = 0x37
    _COMMAND_REQUEST_SAVE_SCREENSHOT = 0x39
    _COMMAND_REQUEST_IS_PRO = 0x3B
    _COMMAND_RETURN_INFO = 0x29
    _COMMAND_RETURN_OK = 0x2E

    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0) -> None:
        self._serial = serial.Serial(port, baudrate=baudrate, timeout=timeout)

    def knock(self) -> bool:
        """Check if the HuskyLens is connected."""
        logger.info('COMMAND_REQUEST_KNOCK')
        self._write_command(self._COMMAND_REQUEST_KNOCK)
        try:
            response = self._read_response()
        except ResponseLengthError:
            return False
        return self._is_response_ok(response)

    def set_algorithm(self, algorithm: int) -> bool:
        """Set the algorithm used by the HuskyLens."""
        logger.info('COMMAND_REQUEST_ALGORITHM %d', algorithm)
        self._write_command(self._COMMAND_REQUEST_ALGORITHM, algorithm.to_bytes(2, byteorder='little'))
        response = self._read_response()
        return self._is_response_ok(response)

    def learn(self, object_id: int) -> bool:
        """Learn the current recognized object with the given ID."""
        logger.info('COMMAND_REQUEST_LEARN %d', object_id)
        self._write_command(self._COMMAND_REQUEST_LEARN, object_id.to_bytes(2, byteorder='little'))
        response = self._read_response()
        return self._is_response_ok(response)

    def forget(self) -> bool:
        """Forget learned objects for the current algorithm."""
        logger.info('COMMAND_REQUEST_FORGET')
        self._write_command(self._COMMAND_REQUEST_FORGET)
        response = self._read_response()
        return self._is_response_ok(response)

    def get_blocks(self) -> list:
        """Get a list of blocks from the HuskyLens."""
        logger.info('COMMAND_REQUEST_BLOCKS')
        self._write_command(self._COMMAND_REQUEST_BLOCKS)
        return self._handle_block_response()

    def get_blocks_learned(self) -> list:
        """Get a list of learned blocks from the HuskyLens."""
        logger.info('COMMAND_REQUEST_BLOCKS_LEARNED')
        self._write_command(self._COMMAND_REQUEST_BLOCKS_LEARNED)
        return self._handle_block_response()

    def get_blocks_by_id(self, id: int) -> list:
        """Get a list of blocks with a specific ID from the HuskyLens."""
        logger.info('COMMAND_REQUEST_BLOCKS_BY_ID %d', id)
        self._write_command(self._COMMAND_REQUEST_BLOCKS_BY_ID, id.to_bytes(2, byteorder='little'))
        return self._handle_block_response()

    def get_arrows(self) -> list:
        """Get a list of arrows from the HuskyLens."""
        logger.info('COMMAND_REQUEST_ARROWS')
        self._write_command(self._COMMAND_REQUEST_ARROWS)
        return self._handle_arrow_response()

    def get_arrows_learned(self) -> list:
        """Get a list of learned arrows from the HuskyLens."""
        logger.info('COMMAND_REQUEST_ARROWS_LEARNED')
        self._write_command(self._COMMAND_REQUEST_ARROWS_LEARNED)
        return self._handle_arrow_response()

    def get_arrows_by_id(self, id: int) -> list:
        """Get a list of arrows with a specific ID from the HuskyLens."""
        logger.info('COMMAND_REQUEST_ARROWS_BY_ID %d', id)
        self._write_command(self._COMMAND_REQUEST_ARROWS_BY_ID, id.to_bytes(2, byteorder='little'))
        return self._handle_arrow_response()

    def photo(self) -> bool:
        """Take a photo with the HuskyLens and save to the SD-card."""
        logger.info('COMMAND_REQUEST_PHOTO')
        self._write_command(self._COMMAND_REQUEST_PHOTO)
        response = self._read_response()
        return self._is_response_ok(response)

    def screenshot(self) -> bool:
        """Save a screenshot of the current UI to the SD-card.

        Note that the function will return True even if no SD-card is inserted.
        """
        logger.info('COMMAND_REQUEST_SAVE_SCREENSHOT')
        self._write_command(self._COMMAND_REQUEST_SAVE_SCREENSHOT)
        response = self._read_response()
        return self._is_response_ok(response)

    def set_name(self, name: str, object_id: int):
        """Set a custom name for the object with given ID."""
        logger.info('COMMAND_REQUEST_CUSTOM_NAMES')

        data = bytearray()
        data.append(object_id)
        data.append(len(name) + 1)  # Add one, for NULL, according to the protocol specification.
        data.extend(name.encode('ascii', 'replace'))
        data.append(0)

        self._write_command(self._COMMAND_REQUEST_CUSTOM_NAMES, data)
        response = self._read_response()
        return self._is_response_ok(response)

    def set_text(self, text: str, x: int, y: int) -> bool:
        """Set a custom text on the HuskyLens display."""
        logger.info('COMMAND_REQUEST_CUSTOM_TEXT')

        # Make sure that the text position is on the screen.
        if x > 320 or y > 240:
            raise ValueError('Invalid text position')

        data = bytearray()
        data.append(len(text))

        x_flag = 0
        if x >= 0xFF:
            x_flag = 0xFF
        data.append(x_flag)

        x_value = x
        if x_flag != 0:
            x_value = x % 0xFF
        data.append(x_value)

        data.append(y)
        data.extend(text.encode('ascii', 'replace'))

        self._write_command(self._COMMAND_REQUEST_CUSTOM_TEXT, data)
        response = self._read_response()
        return self._is_response_ok(response)

    def clear_text(self) -> bool:
        """Clear all custom texts on the HuskyLens display."""
        logger.info('COMMAND_REQUEST_CLEAR_TEXT')
        self._write_command(self._COMMAND_REQUEST_CLEAR_TEXT)
        response = self._read_response()
        return self._is_response_ok(response)

    def save_model(self, file_number):
        """Save the current algorithms model to the SD-card."""
        logger.info('COMMAND_REQUEST_SEND_KNOWLEDGES')
        self._write_command(self._COMMAND_REQUEST_SEND_KNOWLEDGES, file_number.to_bytes(2, byteorder='little'))
        response = self._read_response()
        return self._is_response_ok(response)

    def load_model(self, file_number):
        """Load a model from the SD-card."""
        logger.info('COMMAND_REQUEST_RECEIVE_KNOWLEDGES')
        self._write_command(self._COMMAND_REQUEST_RECEIVE_KNOWLEDGES, file_number.to_bytes(2, byteorder='little'))
        response = self._read_response()
        return self._is_response_ok(response)

    def is_pro(self) -> bool:
        """Check if the HuskyLens is a pro version."""
        logger.info('COMMAND_REQUEST_IS_PRO')
        self._write_command(self._COMMAND_REQUEST_IS_PRO)
        response = self._read_response()
        return response[-2] == 0x01

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

    def _read_response(self) -> bytearray:
        """Read a response from the HuskyLens."""
        RESPONSE_HEADER_LENGTH = 5
        response = self._serial.read(RESPONSE_HEADER_LENGTH)
        if len(response) != RESPONSE_HEADER_LENGTH:
            raise ResponseLengthError('Invalid response header length {} != {}'.format(
                RESPONSE_HEADER_LENGTH, len(response)))
        length = int(response[-2])
        response += (self._serial.read(length + 1))
        if len(response) != RESPONSE_HEADER_LENGTH + length + 1:
            raise ResponseLengthError('Invalid response data length {} != {}'.format(
                RESPONSE_HEADER_LENGTH + length + 1, len(response)))

        logger.debug('read: %s', ' '.join(hex(x) for x in response))

        expected_checksum = sum(response[:-1]) & 0xFF
        checksum = response[-1]
        if expected_checksum != checksum:
            raise ChecksumMismatch('Checksum mismatch {} != {}'.format(
                expected_checksum, checksum))
        return response

    def _is_response_ok(self, response: bytearray) -> bool:
        """Check if the response is OK."""
        return response[-2] == self._COMMAND_RETURN_OK

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._serial.close()

    def _handle_block_response(self) -> list:
        """Handle a block response from the HuskyLens."""
        info_response = self._read_response()
        number_of_blocks = int.from_bytes(info_response[5:6], byteorder='little', signed=False)

        blocks = []
        for _ in range(0, number_of_blocks):
            response = self._read_response()

            x = int.from_bytes(response[5:6], byteorder='little', signed=False)
            y = int.from_bytes(response[7:8], byteorder='little', signed=False)
            width = int.from_bytes(response[9:10], byteorder='little', signed=False)
            height = int.from_bytes(response[11:12], byteorder='little', signed=False)
            block_id = int.from_bytes(response[13:14], byteorder='little', signed=False)
            blocks.append(Block(x, y, width, height, block_id))

        return blocks

    def _handle_arrow_response(self) -> list:
        """Handle an arrow response from the HuskyLens."""
        info_response = self._read_response()
        number_of_arrows = int.from_bytes(info_response[5:6], byteorder='little', signed=False)

        arrows = []
        for _ in range(0, number_of_arrows):
            response = self._read_response()

            x_tail = int.from_bytes(response[5:6], byteorder='little', signed=False)
            y_tail = int.from_bytes(response[7:8], byteorder='little', signed=False)
            x_head = int.from_bytes(response[9:10], byteorder='little', signed=False)
            y_head = int.from_bytes(response[11:12], byteorder='little', signed=False)
            arrow_id = int.from_bytes(response[13:14], byteorder='little', signed=False)
            arrows.append(Arrow(x_tail, y_tail, x_head, y_head, arrow_id))

        return arrows
