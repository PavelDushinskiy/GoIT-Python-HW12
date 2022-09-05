import functools


def parser_handler(func):
    @functools.wraps(func)
    def wrapper(self, user_input: str):
        try:
            return func(self, user_input)
        except ValueError as e:
            return str(e)
        except KeyError as e:
            return str(e)

    return wrapper


def command_handler(func):
    @functools.wraps(func)
    def wrapper(*args):
        try:
            return func(*args)
        except ValueError as e:
            return str(e)
        except KeyError as e:
            return str(e)
        except Exception:
            raise SystemExit("Good bye!")

    return wrapper
