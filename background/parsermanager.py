from abc import ABC, abstractmethod
import importlib
import os
import pkgutil
import warnings
from background.abstractparser import AbstractParser
from background.parsers import __path__ as parsers_path

class ParserManager:
    """
    Manages the loading and selection of data parsers.
    """
    def __init__(self):
        self.parsers = self._load_parsers()
        self.parser_names = [parser.get_name() for parser in self.parsers]

    def parse_data(self, data: bytes) -> tuple[dict[str, any], str]:
        """
        Parses the given byte data using the appropriate parser.
        Returns a dictionary of parsed values.
        """
        parser = self._select_parser(data, self.parsers)
        if parser is not None:
            return parser.parse(data), parser.get_name()
        else:
            return {}, None

    def get_parser_names(self) -> list[str]:
        """
        Returns a list of available parser names.
        """
        return self.parser_names

    def get_parser_information(self, parsername: str) -> dict:
        """
        Returns information about a specific parser.
        """
        for parser in self.parsers:
            if parser.get_name() == parsername:
                return {
                    "name": parser.get_name(),
                    "keys": parser.get_keys(),
                }
        return {"error": "Parser not found"}

    def _load_parsers(self) -> list[AbstractParser]:
        parser_instances = []
        for _, module_name, _ in pkgutil.iter_modules(parsers_path):
            module = importlib.import_module(f"background.parsers.{module_name}")
            if hasattr(module, "parser"):
                instance = getattr(module, "parser")
                if isinstance(instance, AbstractParser):
                    parser_instances.append(instance)
                else:
                    print(f"Module {module_name} has invalid 'parser' object.")
                    print(f"Expected instance of AbstractParser subclass, got {type(instance)}")
            else:
                print(f"Module {module_name} does not define 'parser'")
                print(f"Please ensure it defines a 'parser' object that is an instance of AbstractParser subclass.")
        return parser_instances

    def _select_parser(self, data: bytes, parsers: list[AbstractParser]):
        selected_parser = None
        for parser in parsers:
            if parser.can_parse(data):
                if selected_parser is None:
                    selected_parser = parser
                else:
                    raise ValueError(f"Multiple parsers can parse the data: {selected_parser.get_name()} and {parser.get_name()}\n" \
                                      f"for data: {data.hex()}")
        if selected_parser is None:
            warnings.warn(f"No parser can handle the provided data.\nData: {data.hex()}")
        return selected_parser
