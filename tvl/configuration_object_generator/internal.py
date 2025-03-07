import hashlib
import logging
import xml.etree.cElementTree as et
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, TypedDict

import jinja2

__version__ = "0.4"

TOOL = Path(__file__).parent
TEMPLATE_DIR = TOOL / "templates"

__logger = logging.getLogger(TOOL.stem.lower())


class InputField(TypedDict):
    lowidx: int
    width: int
    longtext: str


class InputRegister(TypedDict):
    baseaddr: int
    fields: Dict[str, InputField]


InputDict = Dict[str, InputRegister]


class Parser:
    @classmethod
    def parse_field(cls, node: et.Element) -> InputField:
        return {
            "lowidx": int(node.findtext("lowidx", "")),
            "width": int(node.findtext("width", "")),
            "longtext": node.findtext("longtext", ""),
        }

    @classmethod
    def parse_register(cls, node: et.Element) -> InputRegister:
        return {
            "baseaddr": int(node.findtext("baseaddr", ""), base=16),
            "fields": {
                child.findtext("shorttext", ""): cls.parse_field(child)
                for child in node.iter("field")
            },
        }

    @classmethod
    def parse(cls, root: et.Element) -> InputDict:
        return {
            child.findtext("shorttext", ""): cls.parse_register(child)
            for child in root.iter("reg")
        }


class ContextField(TypedDict):
    lowidx: int
    width: int
    description: str


class ContextRegister(TypedDict):
    baseaddr: int
    fields: Dict[str, ContextField]


ContextDict = Dict[str, ContextRegister]


class Converter:
    @classmethod
    def convert_field(cls, field: InputField) -> ContextField:
        return {
            "lowidx": field["lowidx"],
            "width": field["width"],
            "description": " ".join(map(str.strip, field["longtext"].split("\n"))),
        }

    @classmethod
    def convert_register(cls, reg: InputRegister) -> ContextRegister:
        return {
            "baseaddr": reg["baseaddr"],
            "fields": {
                key: cls.convert_field(value) for key, value in reg["fields"].items()
            },
        }

    @classmethod
    def convert(cls, root: InputDict) -> ContextDict:
        return {key: cls.convert_register(value) for key, value in root.items()}


class HeaderDict(TypedDict):
    date: datetime
    version: str
    hash: str


def compute_sha256(filepath: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as fd:
        for byte_block in iter(lambda: fd.read(4096), b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


def create_header(input_file: Path) -> HeaderDict:
    return {
        "date": datetime.now(),
        "version": __version__,
        "hash": compute_sha256(input_file),
    }


def create_context(input_file: Path) -> ContextDict:
    return Converter.convert(Parser.parse(et.parse(input_file).getroot()))


def render(template: Path, *, header: HeaderDict, context: ContextDict) -> str:
    environment = jinja2.Environment(
        trim_blocks=False,
        lstrip_blocks=True,
        loader=jinja2.FileSystemLoader(template.parent),
    )
    return environment.get_template(template.name).render(
        header=header, context=context
    )


def generate_configuration_object(
    input_file: Path, output_file: Path, template: Path, **_: Any
) -> None:
    __logger.debug("input_file = %s", input_file)
    __logger.debug("output_file = %s", output_file)
    __logger.debug("template_file = %s", template)

    __logger.info("Processing input file.")
    header = create_header(input_file)
    context = create_context(input_file)
    __logger.info("Input file processed.")

    __logger.info("Rendering template.")
    content = render(template, header=header, context=context)
    __logger.info("Template rendered.")

    __logger.info("Writing output file.")
    with open(output_file, "w") as fd:
        fd.write(content)
    __logger.info("Output file written.")
