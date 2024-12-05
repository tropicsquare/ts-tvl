# Copyright 2023 TropicSquare
# SPDX-License-Identifier: Apache-2.0

import logging
import subprocess
from dataclasses import InitVar, dataclass, field
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from pprint import pformat
from shutil import get_terminal_size
from typing import Any, Callable, Dict, List, Mapping, NamedTuple, Optional, TypedDict

import jinja2
import yaml

from tvl.api_generator.grammar import InoutTypeEnum, InputFileModel

__version__ = "1.7"

TOOL = Path(__file__).parent
TEMPLATE_DIR = TOOL / "templates"

__logger = logging.getLogger(TOOL.stem.lower())


class APIGeneratorError(Exception):
    pass


class LogMapping:
    def __init__(self, __mapping: Mapping[Any, Any]) -> None:
        self.mapping = __mapping

    def __str__(self) -> str:
        return "\n" + pformat(self.mapping, width=get_terminal_size()[0])


def get_suffix(filename: Path) -> str:
    return "".join(filename.suffixes)


def generate_python_api(model: InputFileModel, _: Path) -> Dict[str, Any]:
    PYTHON_TYPES = {
        InoutTypeEnum.U8: ["U8Scalar", "U8Array"],
        InoutTypeEnum.U16: ["U16Scalar", "U16Array"],
        InoutTypeEnum.U32: ["U32Scalar", "U32Array"],
        InoutTypeEnum.U64: ["U64Scalar", "U64Array"],
    }

    def to_dict(lst: List[Any]) -> List[Dict[str, Any]]:
        return [x.dict() for x in lst]

    def format_descr(description: Optional[str]) -> str:
        if description is None:
            return ""
        return " ".join(x.strip() for x in description.split("\n")).strip()

    messages_context: List[Dict[str, Any]] = []
    enum_context: Dict[str, Any] = {"elements": []}
    api_context: Dict[str, Any] = {
        "functions": [],
    }

    for cfg in model.commands:
        tag = cfg.name.upper()
        function_cfg = cfg.function

        # Update enumeration
        enum_dct = {  # type: ignore
            "name": tag,
            "message_id": cfg.message_id,
            "description": cfg.description,
        }
        enum_context["elements"].append(enum_dct)

        function_name = tag.lower()

        # Update functions list
        function_dct = {
            "name": function_name,
            "description": format_descr(cfg.description_long),
        }
        api_context["functions"].append(function_dct)

        # Update messages list
        for io_type, io in (
            ("input", function_cfg.input),
            ("output", function_cfg.output),
        ):
            message_name = function_name.title().replace("_", "")

            function_dct[io_type] = message_name

            message_dct: Dict[str, Any] = {
                "name": message_name,
                "io_type": io_type,
                "tag": tag,
                "arguments": [],
                "result_choices": to_dict(
                    cfg.result.choices if cfg.result is not None else []
                ),
            }

            if io is None:
                continue

            for arg in io:
                arg_type = PYTHON_TYPES[arg.type]
                if (size_value := arg.size) is not None:
                    if size_value == 1:
                        size_dct = {"size": None}
                    else:
                        size_dct = {"size": size_value}
                    size = size_value
                else:
                    size_dct = {
                        "min_size": arg.min_size,
                        "max_size": (max_size_value := arg.max_size),
                    }
                    size = max_size_value
                _size = size if size != 1 else None

                message_dct["arguments"].append(
                    {
                        "name": arg.name.lower(),
                        "description": arg.description,
                        "description_long": format_descr(arg.description_long),
                        "dtype": arg_type[_size is not None],
                        "choices": to_dict(arg.choices)
                        if arg.choices is not None
                        else None,
                        **size_dct,
                    }
                )
            messages_context.append(message_dct)

    return {
        "defines": to_dict(model.defines),
        "enum_class": enum_context,
        "messages": messages_context,
        "api_class": api_context,
    }


def proc_python(filename: Path) -> None:
    subprocess.run(
        f"pycln --all {filename}; isort --profile black {filename}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )


def generate_c_api(model: InputFileModel, output_file: Path) -> Dict[str, Any]:
    def to_dict(lst: List[Any]) -> List[Dict[str, Any]]:
        return [x.dict() for x in lst]

    context: List[Dict[str, Any]] = []

    for cfg in model.commands:
        context_: Dict[str, Any] = {
            "name": cfg.name,
            "description": cfg.description,
            "description_long": cfg.description_long,
            "message_id": cfg.message_id,
            "structs": {"output": {}, "input": {}},
            "result_choices": to_dict(
                cfg.result.choices if cfg.result is not None else []
            ),
        }

        for io_type, io_cfg in (
            ("input", cfg.function.input),
            ("output", cfg.function.output),
        ):
            if io_cfg is None:
                continue
            context_["structs"][io_type] = {
                "name": f"{io_type}_t",
                "members": to_dict(io_cfg),
            }
            for arg in context_["structs"][io_type]["members"]:
                if (size := arg.get("size")) is None:
                    arg["size"] = arg.get("max_size")
                elif arg.get("max_size") is None:
                    arg["max_size"] = size
                    arg["min_size"] = size

        context.append(context_)

    return {
        "name": output_file.name,
        "defines": to_dict(model.defines),
        "tags": context,
    }


def generate_latex_api(model: InputFileModel, _: Path) -> Dict[str, Any]:
    C_TYPES_SIZE = {
        InoutTypeEnum.U8: 1,
        InoutTypeEnum.U16: 2,
        InoutTypeEnum.U32: 4,
        InoutTypeEnum.U64: 8,
    }

    def _size_to_bytes(field: Dict[str, Any]):
        if (size := field.get("size")) is None:
            size = 1
        return C_TYPES_SIZE[field["type"]] * size

    config = model.dict()

    for command in config["commands"]:
        command["function"]["name"] = command["name"].lower()
        for io in ("input", "output"):
            if io not in command["function"]:
                continue

            # Calculate overall command size
            min_size = 0
            max_size = 0
            size = 0
            for _io in command["function"][io]:
                io_size = _size_to_bytes(_io)

                if _io.get("min_size") is None:
                    _io["min_size"] = io_size
                if _io.get("max_size") is None:
                    _io["max_size"] = io_size

                min_size += _io["min_size"]
                max_size += _io["max_size"]
                size += io_size

                # Convert on-the fly field size
                _io["size"] = io_size

            # Fill summed command size
            command["function"][f"{io}_size"] = size
            command["function"][f"{io}_min_size"] = min_size
            command["function"][f"{io}_max_size"] = max_size

    return config


@dataclass(frozen=True)
class LanguageInfo:
    """
    Object that holds the different properties of a language
    """

    name: str
    extension: str
    comment_tag: str
    template: InitVar[str]
    generate_fn: Callable[[InputFileModel, Path], Dict[str, Any]]
    post_processing_fn: Callable[[Path], None] = lambda _: None
    default_template: Path = field(init=False)
    template_extension: str = field(init=False)

    def __post_init__(self, template: str) -> None:
        object.__setattr__(self, "default_template", TEMPLATE_DIR / template)
        object.__setattr__(self, "template_extension", f"{self.extension}.j2")


LANGUAGES = [
    LanguageInfo("C", ".h", "//", "api.h.j2", generate_c_api),
    LanguageInfo("Python", ".py", "#", "api.py.j2", generate_python_api, proc_python),
    LanguageInfo("Latex", ".tex", "%", "api.tex.j2", generate_latex_api),
]


class Params(NamedTuple):
    language_info: LanguageInfo
    output_file: Path
    template: Optional[Path] = None


class HeaderDict(TypedDict):
    date: datetime
    hash: str
    version: str


def prepare_header(input_file: Path) -> HeaderDict:
    def _compute_sha256(filepath: Path) -> str:
        hash_ = sha256()
        with open(filepath, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                hash_.update(block)
        return hash_.hexdigest()

    return {
        "version": __version__,
        "date": datetime.now(),
        "hash": _compute_sha256(input_file).upper(),
    }


def generate(header: HeaderDict, model: InputFileModel, params: Params) -> None:
    __logger.info("Generating %s API file.", params.language_info.name)

    if (template_file := params.template) is None:
        template_file = params.language_info.default_template
    else:
        __logger.info("Using custom template file %s.", template_file)

    api = params.language_info.generate_fn(model, params.output_file)
    __logger.debug("api = %s", LogMapping(api))

    if (key := "header") in api:
        raise APIGeneratorError(f"Unauthorized key: '{key}' is reserved.")

    template = jinja2.Environment(
        trim_blocks=False,
        lstrip_blocks=True,
        loader=jinja2.FileSystemLoader(template_file.parent),
        extensions=["jinja2.ext.do"],
    ).get_template(template_file.name)

    content = template.render(
        header={**header, "comment_tag": params.language_info.comment_tag},
        **api,
    )

    with open(params.output_file, "w") as fd:
        fd.write(content)

    params.language_info.post_processing_fn(params.output_file)

    __logger.info("%s generated.", params.output_file)


def open_api_description_file(filename: Path) -> InputFileModel:
    __logger.info("Opening file %s.", filename)
    with open(filename, "r") as fd:
        content = yaml.safe_load(fd)

    __logger.info("Checking API description.")
    input_model = InputFileModel.parse_obj(content)
    __logger.info("Configuration file is valid.")
    return input_model


def create_param_list(
    output_files: List[Path], templates: Optional[List[Path]] = None
) -> List[Params]:
    __logger.info("Map output files to language info")
    output_file_extensions = {info.extension: info for info in LANGUAGES}
    output_file_mapping = {
        file: output_file_extensions[get_suffix(file)] for file in output_files
    }
    __logger.debug("output_file_mapping = %s", LogMapping(output_file_mapping))

    if templates is None:
        template_mapping = {}
    else:
        __logger.info("Map language info to template")
        template_extensions = {info.template_extension: info for info in LANGUAGES}
        template_mapping = {
            template_extensions[get_suffix(file)]: file for file in templates
        }
    __logger.debug("template_mapping = %s", LogMapping(template_mapping))

    return [
        Params(
            language_info=language_info,
            output_file=output_file,
            template=template_mapping.get(language_info),
        )
        for output_file, language_info in output_file_mapping.items()
    ]


def generate_api_files(
    input_file: Path,
    output_files: List[Path],
    templates: Optional[List[Path]] = None,
    **_: Any,
) -> None:
    """Generate API files from an API description file

    Args:
        input_file (Path): path to the API description file
        output_files (List[Path]): paths to the API files to be generated
        templates: (List[Path], optional):
            templates to render the configuration with. Defaults to None.
    """
    api_model = open_api_description_file(input_file)

    if not (param_list := create_param_list(output_files, templates)):
        raise APIGeneratorError("Nothing to generate, check your inputs.")

    __logger.info("Generating header.")
    header = prepare_header(input_file)
    __logger.debug("header= %s", LogMapping(header))

    __logger.info("Generating API files.")
    for params in param_list:
        generate(header, api_model, params)
    __logger.info("API files generated.")
