# -*- coding=utf-8 -*-
from .classes import *
import inspect
import argparse as ap
import logging
import ast
import typing as t


logger = logging.getLogger(__package__)


def add_subparser(helper, command: Command, *, auto_type: bool) -> Command:
    r"""

    :param helper: argparse._SubParserAction
    :param command:
    :param auto_type:
    :return:
    """
    config = command.config
    if 'name' in config:
        command.name = config.get('name')
    helptext = config.get('help', inspect.getdoc(command.command)) or ""

    parser: ap.ArgumentParser = helper.add_parser(
        command.name,
        formatter_class=ap.RawDescriptionHelpFormatter,
        help=helptext.split('\n', 1)[0],  # short help in main-help
        description=helptext  # long help in command-help
    )

    sig: inspect.Signature = inspect.signature(command.command)  # analyze registered function

    for name, param in sig.parameters.items():
        if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
            flag = '{}'.format(name)
            config = {

            }
        elif param.kind == param.VAR_POSITIONAL:  # todo maybe needs to get removed [NOT TESTED]
            flag = '{}'.format(name)
            config = {
                'nargs': '*'
            }
        elif param.kind == param.KEYWORD_ONLY:
            flag = '--{}'.format(name)
            config = {
                'action': 'store'
            }
        else:
            raise NotImplementedError(param.kind)  # not supported

        if param.default is not param.empty:  # default parameter
            config['default'] = param.default
            config['nargs'] = '?'
        elif param.kind == param.KEYWORD_ONLY:
            config['required'] = True

        if param.annotation is not param.empty:
            config['type'] = get_type(param.annotation)
        elif auto_type:
            config['type'] = convert_auto_type  # todo maybe needs to get removed? (not sure)

        parser.add_argument(
            flag,
            **config
        )

    return command


def get_type(cls) -> t.Callable:
    if t.get_origin(cls) == t.Union:
        args = t.get_args(cls)
    else:
        args = (cls,)

    def shell(string: str):
        for arg in args:
            try:
                return arg(string)
            except Exception:
                pass
        raise TypeError('cannot parse {!r}'.format(string))

    return shell


def convert_auto_type(string: str) -> t.Any:
    try:
        return ast.literal_eval(string)
    except (SyntaxError, NameError, ValueError):
        return string
