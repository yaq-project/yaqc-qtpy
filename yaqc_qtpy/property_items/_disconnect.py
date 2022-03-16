from functools import wraps


def disconnect(signals):
    def decorator(f):
        @wraps(f)
        def wrapper(value, item, *args, **kwargs):
            try:
                f(value, item, *args, **kwargs)
            except RuntimeError:
                for sig, func in signals[id(item)]:
                    try:
                        sig.disconnect(func)
                    except TypeError:
                        pass  # Already disconnected

        return wrapper

    return decorator
