import inspect
from types import ModuleType
from typing import Callable

def _import_module_by_name(name: str):
    name = f"modules.{name}"
    module = __import__(name)
    submodules = name.split('.')
    for sub in submodules[1:]:
        module = getattr(module, sub)
    return module

class Module:
    def __init__(self, name: str):
        self._name: str = name
        self._module: ModuleType = _import_module_by_name(name)
        self._info: str = self._module.__doc__
        self._run_func: Callable = self._module.run
        self._run_args: list[inspect.Parameter] = list(
            inspect.signature(self._run_func)
                .parameters
                .values()
            )
        self._set_args: dict[inspect.Parameter] = {}

    @property
    def name(self) -> str:
        return self._name
    
    def info(self) -> str:
        info_text: str = f"{self._name}\n"
        info_text += f"{self._info}\n"
        info_text += "Options:\n"
        for arg in self._run_args:
            info_text += f"{arg.name} ({arg.annotation.__name__}): "
            if arg in self._set_args:
                info_text += str(self._set_args[arg])
            elif arg.default != inspect.Parameter.empty:
                info_text += arg.default
            info_text += "\n"
        return info_text

    def run(self) -> bool:
        if any(filter(lambda arg: arg.default == inspect.Parameter.empty and arg not in self._set_args, self._run_args)):
            print("Error: One of more required options is not set.")
            return False
        args = tuple(self._set_args[arg] if arg in self._set_args else arg.default for arg in self._run_args)
        return self._run_func(*args)
    
    def set(self, arg_name: str, value):
        arg_fltr = list(filter(lambda a: a.name == arg_name, self._run_args))
        if len(arg_fltr) == 0:
            raise Exception(f"Argument {arg_name} does not exist.")
        arg: inspect.Parameter = arg_fltr[0]
        arg_type: type = arg.annotation
        try:
            value_casted = arg_type(value)
        except TypeError:
            raise Exception(f"Value {value} cannot be converted to type {arg_type.__name__}")
        self._set_args[arg] = value_casted
    
    def clear(self, arg_name: str):
        arg_fltr = list(filter(lambda a: a.name == arg_name, self._run_args))
        if len(arg_fltr) == 0:
            raise Exception(f"Argument {arg_name} does not exist.")
        arg: inspect.Parameter = arg_fltr[0]
        try:
            self._set_args.pop(arg)
        except KeyError:
            pass