import hashlib
import logging
import subprocess
import xml.etree.cElementTree as et
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, TypedDict

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
    bootloader_name: str
    bootloader_hash: str
    bootloader_commit: str
    application_name: str
    application_hash: str
    application_commit: str


def compute_sha256(filepath: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as fd:
        for byte_block in iter(lambda: fd.read(4096), b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


def _git_commit(filepath: Path) -> Optional[str]:
    """Return the short git commit hash that last touched *filepath*."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%h", "--", filepath.name],
            cwd=filepath.parent,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return None


def create_header(bootloader_input: Path, application_input: Path) -> HeaderDict:
    return {
        "date": datetime.now(),
        "version": __version__,
        "bootloader_name": bootloader_input.name,
        "bootloader_hash": compute_sha256(bootloader_input),
        "bootloader_commit": _git_commit(bootloader_input) or "unknown",
        "application_name": application_input.name,
        "application_hash": compute_sha256(application_input),
        "application_commit": _git_commit(application_input) or "unknown",
    }


def create_context(bootloader_input: Path, application_input: Path) -> ContextDict:
    bootloader = Parser.parse(et.parse(bootloader_input).getroot())
    application = Parser.parse(et.parse(application_input).getroot())

    overlaps = set(bootloader) & set(application)
    for name in overlaps:
        if bootloader[name] != application[name]:
            raise ValueError(
                f"Register '{name}' is defined in both bootloader and application "
                f"inputs with different content."
            )

    merged: InputDict = {**bootloader, **application}
    return Converter.convert(merged)


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
    bootloader_input: Path, application_input: Path, output_file: Path, template: Path, **_: Any
) -> None:
    __logger.debug("bootloader_input = %s", bootloader_input)
    __logger.debug("application_input = %s", application_input)
    __logger.debug("output_file = %s", output_file)
    __logger.debug("template_file = %s", template)

    __logger.info("Processing input files.")
    header = create_header(bootloader_input, application_input)
    context = create_context(bootloader_input, application_input)
    __logger.info("Input files processed.")

    __logger.info("Rendering template.")
    content = render(template, header=header, context=context)
    __logger.info("Template rendered.")

    __logger.info("Writing output file.")
    with open(output_file, "w") as fd:
        fd.write(content)
    __logger.info("Output file written.")
