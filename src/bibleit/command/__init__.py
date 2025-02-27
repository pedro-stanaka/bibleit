import sys
import traceback
from importlib import import_module

from bibleit import config, normalize
from bibleit.command import core

_prefix = "bibleit.command"
_default_module = "core"


def eval_methods(module):
    return {
        name
        for name in dir(module)
        if not name.startswith("_")
        if name not in sys.builtin_module_names
    }


def eval_module(name):
    target = f"{_prefix}.{name}"

    try:
        if target not in sys.modules:
            return import_module(target)
        return sys.modules[target]
    except ModuleNotFoundError as e:
        if config.debug:
            print(e)
        return eval_module(_default_module)


def eval(ctx, *line, module=None):
    """Evaluate a function with arbitrary arguments."""
    if module is None:
        module = _default_module
    try:
        name, *args = line

        if name.startswith("!"):
            args.insert(0, name[1:])
            name = "set"

        ctx.module = eval_module(module)
        ctx.methods = eval_methods(ctx.module)

        args = list(filter(None, args))
        
        target = f"{'{} '.format(module) if module != _default_module else ''}{name}{' {}'.format(' '.join(args)) if args else ''}"
        if name in ctx.methods:
            fn = getattr(ctx.module, name)
            nargs = [normalize.normalize(arg) for arg in args]
            return fn(ctx, *nargs)
    except AssertionError as e:
        print(f"Error: {e}")
    except Exception as e:
        if config.debug:
            print(f"*** {e}\n")
            print(traceback.format_exc())
        if module != _default_module:
            core.help(ctx, *[module, *line])
        else:
            core.help(ctx, name)
    else:
        print(f"Error: command '{target}' not found")
