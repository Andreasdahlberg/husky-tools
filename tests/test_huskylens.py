from huskytools import huskylens


def test_block_learned():
    block_id = 0
    block = huskylens.Block(0, 0, 10, 10, block_id)
    assert block.learned is False, "Block with id 0 should not be learned"

    block_id = 1
    block = huskylens.Block(0, 0, 10, 10, block_id)
    assert block.learned is True, "Block with id > 0 should be learned"
