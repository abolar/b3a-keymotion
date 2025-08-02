DEBUG_FLAGS = {
    'v1': False,
    'v2': True,
    'v3': True,
    'keystroke': True,
    'arrows': True,
    'all': False  # master switch
}

def mprint(tag, *args, **kwargs):
    if DEBUG_FLAGS.get(tag, False) or DEBUG_FLAGS['all']:
        print(f"[{tag}]", *args, **kwargs)


from functools import wraps

indent_level = 0

debug_section_enabled = False

def debug_section(enabled=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global indent_level
            if enabled and debug_section_enabled:
                class_name = args[0].__class__.__name__ if args and hasattr(args[0], '__class__') else ''
                class_prefix = f"{class_name}." if class_name else ''
                print(f"{'  ' * indent_level}--> {func.__name__} of {class_prefix}")
                indent_level += 1
            result = func(*args, **kwargs)
            if enabled and debug_section_enabled:
                indent_level -= 1
                # print(f"{'  ' * indent_level}<-- Exiting {func.__name__}")
            return result
        return wrapper
    return decorator
