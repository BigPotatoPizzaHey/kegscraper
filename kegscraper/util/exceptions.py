class UnclosedJSONError(Exception):
    """
    Raised when a JSON string is never closed.
    """
    pass

class NotFound(Exception):
    pass

class Unauthorised(Exception):
    pass

class ServerError(Exception):
    pass
