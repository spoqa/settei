import importlib


def import_hook(module_path: str):
    parts = module_path.split(':', 1)
    if len(parts) == 1:
        module_name, func_name = module_path, "main"
    else:
        module_name, func_name = parts[0], parts[1]

    module = importlib.import_module(module_name)
    func = getattr(module, func_name)

    return func
