from erc7730.common.client.etherscan import get_contract_abis

import pytest


@pytest.mark.skip(reason="Secret management not implemented")
def test_get_contract_abis() -> None:
    assert len(get_contract_abis("0x06012c8cf97bead5deae237070f9587f8e7a266d")) > 0
