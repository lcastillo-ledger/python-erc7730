from pathlib import Path
from erc7730.common.pydantic import model_from_json_file_or_none, json_file_from_model
from erc7730.model.erc7730_descriptor import ERC7730Descriptor
import pytest
import glob
import json
from jsonschema import validate, exceptions

files = glob.glob("clear-signing-erc7730-registry/registry/*/*.json")
with open("clear-signing-erc7730-registry/specs/erc7730-v1.schema.json", "r") as file:
    schema = json.load(file)


@pytest.mark.parametrize("file", files)
def test_from_erc7730(file: str) -> None:
    model_erc7730 = model_from_json_file_or_none(Path(file), ERC7730Descriptor)
    assert model_erc7730 is not None
    json_str_from_model = json_file_from_model(ERC7730Descriptor, model_erc7730)
    json_from_model = json.loads(json_str_from_model)
    try:
        validate(instance=json_from_model, schema=schema)
    except exceptions.ValidationError as ex:
        pytest.fail(f"Invalid schema for serialized data from {file}: {ex}")
