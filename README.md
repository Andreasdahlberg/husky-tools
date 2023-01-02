[![Python package](https://github.com/Andreasdahlberg/husky-tools/actions/workflows/python-package.yml/badge.svg)](https://github.com/Andreasdahlberg/husky-tools/actions/workflows/python-package.yml)

# huskytools
huskytools provides simple and easy-to-use tools for interacting with the HuskyLens AI camera.

## Features
 * An API for interacting with the HuskyLens camera. It's meant as a replacement for the official HuskyLens Python API. It's not a drop-in replacement but all the functionality, except for I2C-support, is there.

* A command line interface for quick testing and debugging.[NOT IMPLEMENTED YET]

* Helper classes for working with the HuskyLens camera, e.g. a class for working with faces.

## Installation
huskytools is available on PyPI, so you can install it with pip:
```bash
pip install huskytools
```

Alternatively, you can install the latest development version of huskytools by cloning the repository and install it with pip:
```bash
git clone https://github.com/Andreasdahlberg/husky-tools.git
cd husky-tools
pip install .
```

## Usage

```python
from huskytools import huskylens

with huskylens.Interface("/dev/ttyUSB0") as lens:
    if lens.knock():
        print("HuskyLens connected")
        for block in lens.get_blocks_learned():
            print("Block ID: {}, X: {}, Y: {}".format(block.id, block.x, block.y))
    else:
        print("HuskyLens not found")
```

For more usage examples, see the the examples directory.
