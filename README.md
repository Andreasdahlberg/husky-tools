[![Python package](https://github.com/Andreasdahlberg/husky-tools/actions/workflows/python-package.yml/badge.svg)](https://github.com/Andreasdahlberg/husky-tools/actions/workflows/python-package.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Andreasdahlberg_husky-tools&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Andreasdahlberg_husky-tools)

# About
huskytools provides tools for interacting with the [HuskyLens AI camera](https://wiki.dfrobot.com/HUSKYLENS_V1.0_SKU_SEN0305_SEN0336).

## Features
 * Low-level API for interacting with the HuskyLens camera. It's meant as a replacement
for the [official HuskyLens Python API](https://github.com/HuskyLens/HUSKYLENSPython). It's not a drop-in replacement but all
the functionality, except for I2C-support, is there.

* A command line interface for quick testing and debugging.[NOT IMPLEMENTED YET]

* Helper classes for working with the HuskyLens camera, e.g. a class for working
with faces. [NOT IMPLEMENTED YET]

## Installation
huskytools is available on PyPI, so you can install it with pip:
```bash
pip install huskytools
```

Alternatively, you can install the latest development version of huskytools by
cloning the repository and install it with pip:
```bash
git clone https://github.com/Andreasdahlberg/husky-tools.git
cd husky-tools
pip install .
```

## Usage

### API

This example shows how to connect to the HuskyLens.
```python
from huskytools import huskylens

with huskylens.Interface("/dev/ttyUSB0") as lens:
    if lens.knock():
        print("HuskyLens connected")
    else:
        print("HuskyLens not found")
```

This example shows how to get all detected faces from the HuskyLens.
```python
from huskytools import huskylens

with huskylens.Interface("/dev/ttyUSB0") as lens:
    if lens.knock():
        lens.set_algorithm(huskylens.RecognitionAlgorithm.FACE_RECOGNITION)
        for block in lens.get_blocks():
            print("Block ID: {}, X: {}, Y: {}".format(block.id, block.x, block.y))
```

### Command line interface
NOT IMPLEMENTED YET

### Helper classes
NOT IMPLEMENTED YET

## Contributing
Contributions are welcome. Please open an issue or a pull request on GitHub.

## Support
If you have any questions or problems, please open an issue on GitHub and i will be happy to help.
