import inspect

def get_args(args, function):
    var_names = inspect.getargspec(function).args
    function_args = {k:args.pop(k, None) for k in var_names if k != 'self'}

    return function_args