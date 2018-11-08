class IncorrectParametersException(Exception):
    pass


class APIErrorException(Exception):
    pass


class ApiKeyError(Exception):
    """The Api key is missing"""
    pass
