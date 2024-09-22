from erc7730.linter.classifier.abi_classifier import ABIClassifier
from erc7730.linter.classifier.eip712_classifier import EIP712Classifier
from erc7730.linter import ERC7730Linter
from erc7730.model.context import EIP712Context, ContractContext, EIP712JsonSchema
from erc7730.model.display import Display
from erc7730.model.erc7730_descriptor import ERC7730Descriptor

from erc7730.linter.classifier import TxClass
from pydantic import AnyUrl

from erc7730.model.display import Format


def determine_tx_class(descriptor: ERC7730Descriptor) -> TxClass | None:
    if isinstance(descriptor.context, EIP712Context):
        classifier = EIP712Classifier()
        if descriptor.context.eip712.schemas is not None:
            first_schema = descriptor.context.eip712.schemas[0]
            if isinstance(first_schema, EIP712JsonSchema):
                return classifier.classify(first_schema)
            # url should have been resolved earlier
    elif isinstance(descriptor.context, ContractContext):
        abi_classifier = ABIClassifier()
        if descriptor.context.contract.abi is not None:
            abi_schema = descriptor.context.contract.abi
            if not isinstance(abi_schema, AnyUrl):
                return abi_classifier.classify(abi_schema)
            # url should have been resolved earlier
    return None


class ClassifyTransactionTypeLinter(ERC7730Linter):
    """
    - given schema/ABI, classify the transaction type
    - if class found, check descriptor display fields against predefined ruleset
    - possible class (swap, staking withdraw, staking deposit)
    """

    def lint(self, descriptor: ERC7730Descriptor, out: ERC7730Linter.OutputAdder) -> None:
        if descriptor.context is None:
            return None
        if (tx_class := determine_tx_class(descriptor)) is None:
            # could not determine transaction type
            return None
        out(
            ERC7730Linter.Output(
                title="Transaction type: ", message=str(tx_class), level=ERC7730Linter.Output.Level.INFO
            )
        )
        if (display := descriptor.display) is None:
            return None
        display_format_checker: DisplayFormatChecker = DisplayFormatChecker(tx_class, display)
        linter_outputs = display_format_checker.check()
        for linter_output in linter_outputs:
            out(linter_output)


def _fields_contain(word: str, fields: set[str]) -> bool:
    """
    to check if the provided keyword is contained in one of the fields (case insensitive)
    """
    for field in fields:
        if word.lower() in field.lower():
            return True
    return False


class DisplayFormatChecker:
    """
    Given a transaction class and a display formats, check if all the required fields of a given
    transaction class are being displayed.
    If a field is missing emit an error.
    """

    def __init__(self, tx_class: TxClass, display: Display):
        self.tx_class = tx_class
        self.display = display

    def _get_all_displayed_fields(self, formats: dict[str, Format]) -> set[str]:
        fields: set[str] = set()
        for format in formats.values():
            if format.fields is not None:
                for field in format.fields:
                    fields.add(str(field))
        return fields

    def check(self) -> list[ERC7730Linter.Output]:
        res: list[ERC7730Linter.Output] = []
        match self.tx_class:
            case TxClass.PERMIT:
                formats = self.display.formats
                fields = self._get_all_displayed_fields(formats)
                if not _fields_contain("spender", fields):
                    res.append(
                        ERC7730Linter.Output(
                            title="Missing spender in displayed fields",
                            message="",
                            level=ERC7730Linter.Output.Level.ERROR,
                        )
                    )
                if not _fields_contain("amount", fields):
                    res.append(
                        ERC7730Linter.Output(
                            title="Missing amount in displayed fields",
                            message="",
                            level=ERC7730Linter.Output.Level.ERROR,
                        )
                    )
                if (
                    not _fields_contain("valid until", fields)
                    and not _fields_contain("expiry", fields)
                    and not _fields_contain("expiration", fields)
                ):
                    res.append(
                        ERC7730Linter.Output(
                            title="Field not displayed",
                            message="Missing expiration date in displayed fields for permit",
                            level=ERC7730Linter.Output.Level.ERROR,
                        )
                    )
            case _:
                pass
        return res
